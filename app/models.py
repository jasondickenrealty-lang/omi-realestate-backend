from typing import Optional
from sqlmodel import SQLModel, Field
import time


class Client(SQLModel, table=True):
	id: Optional[int] = Field(default=None, primary_key=True)
	name: Optional[str] = None
	phone: Optional[str] = None
	email: Optional[str] = None
	created_ts: int = Field(default_factory=lambda: int(time.time()))


class Session(SQLModel, table=True):
	session_id: str = Field(primary_key=True)
	client_id: Optional[int] = Field(default=None, index=True)
	address: str
	lat: Optional[float] = None
	lng: Optional[float] = None
	started_ts: int = Field(default_factory=lambda: int(time.time()))
	ended_ts: Optional[int] = None
	device_id: Optional[str] = Field(default=None, index=True)
	is_active: bool = Field(default=False, index=True)


class Message(SQLModel, table=True):
	id: Optional[int] = Field(default=None, primary_key=True)
	session_id: str = Field(index=True)
	ts: int = Field(default_factory=lambda: int(time.time()), index=True)
	speaker: str
	text: str


# Tracks which device is currently active for a session
class ActiveSession(SQLModel, table=True):
    device_id: str = Field(primary_key=True)
    session_id: str
    updated_ts: int = Field(default_factory=lambda: int(time.time()), index=True)
