from datetime import (
    datetime,
)
from functools import (
    partial,
)
from typing import (
    Any,
    Callable,
    Dict,
    Iterable,
    Iterator,
    Optional,
    Union,
)

from .helpers import (
    with_server_timezone,
)


SimpleValue = Union[str, int, None]

GetterFunction = Callable[
    [
        Dict[str, Any],
    ],
    Any,
]


def simple_simplifyer(value: Any) -> SimpleValue:
    if not (value is None
            or isinstance(value, (int, str))):
        value = str(value)

    return value


def create_datetime_getter(
        attr_name: str,
        func: Callable[[datetime], Any],
        use_server_timezone: bool = True,
) -> GetterFunction:

    def datetime_getter(raw_object: Dict[str, Any]):
        value = raw_object[attr_name]
        assert isinstance(value, datetime)

        if use_server_timezone:
            value = with_server_timezone(value)

        return func(value)

    return datetime_getter


def create_datetime_as_str_getter(
        attr_name: str,
        fmt: str,
        use_server_timezone: bool = True,
) -> GetterFunction:
    return create_datetime_getter(
        attr_name=attr_name,
        func=partial(datetime.strftime, format=fmt),
        use_server_timezone=use_server_timezone,
    )


class OutAttrBuilder:
    def __init__(
            self,
            attr_name: str,
            getter_func: Optional[GetterFunction] = None,
    ) -> None:
        self.attr_name: str = attr_name
        self.getter_func: GetterFunction

        if getter_func is None:
            def default_getter_func(
                    raw_values_dict: Dict[str, Any],
            ) -> Union[int, SimpleValue]:
                return simple_simplifyer(
                    raw_values_dict[attr_name])

            self.getter_func = default_getter_func

        else:
            self.getter_func = getter_func


OutAttrsBuilders = Optional[Iterable[OutAttrBuilder]]


class ExtractParams:
    def __init__(
            self,
            model,
            raw_values: Optional[Iterable[str]] = None,
            out_attrs_builders: OutAttrsBuilders = None,
    ):
        self.model = model
        self.raw_values = raw_values or tuple()
        self.out_attrs_builders = out_attrs_builders


def prepare_object(
        raw_object: Dict[str, Any],
        out_attrs_builders: OutAttrsBuilders = None,
) -> Dict[str, SimpleValue]:
    prepared_object: dict
    if out_attrs_builders is None:
        prepared_object = {
            attr: simple_simplifyer(value)
            for attr, value in raw_object.items()
        }
    else:
        prepared_object = {
            builder.attr_name: builder.getter_func(raw_object)
            for builder in out_attrs_builders
        }

    return prepared_object


def prepare_objects(
        raw_objects: Iterable[Dict[str, Any]],
        out_attrs_builders: OutAttrsBuilders = None,
) -> Iterator[Dict[str, SimpleValue]]:
    return (
        prepare_object(obj, out_attrs_builders)
        for obj in raw_objects
    )
