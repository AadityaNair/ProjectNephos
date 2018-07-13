class NephosException(Exception):
    pass


class AuthFailure(NephosException):
    pass


class FileNotFound(NephosException):
    pass


class SubCommandNotFound(NephosException):
    pass
