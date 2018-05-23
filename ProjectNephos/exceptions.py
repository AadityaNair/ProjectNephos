
class NephosException(Exception):
    pass


class OAuthFailure(NephosException):
    pass


class FileNotFound(NephosException):
    pass
