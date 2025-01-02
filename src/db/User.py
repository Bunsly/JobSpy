from datetime import datetime
from typing import Optional, Union

from pydantic import BaseModel

from db.Position import Position


class User(BaseModel):
    full_name: str
    username: str
    chat_id: Union[int,str]
    field: Optional[Position] = None
