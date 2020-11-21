import json
import redis
import uuid

from datetime import datetime
from jwcrypto import jwt, jwk
from fastapi import FastAPI
from peewee import DoesNotExist
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

from dbModels.User import User
from dbModels.Subscriber import Subscriber
from requestModels.AuthRequest import AuthRequest
from requestModels.UserRegisterRequest import UserRegisterRequest

app = FastAPI()
ph = PasswordHasher()
r = redis.Redis(host='localhost', port=6379)


@app.post('/auth/login/')
async def auth(request: AuthRequest):
    try:
        user = User().get(username=request.username)
        ph.verify(user.password, request.password)
    except DoesNotExist:
        return {'status': 401}
    except VerifyMismatchError:
        return {'status': 401}

    # Key to sign the token
    key = jwk.JWK(generate='oct', size=256)

    # Token to enclosure the payload
    token = jwt.JWT(header={'alg': 'HS256'},
                    claims={'for': user.get_id(),
                            'created': datetime.now().isoformat()})
    token.make_signed_token(key)

    # Encrypts token with the signing secret
    encrypted_token = jwt.JWT(header={"alg": "A256KW", "enc": "A256CBC-HS512"},
                              claims=token.serialize())
    encrypted_token.make_encrypted_token(key)

    # Store secret for the token to Redis
    r.set(encrypted_token.serialize(), key.export())

    return encrypted_token.serialize()


@app.get('/auth/validate/')
async def validate(token: str):
    redis_query = r.get(token)

    # Tokens are stored only in Redis, cuz its fast af and persistence is overrated
    if not redis_query:
        return {'status': 404}

    k = json.loads(redis_query)

    key = jwk.JWK(**k)
    encrypted_token = jwt.JWT(key=key, jwt=token)
    signed_token = jwt.JWT(key=key, jwt=encrypted_token.claims)

    return signed_token.claims


# How is this even secure
# Anyone with subscriber key can do stuff
# Registration service?
@app.post('/register-user')
async def register_user(request: UserRegisterRequest):
    try:
        subscriber = Subscriber().get(subscriber_key=request.subscriber_key)
    except DoesNotExist:
        return {'status': 404, 'message': f'Unknown subscriber {request.subscriber_key}'}

    if not subscriber.can_register:
        return {'status': 401, 'message': 'Unauthorized'}

    user = User.create(id=uuid.uuid4(), username=request.username, email=request.email,
                       password=ph.hash(request.password), registered_by=subscriber,
                       active=True, created=datetime.now())
    return {'status': 201, 'message': f'User {user.username} registered successfully'}

