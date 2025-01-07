from typing import Optional, Union

from pydantic import BaseModel

from model.Position import Position


class User(BaseModel):
    full_name: str
    username: str
    chat_id: Union[int, str] = None
    experience: Union[int, str] = None
    job_age: Union[int, str] = None
    position: Optional[Position] = None
    country: Optional[str] = "Israel"
    cities: Optional[list[str]] = None
    title_filters: Optional[list[str]] = None

    def get_myinfo_message(self):
        message = "Here's your profile:\n\n"
        message += f"Full Name: {self.full_name}\n"
        message += f"Username: @{self.username}\n"
        if self.chat_id:
            message += f"Chat ID: {self.chat_id}\n"
        if self.job_age:
            message += f"Job Age (Hours): {self.experience}\n"
        if self.experience:
            message += f"Experience(Years): {self.experience}\n"
        if self.position:
            message += f"Position Level: {self.position.value}\n"
        if self.cities:
            message += f"Preferred Cities: {', '.join(self.cities)}\n"
        if self.title_filters:
            message += f"Job Title Filters: {', '.join(self.title_filters)}\n"
        return message