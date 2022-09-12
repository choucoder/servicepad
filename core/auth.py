from datetime import datetime, timedelta
from functools import wraps
import json
from typing import Dict

from decouple import config
from flask import Response, request
import jwt

from modules.users.models import User


SECRET_KEY = config('SECRET_KEY')

def token_required(func):
    """Decorator for validate that a token is passed in the headers"""
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
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            user = User.query\
                .get_or_404(data['id'])
        except Exception as e:
            return Response(
                json.dumps({'message': 'Token is invalid'}),
                status=401,
                mimetype='application/json'
            )
        return func(*args, **kwargs)
  
    return decorated


def get_user_by_token(headers: Dict) -> User:
    """Function to obtain the current user given the token
    
    Parameters
    ---
    headers: Http headers for get the x-access-token.

    Return the current user
    """
    data = jwt.decode(headers['x-access-token'], SECRET_KEY,
                      algorithms=["HS256"])
    user = User.query.filter_by(id = data['id']).first()
    return user


def get_token(user: User) -> Dict:
    """Create and return a json web token
    
    Parameters
    ---
    user: User
    """
    token = jwt.encode({
        'id': user.id,
        'exp': datetime.utcnow() + timedelta(minutes=45)
    }, SECRET_KEY, algorithm="HS256")
    return token