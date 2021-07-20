from datetime import datetime

import jwt
import pytz
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from passlib.hash import bcrypt
from tortoise.contrib.fastapi import register_tortoise
from tortoise.exceptions import IntegrityError

from authentication.constants import JWT_SECRET, JWT_TIMEOUT_S
from authentication.handler import authenticate_user, get_current_user
from models.constants import ITEM_NAME_TYPE
from models.pydantic import UserIn, CreateUserIn, CreateUserOut, AddToWishlistIn, AddToWishlistOut, \
    GetWishlistOut, PatchWishlistIn
from models.tortoise import User, Wishlist

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
