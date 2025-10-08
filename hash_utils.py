"""
hash_utils.py

Funciones puras para hashing, salting, peppering y HMAC.
Diseñado para ser importado por app.py.

Funcionalidades:
- hash_text: hash de texto con varios algoritmos soportados.
- hash_file_chunked: hash incremental de archivos (lee en chunks).
- generate_salt: generar salt seguro (base64).
- apply_salt: combinar texto+salt (básico).
- apply_pepper: combinar texto+pepper (pepper no se guarda en repo).
- hmac_text: calcular HMAC usando hmac library.
- compare_hashes: comparar de forma segura (hmac.compare_digest).
"""

from __future__ import annotations
import hashlib
import hmac
import os
import base64
from typing import Tuple, Optional, Iterable, Callable

# Algoritmos soportados por defecto
DEFAULT_ALGOS = ['sha256', 'sha1', 'sha512', 'blake2b']

def _get_hasher(name: str):
    """
    Devuelve un constructor de objeto hash de hashlib según el nombre.
    Raise ValueError si no existe.
    """
    name = name.lower()
    if name not in hashlib.algorithms_available and name not in hashlib.algorithms_guaranteed:
        # intentar mapear blake2b
        if name == 'blake2b' and 'blake2b' in hashlib.algorithms_available:
            return lambda: hashlib.blake2b()
        raise ValueError(f"Algoritmo {name} no soportado en este entorno.")
    def ctor():
        return hashlib.new(name)
    return ctor

def hash_text(text: str, algorithm: str = 'sha256', encoding: str='utf-8') -> str:
    """
    Calcula el hash del texto dado y devuelve hex digest.
    - text: cadena a hashear.
    - algorithm: 'sha256' por defecto (soporta: sha1, sha256, sha512, blake2b).
    """
    ctor = _get_hasher(algorithm)
    h = ctor()
    h.update(text.encode(encoding))
    return h.hexdigest()

def hash_file_chunked(file_obj, algorithm: str='sha256', chunk_size: int=8192, progress_callback: Optional[Callable[[int], None]]=None) -> str:
    """
    Calcula hash de un fichero leyendo en chunks.
    - file_obj: objeto file-like (con read()) ya posicionado al inicio.
    - progress_callback: función opcional que recibe bytes leídos para actualizar UI.
    Devuelve hex digest.
    """
    ctor = _get_hasher(algorithm)
    h = ctor()
    total = 0
    while True:
        chunk = file_obj.read(chunk_size)
        if not chunk:
            break
        if isinstance(chunk, str):
            chunk = chunk.encode('utf-8')
        h.update(chunk)
        total += len(chunk)
        if progress_callback:
            try:
                progress_callback(total)
            except Exception:
                pass
    return h.hexdigest()

def generate_salt(n_bytes: int=16) -> str:
    """
    Genera un salt seguro y devuelve base64 (fácil de almacenar).
    - n_bytes: tamaño en bytes (16 por defecto).
    """
    return base64.b64encode(os.urandom(n_bytes)).decode('utf-8')

def apply_salt(text: str, salt_b64: str) -> str:
    """
    Combina texto y salt (salt público) en una forma estable.
    Notar: el salt se almacena junto al hash en la práctica.
    """
    return f"{salt_b64}${text}"

def apply_pepper(text: str, pepper: str) -> str:
    """
    Aplica pepper (secreto compartido) al texto antes de hashear.
    Pepper debe guardarse en st.secrets o similar y NO en el repo.
    """
    return f"{pepper}${text}"

def hmac_text(text: str, key: str, algorithm: str='sha256', encoding: str='utf-8') -> str:
    """
    Calcula HMAC del texto usando la clave proporcionada.
    - key: string secreto (no en repo).
    - algorithm: algoritmo de hashlib compatible para HMAC.
    """
    algo = algorithm.lower()
    if algo not in hashlib.algorithms_available and algo not in hashlib.algorithms_guaranteed:
        if algo == 'blake2b' and 'blake2b' in hashlib.algorithms_available:
            digestmod = hashlib.blake2b
        else:
            digestmod = None
    else:
        digestmod = lambda d=b'': hashlib.new(algo, d)
    # hmac.new acepta callable for digestmod in Python 3.11+, but to be safe we use name
    h = hmac.new(key.encode(encoding), msg=text.encode(encoding), digestmod=hashlib.new(algo))
    return h.hexdigest()

def compare_hashes(a: str, b: str) -> bool:
    """
    Comparación segura en tiempo constante (usando hmac.compare_digest).
    """
    return hmac.compare_digest(a, b)
