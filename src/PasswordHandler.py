
from argon2 import PasswordHasher

# a class to handle password hashing and salting of passwords
# it makes use of the argon2 hashing algorithm which inherently salts passwords
class PasswordHandler:
    def __init__(self):
        self.hasher = PasswordHasher()

    # Hash a password
    def hash_password(self, password):
        hashed_password = self.hasher.hash(password)
        return hashed_password
    
    # Verify a password
    def verify_password(self, password, hashed_password):
        try:
            self.hasher.verify(hashed_password, password)
            return True
        except:
            return False
