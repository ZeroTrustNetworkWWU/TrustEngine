from flask import Flask, request, jsonify
from TrustEngineExceptions import MissingResourceAccess, UserNotFound, InvalidLogin, InvalidRegistration, IPAddressChange
from UserDataHandler import UserDataHandler
from TrustEngineConfig import TrustEngineConfig
import sqlite3

# Create a Flask app instance
app = Flask(__name__)

class TrustEngine:
    def __init__(self, host, port, enforcerModel, accessEnforcer, userDb):
        # Prepare the user database and access enforcment model
        TrustEngine.userDatabase = UserDataHandler(userDb, enforcerModel, accessEnforcer)

        self.host = host
        self.port = port
    
    @app.route('/getDecision', methods=['POST'])
    def getDecision():
        response_data = {"trustLevel": False, "session": None}
        try:
            data = request.get_json()
            session = data.get("session", None)

            if not TrustEngine.userDatabase.validateSession(session):
                raise InvalidLogin("Invalid session token")

            role = TrustEngine.userDatabase.getRoleFromSession(session)
            if role is None:
                raise UserNotFound("Cannot match session to role")
        
            # Validate that the user has access to the resource
            if not TrustEngine.userDatabase.accessEnforcer.enforce(role, data["resource"], data["action"]):
                raise MissingResourceAccess("User does not have access to this resource")

            # TODO validate the request more rigurously
            if not TrustEngine.userDatabase.validateIP(session, data["ip"]):
                TrustEngine.userDatabase.removeSession(session)
                raise IPAddressChange("Request has different IP from login")

            # Respond with the decision
            response_data["trustLevel"] = True
            response_data["session"] = session
            return jsonify(response_data), 200

        except MissingResourceAccess as e:
            return jsonify(response_data), 200
        except UserNotFound as e:
            return jsonify(response_data), 200
        except InvalidLogin as e:
            return jsonify(response_data), 200
        except IPAddressChange as e:
            return jsonify(response_data), 200
        
    @app.route('/login', methods=['POST'])
    def login():
        response_data = {"trustLevel": False, "session": None}
        try:
            data = request.get_json()

            if not TrustEngine.userDatabase.validateUser(data):
                raise InvalidLogin("Invalid login request")

            # TODO validate the request more rigurously

            session = TrustEngine.userDatabase.getNewSessionToken(data["user"], data["ip"])
            
            response_data["trustLevel"] = True
            response_data["session"] = session
            
            return jsonify(response_data), 200
        
        except InvalidLogin as e:
            return jsonify(response_data), 200

        except IPAddressChange as e:
            return jsonify(response_data), 200

    @app.route('/logout', methods=['POST'])
    def logout():
        response_data = {"trustLevel": False}
        try:
            data = request.get_json()
            session = data.get("session", None)

            if not TrustEngine.userDatabase.validateSession(session):
                raise InvalidLogin("Invalid session token")

            # TODO validate the request more rigurously

            # logout the user
            TrustEngine.userDatabase.removeSession(session)

            # Respond with the decision
            response_data["trustLevel"] = True
            return jsonify(response_data), 200

        except InvalidLogin as e:
            return jsonify(response_data), 200

    @app.route('/register', methods=['POST'])
    def register():
        response_data = {"trustLevel": False}
        try:
            data = request.get_json()

            if not TrustEngine.userDatabase.registerUser(data):
                raise InvalidRegistration("Invalid registration request")

            # TODO validate the request more rigurously

            response_data["trustLevel"] = True
            return jsonify(response_data), 200

        except InvalidRegistration as e:
            return jsonify(response_data), 200

    @app.route('/removeAccount', methods=['POST'])
    def removeAccount():
        pass

    @app.route('/getRoles', methods=['POST'])
    def getRoles():
        pass

    @app.route('/getUsers', methods=['POST'])
    def getUsers():
        pass

    @app.route('/getSessions', methods=['POST'])
    def getSessions():
        pass

    @app.route('/addRole', methods=['POST'])
    def addRole():
        pass

    @app.route('/removeRole', methods=['POST'])
    def removeRole():
        pass

    @app.route('/addUser', methods=['POST'])
    def addUser():
        pass

    @app.route('/removeUser', methods=['POST'])
    def removeUser():
        pass

    # Start the Flask app
    def run(self):
        app.run(host=self.host, port=self.port)#, ssl_context=('cert.pem', 'key.pem'))
    
    @app.route('/log', methods=['POST'])
    def log_entry():
        data = request.json
        timestamp = data.get('timestamp')
        ip = data.get('ip')
        user = data.get('user')
        resource = data.get('resource')
        action = data.get('action')
        additional_info = data.get('additional_info')

        try:
            conn = sqlite3.connect('trust_engine_logs.db')
            cursor = conn.cursor()
            cursor.execute('''
            INSERT INTO logs (timestamp, ip, user, resource, action, additional_info)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (timestamp, ip, user, resource, action, additional_info))
            conn.commit()
            conn.close()
            return 'Log entry added', 200
        except Exception as e:
            print(f"Failed to log entry: {e}")
            return 'Failed to log entry', 500
    

# Entry point
if __name__ == "__main__":
    engine = TrustEngine(host='0.0.0.0', port=5001, enforcerModel="enforcerModel.conf", accessEnforcer="AccessEnforcer.db", userDb="UserData.db")
    engine.run()