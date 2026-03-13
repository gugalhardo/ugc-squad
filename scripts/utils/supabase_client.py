"""
Client reutilizavel para Supabase (REST API + Storage).
Autenticacao via env vars SUPABASE_URL e SUPABASE_SECRET_KEY.

Uso:
    from scripts.utils.supabase_client import SupabaseClient

    db = SupabaseClient()
    db.insert("metrics_daily", {"account_id": "act_123", "date": "2026-03-09", ...})
    rows = db.select("metrics_daily", params={"account_id": "eq.act_123"})

    # Upload de arquivo para Supabase Storage
    url = db.upload_file("outputs", "tailor/ugc/scene-01.png", "/tmp/scene-01.png")
    url = db.upload_bytes("outputs", "tailor/ugc/scene-01.png", image_bytes, content_type="image/png")
"""

import os
import logging
import mimetypes
import requests
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


class SupabaseClient:
    def __init__(self):
        self.url = os.getenv("SUPABASE_URL")
        # Aceita tanto SUPABASE_SECRET_KEY quanto SUPABASE_SERVICE_ROLE_KEY
        self.key = os.getenv("SUPABASE_SECRET_KEY") or os.getenv("SUPABASE_SERVICE_ROLE_KEY")

        if not self.url or not self.key:
            raise EnvironmentError(
                "SUPABASE_URL e SUPABASE_SECRET_KEY (ou SUPABASE_SERVICE_ROLE_KEY) "
                "nao encontrados no .env. Configure as credenciais do Supabase."
            )

        self.base_url = f"{self.url}/rest/v1"
        self.headers = {
            "apikey": self.key,
            "Authorization": f"Bearer {self.key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation",
        }
        logger.info("SupabaseClient inicializado")

    def select(self, table: str, params: dict | None = None) -> list:
        """SELECT com filtros PostgREST."""
        url = f"{self.base_url}/{table}"
        r = requests.get(url, headers=self.headers, params=params)
        r.raise_for_status()
        return r.json()

    def insert(self, table: str, data: dict | list) -> list:
        """INSERT de um ou mais registros."""
        url = f"{self.base_url}/{table}"
        r = requests.post(url, headers=self.headers, json=data if isinstance(data, list) else [data])
        r.raise_for_status()
        return r.json()

    def update(self, table: str, filters: dict, data: dict) -> list:
        """UPDATE com filtros PostgREST."""
        url = f"{self.base_url}/{table}"
        r = requests.patch(url, headers=self.headers, params=filters, json=data)
        r.raise_for_status()
        return r.json()

    def upsert(self, table: str, data: dict | list) -> list:
        """UPSERT (insert or update on conflict)."""
        url = f"{self.base_url}/{table}"
        headers = {**self.headers, "Prefer": "return=representation,resolution=merge-duplicates"}
        r = requests.post(url, headers=headers, json=data if isinstance(data, list) else [data])
        r.raise_for_status()
        return r.json()

    def delete(self, table: str, filters: dict) -> list:
        """DELETE com filtros PostgREST."""
        url = f"{self.base_url}/{table}"
        r = requests.delete(url, headers=self.headers, params=filters)
        r.raise_for_status()
        return r.json()

    def rpc(self, function_name: str, params: dict | None = None) -> dict:
        """Chama uma funcao SQL (stored procedure)."""
        url = f"{self.url}/rest/v1/rpc/{function_name}"
        r = requests.post(url, headers=self.headers, json=params or {})
        r.raise_for_status()
        return r.json()

    # ------------------------------------------------------------------
    # Storage
    # ------------------------------------------------------------------

    def upload_file(self, bucket: str, storage_path: str, local_path: str,
                    upsert: bool = True) -> str:
        """Faz upload de arquivo local para Supabase Storage.

        Retorna a URL publica do arquivo.

        Args:
            bucket: Nome do bucket (ex: 'outputs')
            storage_path: Caminho dentro do bucket (ex: 'tailor/ugc/scene-01.png')
            local_path: Caminho local do arquivo
            upsert: Se True, sobrescreve arquivo existente (default: True)
        """
        content_type, _ = mimetypes.guess_type(local_path)
        content_type = content_type or "application/octet-stream"
        with open(local_path, "rb") as f:
            data = f.read()
        return self.upload_bytes(bucket, storage_path, data,
                                 content_type=content_type, upsert=upsert)

    def upload_bytes(self, bucket: str, storage_path: str, data: bytes,
                     content_type: str = "application/octet-stream",
                     upsert: bool = True) -> str:
        """Faz upload de bytes para Supabase Storage.

        Retorna a URL publica do arquivo.
        """
        url = f"{self.url}/storage/v1/object/{bucket}/{storage_path}"
        headers = {
            "apikey": self.key,
            "Authorization": f"Bearer {self.key}",
            "Content-Type": content_type,
            "x-upsert": "true" if upsert else "false",
        }
        r = requests.post(url, headers=headers, data=data)
        r.raise_for_status()
        public_url = f"{self.url}/storage/v1/object/public/{bucket}/{storage_path}"
        logger.info(f"Storage upload OK: {public_url}")
        return public_url

    def get_public_url(self, bucket: str, storage_path: str) -> str:
        """Retorna a URL publica de um arquivo no Storage (sem fazer request)."""
        return f"{self.url}/storage/v1/object/public/{bucket}/{storage_path}"


if __name__ == "__main__":
    db = SupabaseClient()
    print("Supabase conectado com sucesso!")
    print(f"URL: {db.url}")
