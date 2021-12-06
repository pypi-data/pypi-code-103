# -*- coding: utf-8 -*-

import functools

from fabric2 import Connection
from fabric2.config import Config
from fabric2.runners import Remote

from .exceptions import InvalidMinkeSetup
from .models import CommandResult


class FabricConfig(Config):
    """
    A subclass of fabric's Config-class.
    Add a load_snakeconfig-method, that takes a plain dict and parses its
    snake-case-keys to fit into the nested default-config-structure.
    """
    def __init__(self, *args, **kwargs):
        # NOTE:
        # fabric has a rather dodgy way to check for optional config-files:
        #
        # > # Typically means 'no such file', so just note & skip past.
        # > except IOError as e:
        # >     # TODO: is there a better / x-platform way to detect this?
        # >     if "No such file" in e.strerror:
        # >         err = "Didn't see any {}, skipping."
        # >         debug(err.format(filepath))
        # >     else:
        # >         raise
        #
        # To prevent an accidentally raised IOError we catch it and re-try to
        # initialize Config with `lazy=True` (which means `Config` won't look for
        # config-files at all).
        # FIXME: Initialization fails when building the docs cause sphinx seems
        # to somehow localize the error-message. Find a way to not let sphinx do
        # that, and remove the __init__-hacking.
        try:
            super().__init__(*args, **kwargs)
        except IOError:
            kwargs['lazy'] = True
            super().__init__(*args, **kwargs)

    def load_snakeconfig(self, configdict):
        """
        Load a plane configdict as nested config - using the key's
        snake-structure as representation of the nest-logic.

        Two level of recursion are supported. That means something like
        'connect_kwargs_my_special_key' will be applied as
        'config.connect_kwargs.my_special_key'. To obviate ambiguity the key on
        the first level must already exist. Otherwise we raise InvalidMinkeSetup.

        Parameter
        ---------
        configdict : dict
        """
        for param, value in configdict.items():
            snippets = param.split('_')
            key1 = key2 = None

            for i, key in enumerate(snippets):
                if '_'.join(snippets[:i+1]) in self:
                    key1 = '_'.join(snippets[:i+1])
                    key2 = '_'.join(snippets[i+1:])
                    break

            if not key1:
                msg = 'Invalid fabric-config-parameter: {}'.format(param)
                raise InvalidMinkeSetup(msg)

            # apply config-data
            if not key2:
                self[key1] = value
            else:
                if not self[key1]:
                    # FIXME: normal dict does not support the attr-api.
                    self[key1] = dict()
                self[key1][key2] = value


class FabricRemote(Remote):
    """
    A subclass of fabric's remote-runner to customize the result-class.
    """
    def generate_result(self, **kwargs):
        kwargs["connection"] = self.context
        return CommandResult(**kwargs)


def protect(method):
    """
    Decorator for session-methods to defer their interrupt.
    """
    @functools.wraps(method)
    def wrapper(obj, *args, **kwargs):
        # are we already protected?
        if obj._busy:
            return method(obj, *args, **kwargs)
        # otherwise protect the method-call by setting the busy-flag
        obj._busy = True
        result = method(obj, *args, **kwargs)
        # if interruption was deferred now is the time to raise it
        if obj._stopped:
            raise KeyboardInterrupt
        obj._busy = False
        return result

    return wrapper


class FabricConnection(Connection):
    """
    Extend fabric's Connection by the minkeobj and the db-session and some
    helper-methods.
    """
    def __init__(self, *args, **kwargs):
        self._db = kwargs.pop('db')
        self._minkeobj = kwargs.pop('minkeobj', None)
        self._stopped = False
        self._busy = False
        super().__init__(self, *args, **kwargs)

    @property
    def minkeobj(self):
        """
        Refers to :attr:`.models.MinkeSession.minkeobj`.
        """
        return self._minkeobj or self._db.minkeobj

    @property
    def status(self):
        """
        Refers to :attr:`.models.MinkeSession.session_status`.
        """
        return self._db.session_status

    def add_msg(self, msg, level=None):
        """
        Add a message.

        Parameters
        ----------
        msg
            You could either pass an instance of any :mod:`message-class<.messages>`,
            or any type the different message-classes are initiated with:
            * a string for a :class:`~messages.PreMessage`
            * a tuple or list for a :class:`~messages.TableMessage`
            * an object of :class:`~fabric.runners.Result` for a
              :class:`~messages.ExecutionMessage`
        level : string or bool (optional)
            This could be one of 'info', 'warning' or 'error'. If you pass a
            bool True will be 'info' and False will be 'error'.
        """
        if isinstance(msg, str):
            msg = PreMessage(msg, level)
        elif isinstance(msg, tuple) or isinstance(msg, list):
            msg = TableMessage(msg, level)
        elif isinstance(msg, Result):
            msg = ExecutionMessage(msg, level)
        elif isinstance(msg, BaseMessage):
            pass
        self._db.messages.add(msg, bulk=False)

    def set_status(self, status, update=True):
        """
        Set session-status. Pass a valid session-status or a bool.

        Parameters
        ----------
        status : string or bool
            Valid :attr:`status <models.MinkeSession.SESSION_STATES>` as string
            or True for 'success' and False for 'error'.
        update : bool (optional)
            If True the session-status could only be raised. Lower values as
            current will be ignored.
        """
        states = dict(self._db.SESSION_STATES)
        if type(status) == bool:
            status = 'success' if status else 'error'
        elif status.lower() in states.keys():
            status = status.lower()
        else:
            msg = 'session-status must be one of {}'.format(states.keys())
            raise InvalidMinkeSetup(msg)

        if not self.status or not update or states[self.status] < states[status]:
            self._db.session_status = status

    def format_cmd(self, cmd):
        """
        Use the :attr:`.data` and the fields of the :attr:`.minkeobj` as
        parameters for :func:`format` to prepare the given command.

        Parameters
        ----------
        cmd : string
            a format-string

        Returns
        -------
        string
            The formatted command.
        """
        cmd = cmd.format_map(FormatDict(self.data))
        cmd = cmd.format_map(FormatDict(vars(self.minkeobj)))
        return cmd

    @protect
    def run(self, cmd, **invoke_params):
        """
        Run a command.

        Basically call :meth:`~fabric.connection.Connection.run` on the
        :class:`~fabric.connection.Connection`-object with the given command
        and invoke-parameters.

        Additionally save the :class:`~invoke.runners.Result`-object as an
        :class:`.models.CommandResult`-object.

        Parameters
        ----------
        cmd : string
            The shell-command to be run.
        **invoke_params (optional)
            Parameters that will be passed to
            :meth:`~fabric.connection.Connection.run`

        Returns
        -------
        object of :class:`.models.CommandResult`
        """
        result = super().run(cmd, **invoke_params)
        self._db.commands.add(result, bulk=False)
        return result

    @protect
    def frun(self, cmd, **invoke_params):
        """
        Same as :meth:`.run`, but use :meth:`~.format_cmd` to prepare the
        command-string.
        """
        return self.run(self.format_cmd(cmd), **invoke_params)

    @protect
    def xrun(self, cmd, **invoke_params):
        """
        Same as :meth:`.frun`, but also add a
        :class:`~.messages.ExecutionMessage` and update the session-status.
        """
        result = self.frun(cmd, **invoke_params)
        self.add_msg(result)
        self.set_status(result.status)
        return result

    @protect
    def update_field(self, field, cmd, regex=None, **invoke_params):
        """
        Running a command and update a field of :attr:`~.minkeobj`.

        Assign either result.stdout or if available the first matched
        regex-group. If result.failed is True or result.stdout is empty
        or the given regex does not match, the field is updated with None.
        In this case an error-message will be added.

        Parameters
        ----------
        field : string
            Name of the field that should be updated.
        cmd : string
            The shell-command to be run.
        regex: string (optional)
            A regex-pattern the :class:`.CommandResult` will be initialized with.
        **invoke_params (optional)
            Parameters that will be passed to
            :meth:`~fabric.connection.Connection.run`

        Returns
        -------
        bool
            False if the field was updated with None. True otherwise.

        Raises
        ------
        AttributeError
            If the given field does not exists on :attr:`.minkeobj`.
        """
        # is field a minkeobj-attribute?
        try:
            getattr(self.minkeobj, field)
        except AttributeError as e:
            raise e

        result = self.frun(cmd, **invoke_params)

        if regex and result.validate(regex):
            try:
                value = result.match.group(1)
            except IndexError:
                value = result.stdout
        elif not regex and result.ok and result.stdout:
            value = result.stdout
        else:
            self.add_msg(result, 'error')
            self.set_status('warning')
            value = None

        setattr(self.minkeobj, field, value)
        return bool(value)
