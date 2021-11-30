from django.contrib.auth import get_user_model
from django.contrib.auth.backends import BaseBackend
from django.core.exceptions import ObjectDoesNotExist


class GoogleAuthBackend(BaseBackend):
    model = get_user_model()

    def authenticate(self, request, uid=None):
        if not uid:
            return None

        try:
            user = self.model.objects.get(uid=uid)
            return user
        except ObjectDoesNotExist:
            return None
        except Exception as e:
            print(str(e))
            return None

    def get_user(self, _id):
        try:
            return self.model.objects.get(pk=_id)
        except ObjectDoesNotExist:
            return None
        except Exception as e:
            print(str(e))
            return None
