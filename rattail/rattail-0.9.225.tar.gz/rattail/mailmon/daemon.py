# -*- coding: utf-8; -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2021 Lance Edgar
#
#  This file is part of Rattail.
#
#  Rattail is free software: you can redistribute it and/or modify it under the
#  terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  Rattail is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
#  details.
#
#  You should have received a copy of the GNU General Public License along with
#  Rattail.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
"""
Mail Monitor Daemon
"""

from __future__ import unicode_literals, absolute_import

import re
import time
import imaplib
from six.moves import queue
# import sys
import logging
# from traceback import format_exception

import six

from rattail.daemon import Daemon
from rattail.db import api
from rattail.mailmon.config import load_mailmon_profiles
from rattail.mailmon.util import (get_lastrun,
                                  get_lastrun_setting,
                                  get_lastrun_timefmt)
from rattail.threads import Thread
from rattail.time import make_utc
from rattail.exceptions import StopProcessing
# from rattail.mail import send_email


log = logging.getLogger(__name__)


class MailMonitorDaemon(Daemon):
    """
    Daemon responsible for checking IMAP folders and detecting email
    messages, and then invoking actions upon them.
    """

    def run(self):
        """
        Starts watcher and worker threads according to configuration.
        """
        monitored = load_mailmon_profiles(self.config)
        for key, profile in six.iteritems(monitored):

            # create a msg queue for the profile
            profile.queue = queue.Queue()

            # create a watcher thread for the IMAP folder
            watcher = IMAPWatcher(profile, key)
            name = 'watcher_{}'.format(key)
            log.info("starting IMAP watcher thread: %s", name)
            thread = Thread(target=watcher, name=name)
            thread.daemon = True
            thread.start()

            # create an action thread for the profile
            name = 'actions-{}'.format(key)
            log.debug("starting action thread: %s", name)
            thread = Thread(target=perform_actions, name=name, 
                            args=(self.config, watcher))
            thread.daemon = True
            thread.start()

        # loop indefinitely.  since this is the main thread, the app
        # will terminate when this method ends; all other threads are
        # "subservient" to this one.
        while True:
            time.sleep(.01)


class IMAPWatcher(object):
    """
    Abstraction to make watching an IMAP folder a little more
    organized.  Instances of this class are used as callable targets
    when the daemon starts watcher threads.  They are responsible for
    polling the IMAP folder and processing any messages found there.
    """
    uid_pattern = re.compile(r'^\d+ \(UID (?P<uid>\d+)')

    def __init__(self, profile, key):
        self.profile = profile
        self.config = profile.config
        self.key = key
        self.server = None

        # we need these for writing lastrun times
        self.lastrun_setting = get_lastrun_setting(self.config, self.key)
        self.lastrun_timefmt = get_lastrun_timefmt(self.config)

    def get_uid(self, response):
        match = self.uid_pattern.match(response)
        if match:
            return match.group('uid')

    def __call__(self):
        """
        This is the main loop for the watcher.  It acts as the
        callable target for the thread in which it runs.  It basically
        checks for new messages, queueing any found, then waits for a
        spell, then does it again, forever.
        """
        # the 'lastrun' value is maintained as zone-aware UTC
        lastrun = get_lastrun(self.config, self.key)

        recycled = None
        while True:
            thisrun = make_utc(tzinfo=True)

            if self.server is None:
                self.server = imaplib.IMAP4_SSL(self.profile.imap_server)
                try:
                    result = self.server.login(self.profile.imap_username, self.profile.imap_password)
                except self.server.error:
                    log.exception("failed to login to server!")
                    return

                log.debug("IMAP server login result: %s", result)
                recycled = make_utc()

                result = self.server.select(self.profile.imap_folder)
                log.debug("IMAP server select result: %s", result)

            try:
                self.queue_messages()
            except:
                log.exception("failed to queue messages!")
                if self.profile.stop_on_error:
                    break
            else:
                # successful, so record lastrun time
                lastrun = thisrun
                api.save_setting(None, self.lastrun_setting,
                                 lastrun.strftime(self.lastrun_timefmt))

            # if recycle time limit has been reached, close the IMAP
            # connection; it will be re-established in next loop run
            if self.profile.imap_recycle:
                if (make_utc() - recycled).seconds >= self.profile.imap_recycle:
                    log.debug("recycle time limit reached, disposing of current connection")
                    self.server.close()
                    self.server.logout()
                    self.server = None

            # wait a tick before doing it all again
            time.sleep(self.profile.imap_delay)

        self.server.close()
        self.server.logout()

    def queue_messages(self):
        """
        Check for new messages in the folder, and queue any found, for
        action processing thread.
        """
        # maybe look for "all" or maybe just "unread"
        if self.profile.imap_unread_only:
            criterion = '(UNSEEN)'
        else:
            criterion = 'ALL'

        # log.debug("invoking IMAP4.search()")
        code, items = self.server.uid('search', None, criterion)
        if code != 'OK':
            raise RuntimeError("IMAP4.search() returned bad code: {}".format(code))

        # config may dictacte a "max batch size" in which case we will
        # only queue so many messages at a time
        uids = items[0].split()
        if self.profile.max_batch_size:
            if len(uids) > self.profile.max_batch_size:
                uids = uids[:self.profile.max_batch_size]

        # add message uids to the queue
        for uid in uids:
            self.profile.queue.put(uid)


def perform_actions(config, watcher):
    """
    Target for action threads.  Provides the main loop which checks
    the queue for new messages and invokes actions for each, as they
    appear.
    """
    profile = watcher.profile
    stop = False
    while not stop:

        # suspend execution briefly, to avoid consuming so much CPU...
        time.sleep(0.01)

        try:
            msguid = profile.queue.get_nowait()
        except queue.Empty:
            pass
        except StopProcessing:
            stop = True
        else:
            log.debug("queue contained a msguid: %s", msguid)
            for action in profile.actions:
                try:
                    invoke_action(config, watcher, action, msguid)

                except:
                    # stop processing messages altogether for this
                    # profile if it is so configured
                    if profile.stop_on_error:
                        log.warning("an error was encountered, and config "
                                    "dictates that no more actions should be "
                                    "processed for profile: %s", profile.key)
                        stop = True

                    # either way no more actions should be invoked for
                    # this particular message
                    break


def invoke_action(config, watcher, action, msguid):
    """
    Invoke a single action on a mail message, retrying as necessary.
    """
    attempts = 0
    errtype = None
    while True:
        attempts += 1
        log.debug("invoking action '%s' (attempt #%s of %s) on file: %s",
                  action.spec, attempts, action.retry_attempts, msguid)

        try:
            action.action(watcher.server, msguid, *action.args, **action.kwargs)

        except:

            # if we've reached our final attempt, stop retrying
            if attempts >= action.retry_attempts:
                # log.debug("attempt #%s failed for action '%s' (giving up) on "
                #           "msguid: %s", attempts, action.spec, msguid,
                #           exc_info=True)
                log.exception("attempt #%s failed for action '%s' (giving up) on "
                          "msguid: %s", attempts, action.spec, msguid)
                # TODO: add email support
                # exc_type, exc, traceback = sys.exc_info()
                # send_email(config, 'mailmon_action_error', {
                #     # 'hostname': socket.gethostname(),
                #     # 'path': path,
                #     'msguid': msguid,
                #     'action': action,
                #     'attempts': attempts,
                #     'error': exc,
                #     'traceback': ''.join(format_exception(exc_type, exc, traceback)).strip(),
                # })
                raise

            # if this exception is not the first, and is of a
            # different type than seen previously, do *not* continue
            # to retry
            if errtype is not None and not isinstance(error, errtype):
                log.exception("new exception differs from previous one(s), "
                              "giving up on action '%s' for msguid: %s",
                              action.spec, msguid)
                raise

            # record the type of exception seen, and pause for next retry
            log.warning("attempt #%s failed for action '%s' on msguid: %s",
                        attempts, action.spec, msguid, exc_info=True)
            errtype = type(error)
            log.debug("pausing for %s seconds before making attempt #%s of %s",
                      action.retry_delay, attempts + 1, action.retry_attempts)
            if action.retry_delay:
                time.sleep(action.retry_delay)

        else:
            # no error, invocation successful
            log.debug("attempt #%s succeeded for action '%s' on msguid: %s",
                      attempts, action.spec, msguid)
            break
