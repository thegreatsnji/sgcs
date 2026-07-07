"""Serviços de gestão de ficheiros."""


class FileStorageService:
    @staticmethod
    def build_upload_path(category: str, filename: str) -> str:
        return f"{category}/{filename}"
