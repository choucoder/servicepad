import json

from flask import request, Response, send_from_directory
from flask_restful import Resource

from .models import Publication
from ..users.models import User
from .schemas import PublicationSchema
from ..publications.models import Publication
from core.auth import get_user_by_token, token_required
from database.connection import db


class PublicationResource(Resource):
    def __init__(self) -> None:
        super().__init__()
        self.schemas = {}
        self.schemas['create'] = PublicationSchema()
        self.schemas['list'] = PublicationSchema(many=True)
    
    @token_required
    def post(self):
        form = json.loads(request.data, strict=False)
        form, errs = self.schemas['create'].verify(form)

        if errs:
            return Response(
                json.dumps(errs), status=422, mimetype='application/json'
            )

        user = get_user_by_token(request.headers)
        post = Publication(**form, user=user)

        db.session.add(post)
        db.session.commit()
        db.session.refresh(post)

        result = json.loads(self.schemas['create'].dumps(post))

        return Response(
            json.dumps({'data': result}), status=201,
            mimetype='application/json'
        )

    @token_required
    def get(self):
        posts = Publication.query.order_by(Publication.id).all()
        results = json.loads(self.schemas['list'].dumps(posts))

        return Response(
            json.dumps({'data': results}),
            status=200,
            mimetype='application/json'
        )


class SinglePublicationResource(Resource):
    def __init__(self) -> None:
        super().__init__()
        self.schemas = {}
        self.schemas['create'] = PublicationSchema()
        self.schemas['list'] = PublicationSchema(many=True)

    def check_permissions(self, user: User, post: Publication) -> bool:
        return post.user_id == user.id

    @token_required
    def get(self, id):
        user = get_user_by_token(request.headers)
        post = Publication.query.get_or_404(id, description="Post not found")

        if not self.check_permissions(user, post):
            return Response(
                json.dumps({'message': 'Unauthorized for get post'}),
                status=403,
                mimetype='application/json'
            )
        result = json.loads(self.schemas['create'].dumps(post))

        return Response(
            json.dumps({'data': result}), status=200,
            mimetype='application/json'
        )

    @token_required
    def patch(self, id):
        user = get_user_by_token(request.headers)
        post = Publication.query.get_or_404(id, description="Post not found")

        if not self.check_permissions(user, post):
            return Response(
                json.dumps({'message': 'Unauthorized for update this post'}),
                status=403,
                mimetype='application/json'
            )
        form = json.loads(request.data, strict=False)
        form, error = self.schemas['create'].verify(form, partial=True)
        
        if error:
            return Response(
                json.dumps(error), status=400, mimetype='application/json'
            )

        post.update(form)
        db.session.refresh(post)
        result = json.loads(self.schemas['create'].dumps(post))

        return Response(
            json.dumps({'data': result}), status=200,
            mimetype='application/json'
        )

    @token_required
    def put(self, id):
        user = get_user_by_token(request.headers)
        post = Publication.query.get_or_404(id, description="Post not found")

        if not self.check_permissions(user, post):
            return Response(
                json.dumps({'message': 'Unauthorized for update this post'}),
                status=403,
                mimetype='application/json'
            )
        form = json.loads(request.data, strict=False)
        form, error = self.schemas['create'].verify(form)

        if error:
            return Response(
                json.dumps(error), status=400, mimetype='application/json'
            )

        post.update(form)
        db.session.refresh(post)
        result = json.loads(self.schemas['create'].dumps(post))

        return Response(
            json.dumps({'data': result}), status=200,
            mimetype='application/json'
        )

        
    @token_required
    def delete(self, id):
        user = get_user_by_token(request.headers)
        post = Publication.query.get_or_404(id, description="Post not found")

        if not self.check_permissions(user, post):
            return Response(
                json.dumps({'message': 'Unauthorized for delete post'}),
                status=403,
                mimetype='application/json'
            )

        db.session.delete(post)
        db.session.commit()
        return Response(status=204, mimetype='application/json')