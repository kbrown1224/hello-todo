from pydantic import BaseModel
from ormar import Model


def snake_to_camel(value: str) -> str:
    words = value.split("_")
    first_word = words.pop(0)
    words = [word.title() for word in words]
    words = [first_word] + words

    return "".join(words)


class PydanticBaseModel(BaseModel):
    class Config:
        alias_generator = snake_to_camel
        allow_population_by_field_name = True

    @classmethod
    def from_dict(cls, data):
        return cls(**data)


class OrmarBaseModel(Model):
    class Config:
        alias_generator = snake_to_camel
        allow_population_by_field_name = True
        orm_mode = True
