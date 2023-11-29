from models.user import User
from repository.base import BaseRepository, SessionMixin
from sqlalchemy.ext.asyncio import AsyncSession

class UserRepository(SessionMixin, BaseRepository):
    model = User
    
    @classmethod
    async def create_user(cls, username: str, password: str, session: AsyncSession = None):
        from core.auth import hash_password
        return await UserRepository.add(session=session, username=username, password=hash_password(password))


    @classmethod
    async def authenticate_user(cls, user: User, password: str, session: AsyncSession = None):
        from core.auth import verify_password
        
        if not user:
            return False
        if not verify_password(password, user.password):
            return False
        
        return user
