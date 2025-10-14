
class UserNotFoundError(Exception):
    pass

class DuplicateUserError(Exception):
    pass

class DatabaseError(Exception):
    pass

class AuthenticationError(Exception):
    pass