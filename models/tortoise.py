from passlib.hash import bcrypt
from tortoise import fields
from tortoise.models import Model

from models.constants import USERNAME_MAX_LENGTH, PASSWORD_MAX_LENGTH, ITEM_NAME_MAX_LENGTH, HTTP_LINK_MAX_LENGTH


class User(Model):
    id = fields.IntField(pk=True)
    username = fields.CharField(USERNAME_MAX_LENGTH, unique=True)
    password_hash = fields.CharField(PASSWORD_MAX_LENGTH)

    def verify_password(self, password):
        return bcrypt.verify(password, self.password_hash)


class Wishlist(Model):
    id = fields.IntField(pk=True)
    username = fields.CharField(USERNAME_MAX_LENGTH)
    item_name = fields.CharField(ITEM_NAME_MAX_LENGTH)
    item_link = fields.CharField(HTTP_LINK_MAX_LENGTH, null=True)
    item_price = fields.FloatField(null=True)
    bought = fields.BooleanField()

    class Meta:
        unique_together = ("username", "item_name"),
