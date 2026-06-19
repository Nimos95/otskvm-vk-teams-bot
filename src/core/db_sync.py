# src/core/db_sync.py

import os
import psycopg2
from psycopg2 import pool
from dotenv import load_dotenv
import re

load_dotenv()


class DatabaseSync:
    """Синхронный доступ к базе данных."""
    
    _pool = None
    _initialized = False
    
    @classmethod
    def _parse_url(cls, url):
        """Парсит DATABASE_URL."""
        # postgresql://user:password@host:port/dbname
        match = re.match(
            r'postgresql://([^:]+):([^@]+)@([^:]+):(\d+)/(.+)',
            url
        )
        if not match:
            raise ValueError(f"Неверный формат DATABASE_URL: {url}")
        return match.groups()
    
    @classmethod
    def get_pool(cls):
        """Получает или создаёт пул соединений."""
        if cls._pool is None:
            database_url = os.getenv('DATABASE_URL')
            if not database_url:
                raise ValueError("DATABASE_URL не найден в .env")
            
            user, password, host, port, dbname = cls._parse_url(database_url)
            
            cls._pool = psycopg2.pool.SimpleConnectionPool(
                1, 10,
                host=host,
                port=port,
                database=dbname,
                user=user,
                password=password
            )
            cls._initialized = True
            print("✅ Синхронный пул БД создан")
        return cls._pool
    
    @classmethod
    def get_connection(cls):
        """Получает соединение из пула."""
        pool = cls.get_pool()
        return pool.getconn()
    
    @classmethod
    def return_connection(cls, conn):
        """Возвращает соединение в пул."""
        if cls._pool:
            cls._pool.putconn(conn)
    
    @classmethod
    def execute(cls, query, params=None):
        """
        Выполняет запрос без возврата данных (INSERT, UPDATE, DELETE).
        Возвращает количество затронутых строк.
        """
        conn = cls.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(query, params)
                conn.commit()
                return cur.rowcount
        finally:
            cls.return_connection(conn)
    
    @classmethod
    def fetchone(cls, query, params=None):
        """Выполняет запрос и возвращает одну строку."""
        conn = cls.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(query, params)
                return cur.fetchone()
        finally:
            cls.return_connection(conn)
    
    @classmethod
    def fetchall(cls, query, params=None):
        """Выполняет запрос и возвращает все строки."""
        conn = cls.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(query, params)
                return cur.fetchall()
        finally:
            cls.return_connection(conn)
    
    @classmethod
    def close(cls):
        """Закрывает пул соединений."""
        if cls._pool:
            cls._pool.closeall()
            cls._pool = None
            cls._initialized = False
            print("🔒 Синхронный пул БД закрыт")