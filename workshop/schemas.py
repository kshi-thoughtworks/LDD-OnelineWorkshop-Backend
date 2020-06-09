from dataclasses import field

from marshmallow_dataclass import dataclass

import marshmallow.validate


@dataclass
class CreateUser:
    username: str = field(metadata={"validate": marshmallow.validate.Length(min=4, max=20)})
    email: str = field(metadata={"validate": marshmallow.validate.Email()})
    password: str = field(metadata={"validate": marshmallow.validate.Length(min=6, max=20)})


@dataclass
class LoginUser:
    username: str = field()
    password: str = field()
