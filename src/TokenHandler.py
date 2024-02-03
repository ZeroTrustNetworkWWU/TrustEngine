# a class for providing session tokens
import secrets

class TokenHandler:
    def __init__(self, tokenLength=16):
        self.tokenLength = tokenLength

    def getNewToken(self):
        return secrets.token_hex(self.tokenLength)