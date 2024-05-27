from typing import Optional, Union
from uuid import UUID


def validate_int(
    value, min_value=None, max_value=None, required=False
) -> Optional[int]:
    if value is None:
        if required:
            raise ValueError("required integer parameter missing")
        else:
            return value
    if not isinstance(value, int):
        raise TypeError(f"{repr(value)} is not an integer")
    if min_value and value < min_value:
        raise ValueError(f"{value} shouldn't be lower than {min_value}")
    if max_value and value > max_value:
        raise ValueError(f"{value} shouldn't be higher than {max_value}")
    return value


def validate_class(value, class_type):
    if not isinstance(value, class_type):
        raise TypeError(f"{repr(value)} is not an instance of {class_type.__name__}")
    return value


def validate_uuid(uuid: Union[UUID, str]) -> str:
    try:
        if isinstance(uuid, str):
            return str(UUID(uuid))

        if isinstance(uuid, UUID):
            return str(uuid)

        raise TypeError
    except (ValueError, TypeError) as ex:
        ex.args = (f"{repr(uuid)} is not a valid UUID",)
        raise ex
