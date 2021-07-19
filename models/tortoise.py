from passlib.hash import bcrypt
from tortoise import fields
from tortoise.models import Model

from models.constants import USERNAME_MAX_LENGTH, PASSWORD_MAX_LENGTH


class User(Model):
    id = fields.IntField(pk=True)
    username = fields.CharField(USERNAME_MAX_LENGTH, unique=True)
    password_hash = fields.CharField(PASSWORD_MAX_LENGTH)

    def verify_password(self, password):
        return bcrypt.verify(password, self.password_hash)
