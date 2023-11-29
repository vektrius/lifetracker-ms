from models.tokens import RefreshTokens
from repository.base import BaseRepository, SessionMixin

class RefreshTokensRepository(SessionMixin, BaseRepository):
    model = RefreshTokens


