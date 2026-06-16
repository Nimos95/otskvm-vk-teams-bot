# src/core/database.py

import os
import asyncpg
from typing import Optional, List
from dotenv import load_dotenv

load_dotenv()


class Database:
    """Класс для работы с базой данных PostgreSQL"""
    
    _pool: Optional[asyncpg.Pool] = None
    _initialized: bool = False
    
    @classmethod
    async def get_pool(cls) -> asyncpg.Pool:
        """Получение пула соединений (синглтон)"""
        if cls._pool is None:
            await cls._initialize()
        return cls._pool
    
    @classmethod
    async def _initialize(cls):
        """Инициализация пула соединений"""
        try:
            database_url = os.getenv('DATABASE_URL')
            
            if not database_url:
                raise ValueError(
                    "DATABASE_URL не найден в .env файле.\n"
                    "Пример: DATABASE_URL=postgresql://user:pass@host:port/dbname"
                )
            
            # Скрываем пароль в логах
            import re
            safe_url = re.sub(r':[^:@]+@', ':***@', database_url)
            print(f"🔗 Подключение к БД: {safe_url}")
            
            cls._pool = await asyncpg.create_pool(
                dsn=database_url,
                min_size=1,
                max_size=10,
                command_timeout=60
            )
            
            cls._initialized = True
            print("✅ Подключение к базе данных установлено")
            
        except Exception as e:
            print(f"❌ Ошибка подключения к БД: {e}")
            raise
    
    @classmethod
    async def execute(cls, query: str, *args) -> str:
        """Выполнение запроса без возврата данных"""
        pool = await cls.get_pool()
        async with pool.acquire() as conn:
            return await conn.execute(query, *args)
    
    @classmethod
    async def fetch(cls, query: str, *args) -> List[asyncpg.Record]:
        """Получение нескольких строк"""
        pool = await cls.get_pool()
        async with pool.acquire() as conn:
            return await conn.fetch(query, *args)
    
    @classmethod
    async def fetchrow(cls, query: str, *args) -> Optional[asyncpg.Record]:
        """Получение одной строки"""
        pool = await cls.get_pool()
        async with pool.acquire() as conn:
            return await conn.fetchrow(query, *args)
    
    @classmethod
    async def close(cls):
        """Закрытие пула соединений"""
        if cls._pool:
            await cls._pool.close()
            cls._pool = None
            cls._initialized = False
            print("🔒 Соединение с БД закрыто")