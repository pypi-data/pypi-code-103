from data_verifier.utils.utils import EncryptionTools,DecryptionTools

class AhrefsModel:

    def __init__(self):
        super(AhrefsModel).__init__()
        self.username=None
        self.domain=None
        self._password=None
        self._enc_pass=None

    @classmethod
    def applicant_to_object(cls,db_ob):
        applicant = cls()
        applicant.username=db_ob.username
        applicant.domain = db_ob.domain
        applicant._password=db_ob.password
        applicant._enc_pass=None
        return applicant

    @property
    def enc_pass(self):
        return self._password

    @enc_pass.setter
    def enc_pass(self,value):
        raise BaseException("Method not allowed")

    @property
    def password(self):
        return DecryptionTools(self._password,True).decrypt().decode()

    @password.setter
    def password(self,value):
        try:
            e=EncryptionTools(value,True)
            self._password=e.encrypt().decode()
        except ValueError:
            raise ValueError("Required Integer, provided {}".format(value))