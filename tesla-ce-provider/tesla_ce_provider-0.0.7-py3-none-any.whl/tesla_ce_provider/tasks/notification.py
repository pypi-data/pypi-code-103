#  Copyright (c) 2020 Xavier Baró
#
#      This program is free software: you can redistribute it and/or modify
#      it under the terms of the GNU Affero General Public License as
#      published by the Free Software Foundation, either version 3 of the
#      License, or (at your option) any later version.
#
#      This program is distributed in the hope that it will be useful,
#      but WITHOUT ANY WARRANTY; without even the implied warranty of
#      MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#      GNU Affero General Public License for more details.
#
#      You should have received a copy of the GNU Affero General Public License
#      along with this program.  If not, see <https://www.gnu.org/licenses/>.
""" TeSLA CE Notification tasks module """
from tesla_ce_client.exception import ObjectNotFoundException
from celery.exceptions import Reject
from .base import BaseTask
from ..celery_app import app


class NotificationTask(BaseTask):
    """ Notification Task for TeSLA Providers """
    name = 'tesla_ce.tasks.notification.providers.provider_notify'

    def run(self, notification_id):
        """
            Start a notification response

            :param notification_id: Notification ID
            :type notification_id: int
        """
        # Store the context
        self._unlock_on_failure = False
        self._learner = None

        # Get notification
        try:
            notification = self.get_notification_data(notification_id)
        except ObjectNotFoundException:
            raise Reject('Notification not available.')

        # Perform notification process
        try:
            self.provider.on_notification(notification['key'], notification['info'])
        except Exception as exc:
            raise Reject('Exception from provider: ' + exc.__str__())

        # Remove this notification
        self.delete_notification(notification_id)

        # Send delayed results
        self.send_delayed_results()

        # Add notifications
        self.send_notifications()

NotificationTask = app.register_task(NotificationTask())
