from typing import Optional

from pydantic import BaseModel, constr, condecimal
from tortoise.contrib.pydantic import pydantic_model_creator

from models.constants import USERNAME_TYPE, PASSWORD_TYPE, ITEM_NAME_MAX_LENGTH, HTTP_LINK_MAX_LENGTH
from models.tortoise import User

UserAPI = pydantic_model_creator(User, name="User")


class CreateUserIn(BaseModel):
    username: USERNAME_TYPE
    password: PASSWORD_TYPE


class CreateUserOut(BaseModel):
    username: USERNAME_TYPE


class GetUserOut(BaseModel):
    username: USERNAME_TYPE


class AddToWishlistIn(BaseModel):
    item_name: constr(min_length=3, max_length=ITEM_NAME_MAX_LENGTH)
    item_link: Optional[constr(max_length=HTTP_LINK_MAX_LENGTH)]
    item_price: Optional[condecimal(decimal_places=2)]


class AddToWishlistOut(BaseModel):
    username: USERNAME_TYPE
    item_name: constr(min_length=3, max_length=ITEM_NAME_MAX_LENGTH)
    item_link: Optional[constr(max_length=HTTP_LINK_MAX_LENGTH)]
    item_price: Optional[condecimal(decimal_places=2)]
    bought: bool


class GetWishlistOut(BaseModel):
    username: USERNAME_TYPE
    item_name: constr(min_length=3, max_length=ITEM_NAME_MAX_LENGTH)
    item_link: Optional[constr(max_length=HTTP_LINK_MAX_LENGTH)]
    item_price: Optional[condecimal(decimal_places=2)]
