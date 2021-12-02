import time

from .. import CoreService_pb2 as pb
from ..collections.feature_sets import FeatureSets
from ..utils import Utils
from .user import User


class Project:
    def __init__(self, stub, project):
        self._project = project
        self._stub = stub
        self.feature_sets = FeatureSets(stub, project)

    @property
    def name(self):
        return self._project.name

    @property
    def description(self):
        return self._project.description

    @property
    def secret(self):
        return self._project.secret

    @secret.setter
    def secret(self, value):
        self._project.secret = value

    @property
    def locked(self):
        return self._project.locked

    @locked.setter
    def locked(self, value):
        self._project.locked = value

    @property
    def owner(self):
        return User(self._project.owner)

    @owner.setter
    def owner(self, email):
        request = pb.GetUserByMailRequest()
        request.email = email
        response = self._stub.GetUserByMail(request)
        user = response.user
        self._project.owner.id = user.id
        self._project.owner.name = user.name
        self._project.owner.email = user.email

    @property
    def author(self):
        return User(self._project.author)

    def update_metadata(self):
        request = pb.UpdateProjectMetadataRequest()
        request.project.CopyFrom(self._project)
        self._project = self._stub.UpdateProjectMetadata(request).project

    def delete(self, wait_for_completion=False):
        request = pb.DeleteProjectRequest()
        request.project.CopyFrom(self._project)
        self._stub.DeleteProject(request)
        exists_request = pb.ProjectExistsRequest()
        exists_request.project_id = self._project.id
        if wait_for_completion:
            while self._stub.ProjectExists(exists_request).exists:
                time.sleep(1)
                print("Waiting for project '{}' deletion".format(self._project.name))

    def add_owners(self, user_emails):
        return self._add_permissions(user_emails, pb.PermissionType.Owner)

    def add_editors(self, user_emails):
        return self._add_permissions(user_emails, pb.PermissionType.Editor)

    def add_consumers(self, user_emails):
        return self._add_permissions(user_emails, pb.PermissionType.Consumer)

    def remove_owners(self, user_emails):
        return self._remove_permissions(user_emails, pb.PermissionType.Owner)

    def remove_editors(self, user_emails):
        return self._remove_permissions(user_emails, pb.PermissionType.Editor)

    def remove_consumers(self, user_emails):
        return self._remove_permissions(user_emails, pb.PermissionType.Consumer)

    def _add_permissions(self, user_emails, permission):
        request = pb.ProjectPermissionRequest()
        request.project.CopyFrom(self._project)
        request.user_emails.extend(user_emails)
        request.permission = permission
        self._stub.AddProjectPermission(request)
        return self

    def _remove_permissions(self, user_emails, permission):
        request = pb.ProjectPermissionRequest()
        request.project.CopyFrom(self._project)
        request.user_emails.extend(user_emails)
        request.permission = permission
        self._stub.RemoveProjectPermission(request)
        return self

    def __repr__(self):
        return Utils.pretty_print_proto(self._project)
