"""
Abstract Base Class definition for managing the getting and setting of secrets from flat files, OS vaults, password managers
"""

from abc import ABC, abstractmethod, abstractstaticmethod

class CredContainerBase(ABC):
    """
    This is the abstract base class that other Credential Containers should override
    """

    @abstractmethod
    def get_cred(self):
        """
        Gets a credential
        This is an abstract method that should be overridden by subclasses.
        """

        raise NotImplementedError(f"A get_cred method has not been implemented for the subclass of BaseCredContainer {type(self)}")

    @abstractstaticmethod
    def set_cred(self):
        """
        Sets a credential (create or update)
        This is an abstract method that should be overridden by subclasses.
        """

        raise NotImplementedError(f"A set_cred method has not been implemented for the subclass of BaseCredContainer {type(self)}")
        

    @abstractstaticmethod
    def delete_cred(self):
        """
        Deletes a credential
        This is an abstract method that should be overridden by subclasses.
        """

        raise NotImplementedError(f"A delete_cred method has not been implemented for the subclass of BaseCredContainer {type(self)}")