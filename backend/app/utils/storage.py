from abc import ABC, abstractmethod
from pathlib import Path


class StorageBackend(ABC):
    @abstractmethod
    async def save(self, local_path: Path, remote_key: str) -> str:
        """Save file, return URL or path."""

    @abstractmethod
    async def get_url(self, remote_key: str) -> str:
        """Get public URL for file."""

    @abstractmethod
    async def delete(self, remote_key: str) -> None:
        """Delete file."""


class LocalStorage(StorageBackend):
    async def save(self, local_path: Path, remote_key: str) -> str:
        return str(local_path)

    async def get_url(self, remote_key: str) -> str:
        return f"/static/{remote_key}"

    async def delete(self, remote_key: str) -> None:
        p = Path(remote_key)
        if p.exists():
            p.unlink()
