from typing import Optional
from pydantic import BaseModel

class UserProfile(BaseModel):
    name: str
    age: int
    email: str
    gender: str
    mobile_number: str
    birthday: str
    city: str
    state: str
    country: str
    address1:Optional[str] = None
    address2:Optional[str] = None