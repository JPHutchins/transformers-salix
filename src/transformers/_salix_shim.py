import dataclasses
from typing import Any, Callable, TypeVar

from salix import Struct

_T = TypeVar("_T")


def is_struct(cls_or_instance: Any) -> bool:
    cls = cls_or_instance if isinstance(cls_or_instance, type) else type(cls_or_instance)
    return hasattr(cls, "__struct_fields__")


def is_dataclass(obj: Any) -> bool:
    return dataclasses.is_dataclass(obj) or is_struct(obj)


def fields(cls: type[_T]) -> tuple[dataclasses.Field[Any], ...]:
    if not is_struct(cls):
        return dataclasses.fields(cls)
    names = cls.__struct_fields__
    annotations = cls.__struct_annotations__
    extras = cls.__struct_metadata__
    defaults = cls.__struct_defaults__
    missing = len(names) - len(defaults)
    result = []
    for position, name in enumerate(names):
        field = dataclasses.Field(
            dataclasses.MISSING if position < missing else defaults[position - missing],
            dataclasses.MISSING,
            True,
            True,
            None,
            True,
            {} if not extras[position] else {"extras": extras[position]},
            False,
        )
        field.name = name
        field.type = annotations[position]
        result.append(field)
    return tuple(result)


def asdict(obj: Any) -> dict[str, Any]:
    if not is_struct(obj):
        return dataclasses.asdict(obj)
    return {name: getattr(obj, name) for name in type(obj).__struct_fields__}


def replace(obj: _T, /, **changes: Any) -> _T:
    if is_struct(obj):
        from salix import replace as salix_replace

        return salix_replace(obj, **changes)
    return dataclasses.replace(obj, **changes)


_MISSING = dataclasses.MISSING
_Field = dataclasses.Field
field = dataclasses.field
make_dataclass = dataclasses.make_dataclass


def dataclass(
    _cls: type[_T] | None = None,
    *,
    init: bool = True,
    repr: bool = True,
    eq: bool = True,
    order: bool = False,
    unsafe_hash: bool = False,
    frozen: bool = False,
    match_args: bool = True,
    kw_only: bool = False,
    slots: bool = False,
    weakref_slot: bool = False,
) -> Callable[[type[_T]], type[_T]] | type[_T]:
    def wrap(cls: type[_T]) -> type[_T]:
        if not init:
            raise NotImplementedError(f"init=False is not shimmed yet: {cls.__name__}")
        if kw_only:
            raise NotImplementedError(f"kw_only=True is not shimmed yet: {cls.__name__}")
        namespace: dict[str, Any] = {}
        for name, value in cls.__dict__.items():
            if isinstance(value, _Field):
                if value.init is False:
                    raise NotImplementedError(f"init=False is not shimmed yet: {cls.__name__}.{name}")
                if value.kw_only:
                    raise NotImplementedError(f"kw_only is not shimmed yet: {cls.__name__}.{name}")
                if value.metadata:
                    raise NotImplementedError(f"field metadata is not shimmed yet: {cls.__name__}.{name}")
                if value.default is not _MISSING:
                    namespace[name] = value.default
                elif value.default_factory is not _MISSING:
                    namespace[name] = value.default_factory()
                else:
                    namespace.pop(name, None)
            else:
                namespace[name] = value
        return type(cls)(cls.__name__, (Struct, *cls.__bases__), namespace)

    if _cls is None:
        return wrap
    return wrap(_cls)
