from datetime import datetime, timedelta

import jwt
import pytz
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from tortoise.exceptions import DoesNotExist

from authentication.constants import JWT_SECRET, JWT_TIMEOUT_S
from models.pydantic import UserAPI
from models.tortoise import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="authenticate")


async def authenticate_user(username: str, password: str):

    try:
        user = await User.get(username=username)
    except DoesNotExist:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")
    if not user.verify_password(password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")

    return user


async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        user_object = await User.get(id=payload.get("id"))
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")
    else:
        authenticated_time = datetime.fromisoformat(payload["authenticated_time"])
        if authenticated_time + timedelta(seconds=JWT_TIMEOUT_S) < datetime.now(pytz.utc):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has timed out")

    return await UserAPI.from_tortoise_orm(user_object)
