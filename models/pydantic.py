from pydantic import BaseModel
from tortoise.contrib.pydantic import pydantic_model_creator

from models.constants import USERNAME_TYPE, PASSWORD_TYPE
from models.tortoise import User

UserAPI = pydantic_model_creator(User, name="User")


class CreateUser(BaseModel):
    username: USERNAME_TYPE
    password: PASSWORD_TYPE


class GetUserReturn(BaseModel):
    username: USERNAME_TYPE


class CreateUserReturn(BaseModel):
    username: USERNAME_TYPE
