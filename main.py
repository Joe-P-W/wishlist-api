from datetime import datetime

import jwt
import pytz
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from passlib.hash import bcrypt
from tortoise.contrib.fastapi import register_tortoise
from tortoise.exceptions import IntegrityError

from authentication.handler import authenticate_user, get_current_user
from authentication.constants import JWT_SECRET, JWT_TIMEOUT_S
from models.pydantic import UserAPI, CreateUser, CreateUserReturn, GetUserReturn
from models.tortoise import User

app = FastAPI()
register_tortoise(
    app,
    db_url="sqlite://db.sqlite3",
    modules={"models": ["models.tortoise"]},
    generate_schemas=True,
    add_exception_handlers=True
)


@app.post("/authenticate")
async def generate_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(form_data.username, form_data.password)

    user_object = await UserAPI.from_tortoise_orm(user)

    raw_token = {
        "id": user_object.id,
        "username": user_object.username,
        "authenticated_time": datetime.now(tz=pytz.utc).isoformat(),
        "authentication_timeout_seconds": JWT_TIMEOUT_S
    }

    token = jwt.encode(raw_token, JWT_SECRET)

    return {"access_token": token, "token_type": "bearer"}


@app.post("/users/create", response_model=CreateUserReturn)
async def create_user(user: CreateUser):
    user_object = User(username=user.username, password_hash=bcrypt.hash(user.password))

    try:
        await user_object.save()
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Username is not available")
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not create user.")

    return CreateUserReturn(username=user.username)


@app.get("/users/me", response_model=GetUserReturn)
async def get_user(user: UserAPI = Depends(get_current_user)):
    return GetUserReturn(username=user.username)
