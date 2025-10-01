import base64

# Hardcoded valid credentials
VALID_CREDENTIALS = {"admin": "password123"}

def check_auth(headers, handler):
    """
    Checks Basic Auth credentials from request headers.
    Returns True if authorized, False otherwise.
    """
    auth_header = headers.get('Authorization')

    if not auth_header:
        handler.send_response(401)
        handler.send_header('WWW-Authenticate', 'Basic realm="SMS Transactions API"')
        handler.end_headers()
        return False

    try:
        auth_type, credentials = auth_header.split(' ', 1)
        if auth_type.lower() != 'basic':
            raise ValueError()

        decoded_credentials = base64.b64decode(credentials).decode('utf-8')
        username, password = decoded_credentials.split(':', 1)

        if username not in VALID_CREDENTIALS or VALID_CREDENTIALS[username] != password:
            raise ValueError()

        return True

    except:
        handler.send_response(401)
        handler.send_header('WWW-Authenticate', 'Basic realm="SMS Transactions API"')
        handler.end_headers()
        return False
