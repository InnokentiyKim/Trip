from dishka import Scope
from pydantic_settings import BaseSettings


class MemoryDatabaseSettings(BaseSettings):
    life_scope: Scope = Scope.REQUEST
