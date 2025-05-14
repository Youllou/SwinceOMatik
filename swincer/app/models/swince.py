from ..db import db

class Swince(db.Model):
    __tablename__ = "swince"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    date = db.Column(db.DateTime, nullable=False)
    origin = db.Column(db.Integer, db.ForeignKey("user.id"))

    origin_user = db.relationship("User", backref="swince_origin")
