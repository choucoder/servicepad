from datetime import datetime, timedelta
from functools import wraps
import json
from typing import Dict

from decouple import config
from flask import Response, request
import jwt

from modules.users.models import User


def token_required(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        token = None
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']

        if not token:
            return Response(
                json.dumps({'message': 'Token is missing'}),
                status=401,
                mimetype='application/json'
            )

        try:
            data = jwt.decode(token, config('SECRET_KEY'), algorithms=["HS256"])
            # TODO use just get for throw an exception if id does not exist
            user = User.query\
                .filter_by(id = data['id'])\
                .first()
        except Exception as e:
            return Response(
                json.dumps({'message': 'Token is invalid'}),
                status=401,
                mimetype='application/json'
            )
        return func(*args, **kwargs)
  
    return decorated


def get_user_by_token(headers: Dict) -> User:
    data = jwt.decode(headers['x-access-token'], config('SECRET_KEY'),
                      algorithms=["HS256"])
    user = User.query.filter_by(id = data['id']).first()
    return user


def get_token(user: User) -> Dict:
    token = jwt.encode({
        'id': user.id,
        'exp': datetime.utcnow() + timedelta(minutes=45)
    }, config('SECRET_KEY'), algorithm="HS256")
    return token