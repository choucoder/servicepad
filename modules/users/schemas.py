from marshmallow import Schema, fields, validate, validates, ValidationError

from core.schemas import BaseSchema


class UserSchema(BaseSchema):
    id = fields.Int(dump_only=True)
    fullname = fields.Str(
        validate=validate.Length(max=128), required=True
    )
    email = fields.Email(required=True)
    password = fields.Str(required=True, load_only=True)
    photo = fields.Raw(type='file')

    class Meta:
        ordered = True


class LoginSchema(BaseSchema):
    email = fields.Email(required=True)
    password = fields.Str(required=True)
