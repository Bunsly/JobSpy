from typing import Optional, Union

from pydantic import BaseModel, Field

from model.Position import Position


class User(BaseModel):
    full_name: str
    username: str
    chat_id: Union[int, str] = None
    field: Optional[Position] = None
