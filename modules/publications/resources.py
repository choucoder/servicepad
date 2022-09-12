import json

from flasgger.utils import swag_from
from flask import request, Response, send_from_directory
from flask_restful import Resource

from .models import Publication
from ..users.models import User
from .schemas import PublicationSchema, PublicationUpdateSchema
from ..publications.models import Publication
from core.auth import get_user_by_token, token_required
from database.connection import db


class PublicationResource(Resource):
    """Publication Resource for create and list Post

    Endpoint: /publications
    """
    def __init__(self) -> None:
        super().__init__()
        self.schemas = {}
        self.schemas['create'] = PublicationSchema()
        self.schemas['list'] = PublicationSchema(many=True)

    @token_required
    @swag_from('../../swagger/publication_create.yaml')
    def post(self):
        """Create a Post"""
        form = json.loads(request.data, strict=False)
        form, error = self.schemas['create'].verify(form)

        if error:
            return Response(
                json.dumps(error), status=400, mimetype='application/json'
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
    @swag_from('../../swagger/publication_list.yaml')
    def get(self):
        """List all posts"""
        posts = Publication.query.order_by(Publication.id).all()
        results = json.loads(self.schemas['list'].dumps(posts))

        return Response(
            json.dumps({'data': results}),
            status=200,
            mimetype='application/json'
        )


class SinglePublicationResource(Resource):
    """SinglePublication Resource for get post details, update and
    delete a post

    Endpoint: /publications/{id}
    """
    def __init__(self) -> None:
        super().__init__()
        self.schemas = {}
        self.schemas['create'] = PublicationSchema()
        self.schemas['list'] = PublicationSchema(many=True)
        self.schemas['update'] = PublicationUpdateSchema()

    def check_permissions(self, user: User, post: Publication) -> bool:
        """Check if the current user has permission for update or delete
        a post

        Parameters
        ---
            headers: Dict of http headers
            post: Post object

        Return True if the Post was created by the given user,
        otherwise return False
        """
        return post.user_id == user.id

    @token_required
    @swag_from('../../swagger/publication_detail.yaml')
    def get(self, id):
        """Get Post details for a given Post id
        
        Parameters
        ---
            id: Post id
        """
        post = Publication.query.get_or_404(id, description="Post not found")
        result = json.loads(self.schemas['create'].dumps(post))

        return Response(
            json.dumps({'data': result}), status=200,
            mimetype='application/json'
        )

    @token_required
    @swag_from('../../swagger/publication_partial_update.yaml')
    def patch(self, id):
        """Partially update a post for a given post id
        
        Parameters
        ---
            id: Post id
        """
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
    @swag_from('../../swagger/publication_update.yaml')
    def put(self, id):
        """Update a post for a given post id
        
        Parameters
        ---
            id: Post id
        """
        user = get_user_by_token(request.headers)
        post = Publication.query.get_or_404(id, description="Post not found")

        if not self.check_permissions(user, post):
            return Response(
                json.dumps({'message': 'Unauthorized for update this post'}),
                status=403,
                mimetype='application/json'
            )
        form = json.loads(request.data, strict=False)
        form, error = self.schemas['update'].verify(form)

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
    @swag_from('../../swagger/publication_delete.yaml')
    def delete(self, id):
        """Delete a post for a given Post id
        
        Parameters
        ---
            id: Post id
        """
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


class UserPublicationsResource(Resource):
    """UserPublication Resource for list all posts by a user"""
    def __init__(self) -> None:
        super().__init__()
        self.schema = PublicationSchema(many=True)

    @token_required
    @swag_from('../../swagger/user_publications.yaml')
    def get(self, id):
        """List all posts by a user"""
        user = User.query.get_or_404(id, description="User not found")
        posts = Publication.query\
            .filter_by(user_id=user.id)\
            .order_by(Publication.id).all()

        posts = self.schema.dumps(posts)
        return Response(
            json.dumps({'data': json.loads(posts)}),
            status=200,
            mimetype='application/json'
        )