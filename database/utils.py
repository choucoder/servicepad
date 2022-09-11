from re import X


from flask import abort


def get_resource_or_404(obj, **kwargs):
    user = obj.query.filter_by(**kwargs).first()
    if user is None:
        abort(404, message='Resource not found!')
    return user