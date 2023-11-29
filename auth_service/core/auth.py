
import datetime
from fastapi import Depends
from fastapi.security import OAuth2AuthorizationCodeBearer
from passlib.context import CryptContext
from pydantic import BaseModel
from core.settings import settings
from exceptions.auth import NotUserException

from models.user import User
from database.database import get_session
from jose import jwt
from repository.tokens import RefreshTokensRepository

from repository.user import UserRepository    
    
class AccessTokenData(BaseModel):
    username: str
    exp: int
    type: str

class RefreshTokenData(BaseModel):
    username: str
    exp: int
    type: str
    
class Tokens(BaseModel):
    access_token: str
    refresh_token: str
    
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2AuthorizationCodeBearer(authorizationUrl='auth', tokenUrl="login")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def decode_token(token) -> AccessTokenData | RefreshTokenData:
    payload = jwt.decode(token, key=settings.SECRET_KEY, algorithms=settings.ALGORITHM)
    return AccessTokenData(**payload) if payload['type'] == 'access' else RefreshTokenData(**payload) 


def create_jwt_token(data: dict, type: str, expires_delta: datetime.timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.datetime.utcnow() + expires_delta
    else:
        expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=15)
        
    to_encode.update({"exp": expire, "type": type})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


async def create_tokens(user: User) -> Tokens:
    tokens = Tokens(
        access_token=create_jwt_token({"username": user.username}, type="access"), 
        refresh_token=create_jwt_token({"username": user.username}, type="access", expires_delta=datetime.timedelta(days=1))
    )
    await RefreshTokensRepository.add(token=tokens.refresh_token, user_id=user.id)
    
    return tokens
    
    
async def refresh_tokens(refresh_token: str) -> Tokens:
    payload: RefreshTokenData = decode_token(refresh_token)
    username: str = payload.get('username', None)
    if username is None:
        raise NotUserException('Имя пользователя не было переданно.')
    
    async with get_session() as session:
        user: User = await UserRepository.find_one(session=session, username=username, refresh_token__token=refresh_token)
        if user is None:
            raise NotUserException("Пользователь не найден.")
        tokens: Tokens = await create_tokens(user)
        
        await RefreshTokensRepository.delete(session=session, token=refresh_token)
        
        return tokens
        
        
async def get_user_for_token(token: str = Depends(oauth2_scheme)):
    payload: AccessTokenData = decode_token(token)
    user = await UserRepository.find_one(username=payload.username)
    return user

