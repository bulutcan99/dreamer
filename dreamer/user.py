from typing import NoReturn
from flask import session
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class UserModel(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    surname = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(200), nullable=False)
    dreams = db.relationship('DreamModel', lazy='dynamic')


    def __init__(self, name, surname, email, password):
        self.name = name
        self.surname = surname
        self.password = password
        self.email = email


    def save_to_db(self) -> NoReturn:
        db.session.add(self)
        db.session.commit()

    @classmethod
    def find_by_email(cls, email: str):
        return cls.query.filter_by(email=email).first()

    @classmethod
    def find_by_id(cls, id: int):
        return cls.query.filter_by(id=id).first()

    @classmethod
    def find_all(cls):
        return cls.query.all()

    def get_name_surname(self) -> str:
        return f"{self.name} {self.surname}"

    def json(self) -> dict:
        return {
            "id": self.id,
            "email": self.email,
            "name": self.name,
            "surname": self.surname
        }

    def repr_(self):
        return self.name + " " + self.surname


class DreamModel(db.Model):
    __tablename__ = "dreams"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    dream = db.Column(db.String(300), nullable=False)
    detail = db.Column(db.Text)
    quote = db.Column(db.String(300), nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship("UserModel")

    def __init__(self, dream: str, detail: str, quote: str, user_id: int):
        self.dream = dream
        self.detail = detail
        self.quote = quote
        self.user_id = user_id

    def save_to_db(self) -> NoReturn:
        db.session.add(self)
        db.session.commit()

    @classmethod
    def find_by_id(cls, id: int):
        return cls.query.filter_by(id=id).first()

    @classmethod
    def find_all(cls):
        return cls.query.all()

    @classmethod
    def find_all_by_user_id(cls, user_id: int):
        return cls.query.filter_by(user_id=user_id).all()


    def get_user_id(self):
        return self.user_id

    def json(self) -> dict:
        return {
            "id": self.id,
            "dream": self.dream,
            "detail": self.detail,
            "quote": self.quote,
            "dreamer": self.dreamer,
            "user_id": self.user_id
        }

    def repr_(self):
        return self.name + " " + self.surname
