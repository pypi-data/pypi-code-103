from .mixins.jsonable import JsonMixin


class BaseUser(JsonMixin):
    def __init__(self, fname=None, lname=None, username=None, email=None, dept=None):
        super().__init__()
        self.firstname = fname
        self.lastname = lname
        self.username = username
        self.email = email
        self.department = dept

    def __repr__(self):
        return f"{self.__class__.__name__}\
(fname='{self.firstname}', lname='{self.lastname}',\
email='{self.email}')<username: {self.username}, dept: {self.department}>"

    def __eq__(self, o):
        return (
            self.firstname == o.firstname
            and self.lastname == o.lastname
            and self.email == o.email
            and self.department == o.department
        )

    def __ne__(self, o):
        return not self == o

    def __hash__(self):
        return hash((self.firstname, self.lastname, self.email))

    @property
    def fullname(self):
        """Returns fullname of the User by concatenating first_name and the
        last_name.
        """
        return f"{self.firstname} {self.lastname}"

    def validate(self):
        """Validates whether the specified user is registered with the specified
        department.
        """
        raise NotImplementedError()

    def authenticate(self):
        raise NotImplementedError()
