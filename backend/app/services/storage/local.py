import hashlib
import shutil
import uuid
from datetime import datetime
from pathlib import Path

from fastapi import HTTPException, UploadFile

from app.core.config import settings
from app.services.storage.base import StorageProvider, StoredFile


class LocalStorageProvider(StorageProvider):
    def _get_base_dir(self, visibility: str) -> Path:
        if visibility == "public":
            return Path(settings.UPLOAD_PUBLIC_DIR).resolve()
        elif visibility == "private":
            return Path(settings.UPLOAD_PRIVATE_DIR).resolve()
        raise ValueError(f"Unknown visibility: {visibility}")

    def save(
        self,
        *,
        file: UploadFile,
        visibility: str,
        extension: str,
        max_size_bytes: int,
    ) -> StoredFile:
        base_dir = self._get_base_dir(visibility)
        now = datetime.now()
        year_str = now.strftime("%Y")
        month_str = now.strftime("%m")

        target_dir = base_dir / year_str / month_str
        target_dir.mkdir(parents=True, exist_ok=True)

        file_uuid = uuid.uuid4()
        filename = f"{file_uuid}.{extension}"
        storage_key = f"{year_str}/{month_str}/{filename}"

        final_path = target_dir / filename
        # Ensure it doesn't escape base dir
        if not final_path.resolve().is_relative_to(base_dir):
            raise HTTPException(status_code=400, detail="Invalid path")

        sha256_hash = hashlib.sha256()
        size_bytes = 0

        # Read into temp file, checking size
        temp_path = target_dir / f"{filename}.tmp"
        try:
            with open(temp_path, "wb") as out_file:
                while chunk := file.file.read(8192):
                    size_bytes += len(chunk)
                    if size_bytes > max_size_bytes:
                        raise HTTPException(
                            status_code=400,
                            detail=f"File too large. Max size is {max_size_bytes} bytes",
                        )
                    sha256_hash.update(chunk)
                    out_file.write(chunk)

            # Atomically move to final path
            shutil.move(temp_path, final_path)
        except Exception as e:
            if temp_path.exists():
                temp_path.unlink()
            raise e
        finally:
            file.file.seek(0)  # Reset file pointer

        public_url = None
        if visibility == "public":
            public_url = f"{settings.UPLOAD_PUBLIC_URL_PREFIX.rstrip('/')}/{storage_key}"

        return StoredFile(
            storage_provider="local",
            storage_key=storage_key,
            public_url=public_url,
            size_bytes=size_bytes,
            sha256=sha256_hash.hexdigest(),
        )

    def delete(self, *, visibility: str, storage_key: str) -> None:
        base_dir = self._get_base_dir(visibility)
        target_path = (base_dir / storage_key).resolve()
        if not target_path.is_relative_to(base_dir):
            raise HTTPException(status_code=400, detail="Invalid path")
        if target_path.exists() and target_path.is_file():
            target_path.unlink()
