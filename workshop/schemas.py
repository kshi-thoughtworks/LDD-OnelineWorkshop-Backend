from dataclasses import field
from typing import List

from marshmallow_dataclass import dataclass

import marshmallow.validate


@dataclass
class CreateUser:
    username: str = field(metadata={"validate": marshmallow.validate.Length(min=4, max=20)})
    email: str = field(metadata={"validate": marshmallow.validate.Email()})
    password: str = field(metadata={"validate": marshmallow.validate.Length(min=6, max=20)})


@dataclass
class LoginUser:
    name_or_email: str = field()
    password: str = field()


@dataclass
class CreateWorkbench:
    name: str = field(metadata={"validate": marshmallow.validate.Length(min=1, max=20)})
    description: str = field(metadata={"validate": marshmallow.validate.Length(min=0, max=200)})
    workshop_id: int = field()


@dataclass
class UpdateWorkbench:
    name: str = field(metadata={"validate": marshmallow.validate.Length(min=1, max=20)})
    description: str = field(metadata={"validate": marshmallow.validate.Length(min=0, max=200)})


@dataclass
class AddUsers:
    user_ids: List[int] = field()
