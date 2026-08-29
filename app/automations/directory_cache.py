from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String

class DirectorySizeCache(db.Model):
    __tablename__ = "cache"

    full_path: Mapped[str] = mapped_column(primary_key = True)
    name: Mapped[str]
    size: Mapped[int]
    mtime: Mapped[float]
    is_dir: Mapped[bool]
    parent_path: Mapped[str]