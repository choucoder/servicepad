from marshmallow import Schema, fields, validate, validates, ValidationError

from core.schemas import BaseSchema
from core.utils import is_valid_picture


class UserSchema(BaseSchema):
    """User Schema class for validate User Creation/Update.
    Also it's used for serialize User objects model into json
    """
    id = fields.Int(dump_only=True)
    fullname = fields.Str(
        validate=validate.Length(max=128), required=True
    )
    email = fields.Email(required=True)
    password = fields.Str(required=True, load_only=True)
    photo = fields.Str()

    @validates("photo")
    def validate_picture(self, value):
        if not is_valid_picture(value):
            raise ValidationError(
                {'message': "The photo field must be a valid base64 image"}
            )

    class Meta:
        ordered = True


class LoginSchema(BaseSchema):
    """Login Schema class for validate User Login"""
    email = fields.Email(required=True)
    password = fields.Str(required=True)
