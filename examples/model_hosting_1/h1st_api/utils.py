import json
import jwt
import requests
from django.contrib.auth import authenticate

def jwt_get_username_from_payload_handler(payload):
    username = payload.get('sub').replace('|', '.')
    authenticate(remote_user=username)
    return username

def jwt_decode_token(token):
    header = jwt.get_unverified_header(token)
    jwks = requests.get('https://{}/.well-known/jwks.json'.format(os.getenv('AUTH0_DOMAIN', 'aitomatic.us.auth0.com'))).json()
    public_key = None
    for jwk in jwks['keys']:
        if jwk['kid'] == header['kid']:
            public_key = jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(jwk))

    if public_key is None:
        raise Exception('Public key not found.')

    issuer = 'https://{}/'.format('YOUR_DOMAIN')
    return jwt.decode(token, public_key, audience=os.getenv('AUTH0_API', 'https://aitomatic.us.auth0.com/api/v2/'), issuer=issuer, algorithms=['RS256'])
