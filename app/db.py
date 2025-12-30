import os
from sqlmodel import SQLModel, create_engine


def _normalize_db_url(url: str) -> str:
	# Some platforms use postgres:// but SQLAlchemy expects postgresql://
	if url.startswith("postgres://"):
		return url.replace("postgres://", "postgresql://", 1)
	return url


def get_engine():
	url = os.getenv("DATABASE_URL")

	# Local fallback if not set, or if Railway internal hostname is present
	if (not url) or ("railway.internal" in url):
		return create_engine("sqlite:///./dev.db", echo=False)

	url = _normalize_db_url(url)
	return create_engine(url, pool_pre_ping=True)


def init_db(engine):
	SQLModel.metadata.create_all(engine)
