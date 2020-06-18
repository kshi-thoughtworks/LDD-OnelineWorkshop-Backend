from dataclasses import field, MISSING
from typing import List

from marshmallow_dataclass import dataclass

import marshmallow.validate

from workshop.enums import Element_type


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


@dataclass
class UpdateWorkbench:
    name: str = field(metadata={"validate": marshmallow.validate.Length(min=1, max=20)})
    description: str = field(metadata={"validate": marshmallow.validate.Length(min=0, max=200)})


@dataclass
class CreateElement:
    type: str = field(init=False,default=Element_type.STICKY)
    content: str = field(metadata={"validate": marshmallow.validate.Length(min=0, max=1024)})
    step_id: int = field()
    card_id: int = field(default=None)
    # save properties, like: rotate, scale, color, length
    meta: dict = field(default=None)


@dataclass
class UpdateElement:
    content: str = field(metadata={"validate": marshmallow.validate.Length(min=0, max=1024)})
    meta: dict = field(default=None)


@dataclass
class AddUsers:
    user_ids: List[int] = field()
