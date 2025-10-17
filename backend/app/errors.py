
class NotFoundError(Exception):
    pass

class DuplicateUserError(Exception):
    pass

class DatabaseError(Exception):
    pass

class AuthenticationError(Exception):
    pass

class UnauthorizedError(Exception):
    pass

class InvalidGPXError(Exception):
    pass

class InputError(Exception):
    pass