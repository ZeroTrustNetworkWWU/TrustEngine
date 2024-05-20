# A file that handles connection to the database

import sqlite3
from TrustEngineExceptions import InvalidLogin, InvalidRegistration
from TokenHandler import TokenHandler
from PasswordHandler import PasswordHandler
from datetime import datetime, timedelta
import casbin
import casbin_sqlalchemy_adapter

class UserDataHandler:
    defaultRole = "user"

    def __init__(self, dbName, enforcerModel, accessEnforcer):
        self.dbName = dbName
        self.tokenHandler = TokenHandler()
        self.passwordHandler = PasswordHandler()

        adapter = casbin_sqlalchemy_adapter.Adapter("sqlite:///" + accessEnforcer)
        self.accessEnforcer = casbin.Enforcer(enforcerModel, adapter)

        # Add the admin and user default policies TODO remove this
        self.accessEnforcer.add_policy("admin", "/*", "*")
        self.accessEnforcer.add_policy("user", "/testGet", "GET")

        # Add the default user to the database
        with sqlite3.connect(self.dbName) as conn:
            cursor = conn.cursor()

            # Create the needed tables if they don't exist
            cursor.execute("CREATE TABLE IF NOT EXISTS users (username TEXT, password TEXT, role TEXT)")
            cursor.execute("CREATE TABLE IF NOT EXISTS sessions (username TEXT, session TEXT, expiration TEXT, ip_addr TEXT)")

            # Add the admin user if it doesn't exist TODO remove this
            if not self.userExists("user1"):
                cursor.execute("INSERT INTO users VALUES (?, ?, ?)", ("user1", self.passwordHandler.hash_password("password1"), "admin"))
            
            conn.commit()

    def getRoleFromUser(self, user):
        with sqlite3.connect(self.dbName) as conn:
            cursor = conn.cursor()
            role = cursor.execute("SELECT role FROM users WHERE username=?", (user,)).fetchone()[0]

        return role
    
    def getRoleFromSession(self, session):
        with sqlite3.connect(self.dbName) as conn:
            cursor = conn.cursor()
            username = cursor.execute("SELECT username FROM sessions WHERE session=?", (session,)).fetchone()[0]

        return self.getRoleFromUser(username)
    
    def registerUser(self, data):
        user = data.get("user", None)
        password = data.get("password", None)
        role = UserDataHandler.defaultRole
        if user is None or password is None:
            raise InvalidRegistration("Invalid registration request")
        self.addUser(user, password, role)
        return True
    
    # Adds a user to the database first checking if the user already exists
    def addUser(self, user, password, role):
        # Check if the user already exists
        if self.userExists(user):
            raise InvalidRegistration("User already exists")

        with sqlite3.connect(self.dbName) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users VALUES (?, ?, ?)", (user, self.passwordHandler.hash_password(password), role))
            conn.commit()
    
    def validateUser(self, data):
        user = data.get("user", None)
        password = data.get("password", None)
        if not self.userExists(user):
            raise InvalidLogin("Invalid username")
        if not self.validatePassword(user, password):
            raise InvalidLogin("Invalid password")
        return True
        
    def validateSession(self, session):
        if session is None:
            return False
        
        with sqlite3.connect(self.dbName) as conn:
            cursor = conn.cursor()
            result = cursor.execute("SELECT username, expiration FROM sessions WHERE session=?", (session,)).fetchone()
            
        if result is None:
            return False
        
        username, expiration = result

        if not self.userExists(username) or datetime.strptime(expiration, "%Y-%m-%d %H:%M:%S") < datetime.now():
            return False
        
        # Update the expiration time if there is less than 10 minutes left
        if datetime.strptime(expiration, "%Y-%m-%d %H:%M:%S") < datetime.now() + timedelta(minutes=10):
            with sqlite3.connect(self.dbName) as conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE sessions SET expiration=? WHERE session=?", ((datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S"), session))
                conn.commit()

        return True

    def validateIP(self, session, requestIP):
        with sqlite3.connect(self.dbName) as conn:
            cursor = conn.cursor()
            loginIP = cursor.execute("SELECT ip_addr FROM sessions WHERE session=?", (session,)).fetchone()[0]
        return requestIP == loginIP
        
    def getSessionFromUser(self, user):
        if user is None:
            return None

        with sqlite3.connect(self.dbName) as conn:
            cursor = conn.cursor()
            session = cursor.execute("SELECT session FROM sessions WHERE username=?", (user,)).fetchone()

        if session is None:
            return None

        return session[0]

    def getNewSessionToken(self, user, ip_addr):
        # make sure the user is not already logged in if so 
        # logout the old session and create a new one
        session = self.getSessionFromUser(user)
        if self.validateSession(session):
            self.removeSession(session)

        # Get the session token
        token = self.tokenHandler.getNewToken()
        expiration = datetime.now() + timedelta(hours=1)

        # Add the session token to the database making sure to remove any previous sessions for the user
        with sqlite3.connect(self.dbName) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM sessions WHERE username=?", (user,))
            cursor.execute("INSERT INTO sessions VALUES (?, ?, ?, ?)", (user, token, expiration.strftime("%Y-%m-%d %H:%M:%S"), ip_addr))
            conn.commit()

        return token
    
    def userExists(self, user):
        if user is None:
            return False
        
        with sqlite3.connect(self.dbName) as conn:
            cursor = conn.cursor()
            username = cursor.execute("SELECT * FROM users WHERE username=?", (user,))

        return username.fetchone() is not None
    
    def validatePassword(self, user, password):
        if user is None or password is None:
            return False

        with sqlite3.connect(self.dbName) as conn:
            cursor = conn.cursor()
            dbPassword = cursor.execute("SELECT password FROM users WHERE username=?", (user,)).fetchone()[0]

        return self.passwordHandler.verify_password(password, dbPassword)
    
    def removeSession(self, session):
        with sqlite3.connect(self.dbName) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM sessions WHERE session=?", (session,))
            conn.commit()

    def getAllUsers(self):
        with sqlite3.connect(self.dbName) as conn:
            cursor = conn.cursor()
            usernames = cursor.execute("SELECT * FROM users WHERE username IS NOT NULL")
            # should it be only "SELECT username, role" instead?

        return usernames.fetchall()
    
    def removeUser(self, data):
        username = data.get("user", None)
        if username is None:
            return False

        with sqlite3.connect(self.dbName) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM users WHERE username=?", (username,))
            conn.commit()

        return True

    def getAllRoles(self):
        with sqlite3.connect(self.dbName) as conn:
            cursor = conn.cursor()
            roles = cursor.execute("SELECT DISTINCT role FROM users WHERE role IS NOT NULL")

        return roles.fetchall()