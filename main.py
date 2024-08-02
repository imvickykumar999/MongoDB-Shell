import jwt
import datetime

# Secret key to encode the JWT
SECRET_KEY = 'your_secret_key'

# Function to create a JWT token with custom expiry time
def create_jwt_token(data, expires_in_seconds):
    # Current time
    current_time = datetime.datetime.utcnow()
    # Expiry time
    expiry_time = current_time + datetime.timedelta(seconds=expires_in_seconds)
    # Payload with expiry time
    payload = {
        'data': data,
        'exp': expiry_time
    }
    # Encode the JWT token
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return token

# Example usage
custom_data = {'user_id': 123}
expiry_time_seconds = 3600  # Token valid for 1 hour
token = create_jwt_token(custom_data, expiry_time_seconds)
print(f"\nGenerated JWT Token: {token}")

# Function to decode a JWT token
def decode_jwt_token(token):
    try:
        # Decode the token
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return 'Token has expired'
    except jwt.InvalidTokenError:
        return 'Invalid token'

# Example usage
decoded_data = decode_jwt_token(token)
print(f"\nDecoded JWT Data: {decoded_data}")
