from datetime import datetime

from ..users.models import db


class Publication(db.Model):
    __tablename__ = 'publication_table'
 
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(128))
    description = db.Column(db.String(512), unique=True, nullable=False)
    priority = db.Column(db.String(), nullable=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship("User", backref=db.backref("users", lazy="dynamic"))

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    status = db.Column(db.String())
    
    def __init__(self, title, description, priority, status, user):
        self.title = title
        self.description = description
        self.priority = priority
        self.status = status
        self.user = user

    def update(self, data):
        for name, value in data.items():
            setattr(self, name, value)
        self.updated_at = datetime.utcnow()

        db.session.add(self)
        db.session.commit()

    def __repr__(self):
        return f"{self.fullname}:{self.email}"