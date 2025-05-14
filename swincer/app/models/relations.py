from ..db import db

class Originator(db.Model):
    __tablename__ = "originator"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    swince_id = db.Column(db.Integer, db.ForeignKey("swince.id"), nullable=False)
    originator_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

class Target(db.Model):
    __tablename__ = "target"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    swince_id = db.Column(db.Integer, db.ForeignKey("swince.id"), nullable=False)
    target_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
