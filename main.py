import secrets
from binascii import b2a_base64
from datetime import datetime

import aioredis
import jwt
import pytz
import uvicorn
from aioredis import Redis
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from passlib.hash import bcrypt
from tortoise.contrib.fastapi import register_tortoise
from tortoise.exceptions import IntegrityError

from authentication.constants import JWT_SECRET, JWT_TIMEOUT_S
from authentication.handler import authenticate_user, get_current_user
from friends.constants import FRIEND_TOKEN_TTL
from models.constants import ITEM_NAME_TYPE
from models.pydantic import (
    UserIn, CreateUserIn, CreateUserOut, AddToWishlistIn, AddToWishlistOut, GetWishlistOut, PatchWishlistIn,
    GetMakeFriendTokenOut, PostMakeFriendIn, PostMakeFriendsOut
)
from models.tortoise import User, Wishlist, Friends

app = FastAPI()
register_tortoise(
    app,
    db_url="sqlite://db.sqlite3",
    modules={"models": ["models.tortoise"]},
    generate_schemas=True,
    add_exception_handlers=True
)

redis: Redis


@app.on_event("startup")
async def startup_event():
    global redis

    redis = aioredis.from_url(
        "redis://localhost", encoding="utf-8", decode_responses=True,
    )


@app.post("/authenticate")
async def generate_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(form_data.username, form_data.password)

    user_object = await UserIn.from_tortoise_orm(user)

    raw_token = {
        "id": user_object.id,
        "username": user_object.username,
        "authenticated_time": datetime.now(tz=pytz.utc).isoformat(),
        "authentication_timeout_seconds": JWT_TIMEOUT_S
    }

    token = jwt.encode(raw_token, JWT_SECRET)

    return {"access_token": token, "token_type": "bearer"}


@app.post("/users/create", response_model=CreateUserOut)
async def create_user(user: CreateUserIn):
    user_object = User(username=user.username, password_hash=bcrypt.hash(user.password))

    try:
        await user_object.save()
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Username is not available")
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not create user.")

    return CreateUserOut(username=user.username)


@app.post("/wishlist/add", response_model=AddToWishlistOut)
async def add_to_wishlist(wanted_item: AddToWishlistIn, user: UserIn = Depends(get_current_user)):
    wishlist_object = Wishlist(**wanted_item.dict(), username=user.username, bought=False)

    try:
        await wishlist_object.save()
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=f"'{wanted_item.item_name}' already listed in your wishlist."
        )
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not save to wishlist.")

    return AddToWishlistOut(**wanted_item.dict(), username=user.username)


@app.get("/wishlist/mine", response_model=list[GetWishlistOut])
async def get_my_wishlist(user: UserIn = Depends(get_current_user)):
    return await Wishlist.filter(username=user.username).values(
        "username", "item_name", "item_link", "item_price", "want_rating"
    )


@app.delete("/wishlist/mine/{item_name}")
async def delete_from_my_wishlist(item_name: ITEM_NAME_TYPE, user: UserIn = Depends(get_current_user)):
    await Wishlist.filter(username=user.username, item_name=item_name).delete()


@app.patch("/wishlist/mine")
async def update_wishlist_item(item: PatchWishlistIn, user: UserIn = Depends(get_current_user)):
    update_info = item.update_info.dict(exclude_none=True)
    await Wishlist.filter(username=user.username, item_name=item.item_name).update(**update_info)


@app.get("/friends/make_token", response_model=GetMakeFriendTokenOut)
async def make_token(user: UserIn = Depends(get_current_user)):
    global redis

    token = b2a_base64(bytes.fromhex(secrets.token_hex(12))).decode().strip("\n")
    await redis.set(token, user.username, ex=FRIEND_TOKEN_TTL)

    return GetMakeFriendTokenOut(token=token)


@app.post("/friends/make_friend", response_model=PostMakeFriendsOut)
async def make_friend(friend_token: PostMakeFriendIn, user: UserIn = Depends(get_current_user)):
    global redis

    friend = await redis.get(friend_token.token)

    if friend is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="No such code"
        )
    if friend == user.username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="You can't make friends with yourself"
        )

    try:
        await Friends(username=user.username, friend=friend).save()
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"You and {friend} are already friends"
        )

    return PostMakeFriendsOut(username=user.username, friend=friend)


@app.on_event("shutdown")
async def shutdown_event():
    await redis.close()


if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=8000, reload=True, debug=True)
