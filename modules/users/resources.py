import json

from flask import request, Response, make_response, send_from_directory
from flask_restful import Resource
from werkzeug.security import (
    generate_password_hash, check_password_hash
)   

from .models import User
from .schemas import UserSchema, LoginSchema
from core.auth import get_token, get_user_by_token, token_required
from database.connection import db


class LoginResource(Resource):
    def __init__(self) -> None:
        super().__init__()
        self.loginSchema = LoginSchema()
    
    def post(self):
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
            response = make_response({'token': token})
            response.set_cookie("x-access-token", token)
            return response

        return Response(
            json.dumps({'message': 'Could not verify, wrong password'}),
            status=401,
            mimetype='application/json'
        )


class UserResource(Resource):
    def __init__(self) -> None:
        super().__init__()
        self.schemas = {}
        self.schemas['create'] = UserSchema()
        self.schemas['list'] = UserSchema(many=True)
    
    def post(self):
        print(request.json)
        form = json.loads(request.data, strict=False)
        form, error = UserSchema().verify(form)

        if error:
            return Response(
                json.dumps(error), status=400, mimetype='application/json'
            )

        user = User.query.filter_by(email=form['email']).first()

        if not user:
            print(form)
            password = generate_password_hash(form.pop('password'))
            user = User(
                **form,
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
                status=400,
                mimetype='application/json'
            )

    @token_required
    def get(self):
        users = User.query.order_by(User.id).all()
        results = self.schemas['list'].dumps(users)

        return Response(
            json.dumps({'data': json.loads(results)}),
            status=200,
            mimetype='application/json'
        )


class SingleUserResource(Resource):
    
    def __init__(self) -> None:
        super().__init__()
        self.schema = UserSchema()

    def check_permission(self, headers, user) -> bool:
        current_user = get_user_by_token(headers)
        return current_user.id == user.id
    
    @token_required
    def get(self, id):
        user = User.query.get_or_404(id, description="User not found")
        result = json.loads(self.schema.dumps(user))

        return Response(
            json.dumps({'data': result}), status=200,
            mimetype='application/json'
        )

    @token_required
    def patch(self, id):
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
    def put(self, id):
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
    def delete(self, id):
        user = User.query.get_or_404(id, description="User not found")
        if not self.check_permission(request.headers, user):
            return Response(
                json.dumps({'message': "You can not update this user"}),
                status=403,
                mimetype='application/json'
            )
        db.session.delete(user)
        db.session.commit()
        return Response(status=204, mimetype='application/json')