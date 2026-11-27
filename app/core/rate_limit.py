"""Limite de tentativas de login, para impedir que alguém fique chutando senhas.

Usa o Redis quando ele está disponível (os contadores valem para todos os
processos da API). Se o Redis cair, usa um contador em memória, para o login
continuar funcionando.
"""
import time
from threading import Lock

import redis

from app.core.config import settings

MAX_FAILURES = 5          # tentativas erradas permitidas
WINDOW_SECONDS = 15 * 60  # por janela de 15 minutos

_redis = redis.Redis.from_url(settings.REDIS_URL, socket_connect_timeout=1, socket_timeout=1)
_memory: dict[str, tuple[int, float]] = {}
_lock = Lock()


def _keys(email: str, ip: str) -> list[str]:
    # Conta por e-mail (protege a conta) e por IP (protege contra chutar várias contas).
    return [f"login_fail:email:{email.lower()}", f"login_fail:ip:{ip}"]


def is_blocked(email: str, ip: str) -> bool:
    for key in _keys(email, ip):
        try:
            count = int(_redis.get(key) or 0)
        except redis.RedisError:
            with _lock:
                count, expires = _memory.get(key, (0, 0.0))
                if expires < time.time():
                    count = 0
        # O limite por IP é mais alto, para uma casa com várias pessoas não ser bloqueada.
        limit = MAX_FAILURES if ":email:" in key else MAX_FAILURES * 4
        if count >= limit:
            return True
    return False


def register_failure(email: str, ip: str) -> None:
    for key in _keys(email, ip):
        try:
            pipe = _redis.pipeline()
            pipe.incr(key)
            pipe.expire(key, WINDOW_SECONDS, nx=True)
            pipe.execute()
        except redis.RedisError:
            with _lock:
                count, expires = _memory.get(key, (0, 0.0))
                if expires < time.time():
                    count, expires = 0, time.time() + WINDOW_SECONDS
                _memory[key] = (count + 1, expires)


def clear(email: str) -> None:
    key = f"login_fail:email:{email.lower()}"
    try:
        _redis.delete(key)
    except redis.RedisError:
        with _lock:
            _memory.pop(key, None)
