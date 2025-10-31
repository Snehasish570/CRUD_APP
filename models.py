from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(300), nullable=False)


class Item(db.Model):
    __tablename__ = 'items'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    mail = db.Column(db.String(50), unique=True, nullable=False)

    def to_dict(self):
        return {'id': self.id, 'name': self.name, 'mail': self.mail}
