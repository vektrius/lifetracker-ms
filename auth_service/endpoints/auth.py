from typing import Any
from fastapi import APIRouter, Depends
from jose import JWTError, ExpiredSignatureError
from jose.exceptions import JWTClaimsError
from pydantic import BaseModel, model_validator

from core.auth import Tokens, create_tokens, oauth2_scheme, decode_token, RefreshTokenData, AccessTokenData
from core.helpers import json_exception
from database.database import get_session
from models.user import User
from repository.user import UserRepository

router = APIRouter(
    prefix='/api/auth',
    tags=['Авторизация']
)


class RegisterRequest(BaseModel):
    username: str
    password: str
    confirm_password: str

    @model_validator(mode='after')
    @classmethod
    def check_password_equals(cls, data: Any) -> Any:
        if isinstance(data, dict):
            assert (
                    data['password'] == data['confirm_password']
            ), 'Пароли не совпадают.'
        return data


class LoginRequest(BaseModel):
    username: str
    password: str


@router.post("/login")
async def login(login_request: LoginRequest):
    user: User = await UserRepository.find_one(username=login_request.username)

    if not UserRepository.authenticate_user(user=user, password=login_request.password):
        return {'error': 'Не верный логин или пароль.'}

    return await create_tokens(user)


@router.post("/register")
async def register(register_request: RegisterRequest) -> Tokens:
    async with get_session() as session:
        user = await UserRepository.create_user(register_request.username, register_request.password, session=session)
        tokens = await create_tokens(user)
        return tokens


@router.get("/token-introspection")
async def token_introspection(token: str = Depends(oauth2_scheme)):
    try:
        return decode_token(token)
    except ExpiredSignatureError:
        return json_exception("Signature has expired.", status_code=403)
    except JWTClaimsError:
        return json_exception("Something's wrong..", status_code=403)
    except JWTError:
        return json_exception("Signature is invalid.", status_code=403)



"""

JWTError: If the signature is invalid in any way.
ExpiredSignatureError: If the signature has expired.
JWTClaimsError: If any claim is invalid in any way.
        
        """
