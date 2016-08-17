from rest_framework.authentication import BasicAuthentication

__author__ = 'pivstone'


class TOTPAuthentication(BasicAuthentication):
    def authenticate_credentials(self, userid, password):
        pass



