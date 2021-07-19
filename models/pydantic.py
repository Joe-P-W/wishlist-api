import re
from typing import Optional

from pydantic import BaseModel, constr, condecimal, validator, conint
from tortoise.contrib.pydantic import pydantic_model_creator

from models.constants import USERNAME_TYPE, PASSWORD_TYPE, ITEM_NAME_MAX_LENGTH, HTTP_LINK_MAX_LENGTH, ITEM_NAME_TYPE
from models.regex import URL_REGEX
from models.tortoise import User

UserIn = pydantic_model_creator(User, name="User")


class CreateUserIn(BaseModel):
    username: USERNAME_TYPE
    password: PASSWORD_TYPE


class CreateUserOut(BaseModel):
    username: USERNAME_TYPE


class GetUserOut(BaseModel):
    username: USERNAME_TYPE


class AddToWishlistIn(BaseModel):
    item_name: ITEM_NAME_TYPE
    item_link: Optional[constr(max_length=HTTP_LINK_MAX_LENGTH)]
    item_price: Optional[condecimal(decimal_places=2)]
    want_rating: Optional[conint(ge=1, le=10)]

    @validator("item_link")
    def link_must_be_http_link(cls, url):
        if not re.fullmatch(URL_REGEX, url):
            raise ValueError("url doesn't match url regex")

        return url


class AddToWishlistOut(BaseModel):
    username: USERNAME_TYPE
    item_name: ITEM_NAME_TYPE
    item_link: Optional[constr(max_length=HTTP_LINK_MAX_LENGTH)]
    item_price: Optional[condecimal(decimal_places=2)]
    want_rating: Optional[conint(ge=1, le=10)]


class GetWishlistOut(BaseModel):
    username: USERNAME_TYPE
    item_name: ITEM_NAME_TYPE
    item_link: Optional[constr(max_length=HTTP_LINK_MAX_LENGTH)]
    item_price: Optional[condecimal(decimal_places=2)]
    want_rating: Optional[conint(ge=1, le=10)]


class UpdateWishlistInfo(BaseModel):
    item_name: Optional[ITEM_NAME_TYPE]
    item_link: Optional[constr(max_length=HTTP_LINK_MAX_LENGTH)]
    item_price: Optional[condecimal(decimal_places=2)]
    want_rating: Optional[conint(ge=1, le=10)]

    @validator("item_link")
    def link_must_be_http_link(cls, url):
        if not re.fullmatch(URL_REGEX, url):
            raise ValueError("url doesn't match url regex")

        return url


class PatchWishlistIn(BaseModel):
    item_name: ITEM_NAME_TYPE
    update_info: UpdateWishlistInfo
