from datetime import datetime

from marshmallow import Schema, fields, validate, validates, ValidationError

from core.schemas import BaseSchema
from ..users.schemas import UserSchema


class PublicationSchema(BaseSchema):
    """Publication Schema class for validate Publication Creation
    and partial Update. Also it's used for serialize Publication
    objects into json
    """
    id = fields.Int(dump_only=True)
    title = fields.Str(
        validate=validate.Length(max=128), required=True
    )
    description = fields.Str(
        validate=validate.Length(max=512), required=True
    )
    priority = fields.Str(
        validate=validate.OneOf(["NORMAL", "URGENT"]),
        default="NORMAL"
    )
    status = fields.Str(
        validate=validate.OneOf(["1"]),
        default="1"
    )
    user = fields.Nested(UserSchema, dumb_only=True)
    
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

    posted_ago = fields.Method("get_time_ago", dump_only=True)

    def get_time_ago(self, post):
        """Compute and return the time since a post has been published
        (seconds, minutes, hours, days, weeks, months, years)

        Parameters
        ---
        post: A publication model object 
        """
        diff = datetime.utcnow() - post.created_at
        years = diff.days // 365
        months = diff.days // 30
        weeks = diff.days // 7
        days = diff.days
        hours = diff.seconds // 3600
        minuts = diff.seconds // 60

        ago_number = 0
        ago_string = ""

        if years:
            ago_string = "year" if years == 1 else "years"
            ago_number = years
        elif months:
            ago_string = "month" if months == 1 else "months"
            ago_number = months
        elif weeks:
            ago_string = "week" if weeks == 1 else "weeks"
            ago_number = weeks
        elif days:
            ago_string = "day" if days == 1 else "days"
            ago_number = days
        elif hours:
            ago_string = "hour" if hours == 1 else "hours"
            ago_number = hours
        elif minuts:
            ago_string = "min" if minuts == 1 else "minutes"
            ago_number = minuts
        else:
            ago_string = "secs"
            ago_number = diff.seconds

        return f"{ago_number} {ago_string} ago"


    class Meta:
        ordered = True


class PublicationUpdateSchema(PublicationSchema):
    """PublicationUpdate Schema class for validate Publication Update"""
    title = fields.Str(
        validate=validate.Length(max=128), required=True
    )
    description = fields.Str(
        validate=validate.Length(max=512), required=True
    )
    priority = fields.Str(
        validate=validate.OneOf(["NORMAL", "URGENT"]),
        required=True
    )
    status = fields.Str(
        validate=validate.OneOf(["1"]),
        required=True
    )