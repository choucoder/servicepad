import json

from flasgger.utils import swag_from
from flask import request, Response, make_response, send_from_directory
from flask_restful import Resource
from werkzeug.security import (
    generate_password_hash, check_password_hash
)   

from .models import User
from .schemas import UserSchema, LoginSchema
from core.auth import get_token, get_user_by_token, token_required
from core.utils import save_picture
from database.connection import db


class LoginResource(Resource):
    """Login Resource class
    
    Endpoint: /users/login
    """
    def __init__(self) -> None:
        super().__init__()
        self.loginSchema = LoginSchema()
    
    @swag_from('../../swagger/user_login.yaml')
    def post(self):
        """Login POST method for User authentication"""
        form = json.loads(request.data, strict=False)
        form, error = self.loginSchema.verify(form)

        if error:
            return Response(
                json.dumps(error), status=400, mimetype='application/json'
            )

        user = User.query.filter_by(email=form['email']).first()

        if not user:
            return Response(
                json.dumps({'message': 'Could not verify'}),
                status=401,
                mimetype='application/json'
            )
        
        if check_password_hash(user.password, form['password']):
            token = get_token(user)
            response = make_response({
                'id': user.id,
                'fullname': user.fullname,
                'token': token
            })
            response.set_cookie("x-access-token", token)
            return response

        return Response(
            json.dumps({'message': 'Could not verify, wrong password'}),
            status=401,
            mimetype='application/json'
        )


class UserResource(Resource):
    """User Resource for create and list User

    Endpoint: /users
    """
    def __init__(self) -> None:
        super().__init__()
        self.schemas = {}
        self.schemas['create'] = UserSchema()
        self.schemas['list'] = UserSchema(many=True)
    
    @swag_from('../../swagger/user_register.yaml')
    def post(self):
        """Create a User"""
        form = json.loads(request.data, strict=False)
        form, error = UserSchema().verify(form)

        if error:
            return Response(
                json.dumps(error), status=400, mimetype='application/json'
            )

        user = User.query.filter_by(email=form['email']).first()

        if not user:
            password = generate_password_hash(form.pop('password'))
            b64image = form.pop('photo')
            filename = save_picture(b64image)

            user = User(
                **form,
                photo=filename,
                password=password
            )
            
            db.session.add(user)
            db.session.commit()
            return Response(
                json.dumps({'message': 'Successfully registered.'}),
                status=201,
                mimetype='application/json'
            )
        else:
            return Response(
                json.dumps({'message': 'User already exists. Log in'}),
                status=422,
                mimetype='application/json'
            )

    @token_required
    @swag_from('../../swagger/user_list.yaml')
    def get(self):
        """List all registered users"""
        users = User.query.order_by(User.id).all()
        results = self.schemas['list'].dumps(users)

        return Response(
            json.dumps({'data': json.loads(results)}),
            status=200,
            mimetype='application/json'
        )


class SingleUserResource(Resource):
    """SingleUser Resource for get user details, update and
    delete an User

    Endpoint: /users/{id}
    """
    def __init__(self) -> None:
        super().__init__()
        self.schema = UserSchema()

    def check_permission(self, headers, user) -> bool:
        """Check if the current user has permission for update or delete
        a given user

        Parameters
        ---
            headers: Dict of http headers
            user: User object

        Return True if the current_user is equal to the user given user,
        otherwise return False
        """
        current_user = get_user_by_token(headers)
        return current_user.id == user.id
    
    @token_required
    @swag_from('../../swagger/user_details.yaml')
    def get(self, id):
        """Get User details for a given User id
        
        Parameters
        ---
            id: User id
        """
        user = User.query.get_or_404(id, description="User not found")
        result = json.loads(self.schema.dumps(user))

        return Response(
            json.dumps({'data': result}), status=200,
            mimetype='application/json'
        )

    @token_required
    @swag_from('../../swagger/user_partial_update.yaml')
    def patch(self, id):
        """Partially update a user for a given User id
        
        Parameters
        ---
            id: User id
        """
        user = User.query.get_or_404(id, description="User not found")
        
        if not self.check_permission(request.headers, user):
            return Response(
                json.dumps({'message': "You can not update this user"}),
                status=403,
                mimetype='application/json'
            )

        form = json.loads(request.data, strict=False)
        form, error = UserSchema().verify(form, partial=True)

        if error:
            return Response(
                json.dumps(error), status=400, mimetype='application/json'
            )

        if 'email' in form:
            user2 = User.query.filter_by(email=form['email']).first()
            if user2 and user2.email != user.email:
                return Response(
                    json.dumps({'message': 'Email is already taken'}),
                    status=400,
                    mimetype='application/json'
                )
        user.update(form)
        db.session.refresh(user)        
        result = json.loads(self.schema.dumps(user))

        return Response(
            json.dumps({'data': result}), status=200,
            mimetype='application/json'
        )

    @token_required
    @swag_from('../../swagger/user_update.yaml')
    def put(self, id):
        """Update a user for a given User id
        
        Parameters
        ---
            id: User id
        """
        user = User.query.get_or_404(id, description="User not found")
        if not self.check_permission(request.headers, user):
            return Response(
                json.dumps({'message': "You can not update this user"}),
                status=403,
                mimetype='application/json'
            )

        form = json.loads(request.data, strict=False)
        form, error = UserSchema().verify(form)

        if error:
            return Response(
                json.dumps(error), status=400, mimetype='application/json'
            )
        
        user2 = User.query.filter_by(email=form['email']).first()
        if user2 and user2.email != user.email:
            return Response(
                json.dumps({'message': 'Email is already taken'}),
                status=400,
                mimetype='application/json'
            )
        user.update(form)
        db.session.refresh(user)        
        result = json.loads(self.schema.dumps(user))

        return Response(
            json.dumps({'data': result}), status=200,
            mimetype='application/json'
        ) 
    
    @token_required
    @swag_from('../../swagger/user_delete.yaml')
    def delete(self, id):
        """Delete a user for a given User id
        
        Parameters
        ---
            id: User id
        """
        user = User.query.get_or_404(id, description="User not found")
        if not self.check_permission(request.headers, user):
            return Response(
                json.dumps({'message': "You cannot delete this user"}),
                status=403,
                mimetype='application/json'
            )
        db.session.delete(user)
        db.session.commit()
        return Response(status=204, mimetype='application/json')