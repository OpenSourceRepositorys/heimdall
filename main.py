import json
import redis
import uuid

from datetime import datetime
from jwcrypto import jwt, jwk
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from peewee import DoesNotExist
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

from models.User import User
from models.Subscriber import Subscriber
from api_requests.AuthRequest import AuthRequest
from api_requests.UserRegisterRequest import UserRegisterRequest

app = FastAPI()
ph = PasswordHasher()
r = redis.Redis(host='redis', port=6379)

origins = [
    "http://friday",
    "http://friday:8000",
    "http://friday:8001",
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:8081",
    "http://localhost:4200",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post('/auth/login/')
async def auth(request: AuthRequest):
    try:
        user = User().get(username=request.username)
        ph.verify(user.password, request.password)
    except DoesNotExist:
        return {'status': 404}
    except VerifyMismatchError:
        return {'status': 401}

    # Key to sign the token
    key = jwk.JWK(generate='oct', size=256)

    # Token to enclosure the payload
    token = jwt.JWT(header={'alg': 'HS256'},
                    claims={'for': str(user.get_id()),
                            'created': datetime.now().isoformat()})
    token.make_signed_token(key)

    # Encrypts token with the signing secret
    encrypted_token = jwt.JWT(header={"alg": "A256KW", "enc": "A256CBC-HS512"},
                              claims=token.serialize())
    encrypted_token.make_encrypted_token(key)

    # Store secret for the token to Redis
    r.set(encrypted_token.serialize(), key.export())

    return {'status': 200, 'token': encrypted_token.serialize()}


# TODO: Check if signature can be manipulated
@app.get('/auth/validate/')
async def validate(token: str):
    print('Trying to resolve token... ' + token)
    print(token)
    print('Querying redis...')
    redis_query = r.get(token)
    print(redis_query)

    # Tokens are stored only in Redis, cuz its fast af and persistence is overrated
    if not redis_query:
        return {'status': 404}

    k = json.loads(redis_query)

    key = jwk.JWK(**k)
    encrypted_token = jwt.JWT(key=key, jwt=token)
    signed_token = jwt.JWT(key=key, jwt=encrypted_token.claims)

    return {'status': 200, 'user': json.loads(signed_token.claims)}


@app.get('/auth/user-details/')
async def user_details(token: str):
    redis_query = r.get(token)

    # Tokens are stored only in Redis, cuz its fast af and persistence is overrated
    if not redis_query:
        return {'status': 404}

    k = json.loads(redis_query)

    key = jwk.JWK(**k)
    encrypted_token = jwt.JWT(key=key, jwt=token)
    signed_token = jwt.JWT(key=key, jwt=encrypted_token.claims)
    token_content = json.loads(signed_token.claims)
    if 'for' in token_content.keys():
        try:
            user = User().get(id=token_content['for'])
        except DoesNotExist:
            return {'status': 404}

        return {'status': 200,
                'user': {**token_content, 'username': user.username}
                }
    return {'status': 500}


@app.post('/auth/register-user/')
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

