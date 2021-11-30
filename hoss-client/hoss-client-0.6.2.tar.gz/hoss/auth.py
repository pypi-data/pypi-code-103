from typing import Optional, List
import os
import time
from dataclasses import dataclass
from enum import Enum

import requests
import jwt

from hoss.error import *


class Role(Enum):
    """Enum for user roles"""
    USER = 0
    PRIVILEGED = 1
    ADMIN = 2


@dataclass
class User:
    """Class for representing users"""
    username: str
    email: str
    role: Role


@dataclass
class Group:
    """Class for representing groups"""
    name: str
    description: str
    members: Optional[List[User]]


class AuthService(object):
    """A class to represent a Hoss server's Auth Service"""
    def __init__(self, auth_service_endpoint: str) -> None:
        """Constructor

        Args:
            auth_service_endpoint: Endpoint to the desired auth service (e.g. http://localhost/auth/v1)
        """
        self.endpoint = auth_service_endpoint
        self.pat = os.environ.get("HOSS_PAT")
        self.jwt: Optional[str] = None
        self.jwt_exp_seconds: Optional[int] = None
        self.jwt_refresh_at: Optional[int] = None

        # Get a JWT on load. Also useful because it quickly verifies server access
        self._get_jwt()

    def _get_jwt(self) -> None:
        """Method to exchange a PAT for a JWT or alternatively load it directly from an env var `HOSS_JWT`

        Returns:
            None
        """
        # Set jwt property
        if self.pat is None:
            self.jwt = os.environ.get("HOSS_JWT")
            if self.jwt is None:
                raise HossException("env var 'HOSS_PAT' or 'HOSS_JWT' must be set to authenticate with a server.")
        else:
            headers = {"Authorization": f"Bearer {self.pat}"}
            try:
                resp = requests.request("POST", f"{self.endpoint}/pat/exchange/jwt", headers=headers)
            except requests.exceptions.ConnectionError:
                raise HossException(f"Cannot reach Hoss auth service for server '{self.endpoint}'. "
                                    f"Verify your network connection and try again.")

            if not resp.ok:
                print(f"{resp.status_code} {resp.reason}: {resp.text}")
                raise HossException("Could not retrieve JWT using PAT: " + resp.text)

            self.jwt = resp.json()["id_token"]

        if not self.jwt:
            raise HossException("Failed to load JWT")

        claims = jwt.decode(self.jwt,
                            options={"verify_signature": False},
                            audience="hoss",
                            issuer="hoss auth")
        self.jwt_exp_seconds = claims["exp"] - claims["iat"]
        self.jwt_refresh_at = claims["iat"] + self.jwt_exp_seconds / 2
        if self._has_jwt_expired():
            raise Exception("HOSS_JWT has expired")

    def _has_jwt_expired(self) -> bool:
        """Check if the JWT currently set in this instance has expired, using 3 hour buffer to allow up to 3 hours
        expiration for temporary STS credentials

        Returns:
            bool
        """
        return time.time() > self.jwt_refresh_at

    def headers(self) -> dict:
        """Method to populate a dict with request headers, primarily setting the Authorization header

        Returns:
            request headers
        """
        if self._has_jwt_expired():
            self._get_jwt()

        return {"Authorization": f"Bearer {self.jwt}"}

    # groups API
    def get_user(self, user_name):
        resp = requests.request("GET", f"{self.endpoint}/user/{user_name}", headers=self.headers())
        if not resp.ok:
            if "not found" in resp.text:
                raise NotFoundException()

            print(f"{resp.status_code} {resp.reason}: {resp.text}")
            raise HossException("Could not get user info: " + resp.text)

        data = resp.json()
        return User(data['username'],
                    data['email'],
                    Role[data['role'].upper()])

    @staticmethod
    def _parse_memberships(memberships: list) -> List[User]:
        if memberships:
            return [User(m['user']['username'],
                         m['user']['email'],
                         Role[m['user']['role'].upper()]) for m in memberships]
        else:
            return list()

    def get_group(self, group_name):
        resp = requests.request("GET", f"{self.endpoint}/group/{group_name}", headers=self.headers())
        if not resp.ok:
            if "not found" in resp.text:
                raise NotFoundException()

            print(f"{resp.status_code} {resp.reason}: {resp.text}")
            raise HossException("Could not get group info: " + resp.text)
        data = resp.json()
        return Group(data['group_name'], data['description'],
                     members=self._parse_memberships(data.get('memberships')))

    def create_group(self, group_name, description="No description provided"):
        data = {"name": group_name, "description": description}
        resp = requests.request("POST", f"{self.endpoint}/group", json=data, headers=self.headers())
        if not resp.ok:
            if "already exists" in resp.text:
                raise AlreadyExistsException()

            print(f"{resp.status_code} {resp.reason}: {resp.text}")
            raise HossException("Could not create group: " + resp.text)

        return self.get_group(group_name)

    def delete_group(self, group_name):
        resp = requests.request("DELETE", f"{self.endpoint}/group/{group_name}", headers=self.headers())
        if not resp.ok:
            print(f"{resp.status_code} {resp.reason}: {resp.text}")
            raise HossException("Could not delete group: " + resp.text)

    def add_user_to_group(self, group_name, username) -> None:
        resp = requests.request("PUT", f"{self.endpoint}/group/{group_name}/user/{username}",
                                headers=self.headers())
        if not resp.ok:
            print(f"{resp.status_code} {resp.reason}: {resp.text}")
            raise HossException("Could not add user to group: " + resp.text)

    def remove_user_from_group(self, group_name, username) -> None:
        resp = requests.request("DELETE", f"{self.endpoint}/group/{group_name}/user/{username}", headers=self.headers())
        if not resp.ok:
            print(f"{resp.status_code} {resp.reason}: {resp.text}")
            raise HossException("Could not remove user from group: " + resp.text)
