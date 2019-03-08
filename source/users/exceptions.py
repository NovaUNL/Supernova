class InvalidToken(Exception):
    def __init__(self, deleted=False):
        super().__init__()
        self.deleted = deleted  # Whether the token has been deleted


class UnknownStudent(Exception):
    def __init__(self, message, multiple=False):
        super().__init__(message)
        self.multiple = multiple


class AccountExists(Exception):
    def __init__(self, message):
        super().__init__(message)


class DuplicatedUsername(Exception):
    def __init__(self, message):
        super().__init__(message)


class InvalidUsername(Exception):
    def __init__(self, message):
        super().__init__(message)


class ExpiredRegistration(Exception):
    def __init__(self, message):
        super().__init__(message)


class AssignedStudent(Exception):
    def __init__(self, message):
        super().__init__(message)
