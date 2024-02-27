class MissingResourceAccess(Exception):
    def __init__(self, message):
        super().__init__(message)

class UserNotFound(Exception):
    def __init__(self, message):
        super().__init__(message)

class InvalidLogin(Exception):
    def __init__(self, message):
        super().__init__(message)

class InvalidRegistration(Exception):
    def __init__(self, message):
        super().__init__(message)
        
class IPAddressChange(Exception)
    def __init__(self, message):
        super().__init__(message)
