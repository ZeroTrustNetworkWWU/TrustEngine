# TrustEngine

## Description:
The Trust Engine is the core component of the Zero Trust Network. It is responsible for processing trust data and making decisions on whether to allow or deny a request. This README provides an overview of the project structure and how to navigate through its components.

## Prerequisites:
- Python 3.10 or higher
- Git (for cloning the repository)
- Windows or Linux OS

## Installation
Clone the repository by running the following command:
```bash
git clone https://github.com/ZeroTrustNetworkWWU/TrustEngine
```

To run the Trust Engine server, you can do so by running the following command:
```bash
./start.bat
```

Or if your on a linux system:
```bash
./start.sh
```

## Structure:
- `TrustEngine.py`: Contains the main code for the Trust Engine server. This server is responsible for processing trust data and making decisions on whether to allow or deny a request.
- `TrustEngineExceptions.py`: Contains custom exceptions that are raised by the Trust Engine server. These exceptions are used to handle errors that occur during the trust data processing.
- `TrustEngineConfig.py`: Contains the configuration settings for the Trust Engine server. Currently empty.
- `UserDataHandler.py`: Contains the database for storing users and their associated data. Also handles active sessions and role based access control using Casbin.

# Trust Engine Flow

## Processing a Generic Request
1. The EdgeNode sends a request to the Trust Engine server.
2. The trust data validates the session key and extracts the user's role.
3. The Trust Engine verifies the resource being requested is within the user's role.
4. the Trust Engine verifies the IP address of the client has not changed since login.
5. The Trust Engine returns a decision to the EdgeNode.

## Processing a Login Request
1. The EdgeNode sends a login request to the Trust Engine server.
2. The Trust Engine verifies the username and password. 
3. If the login is successful, the Trust Engine saves the IP associated with the new session key.
3. The Trust Engine generates a session key and returns it to the EdgeNode.

## Processing a Logout Request
1. The EdgeNode sends a logout request to the Trust Engine server.
2. The Trust Engine deletes the session key from the database.

## Updating roles and Users
1. TODO - This is not yet implemented however it should be done through the AdminGUI.

