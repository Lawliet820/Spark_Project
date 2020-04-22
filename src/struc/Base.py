from dataclasses import dataclass, field
from sqlalchemy.orm.collections import InstrumentedList

noDefault = object()


def duck_check(obj, clses):
    """
    check obj is instance of clses,
    clses can be a set of class or one class
    """

    if isinstance(clses, tuple):
        for cls in clses:
            try:
                cls._check(obj)
                return True
            except Exception:
                continue
        return False
    else:
        try:
            clses._check(obj)
        except Exception:
            return False
    return True


class AttributesTypeError(Exception):
    """
    this Attributes Type is Error
    """

    def __init__(self, cls, attr_name, target_recive_type, recived_type):
        self.cls = cls
        self.attr_name = attr_name
        self.target_recive_type = target_recive_type
        self.recived_type = recived_type

    def __str__(self):
        return "attr <{}> of class {} should recive type is {} but recived type is {}".format(
            str(self.attr_name),
            str(self.cls),
            str(self.target_recive_type),
            str(self.recived_type),
        )


class NoFallbackFound(Exception):
    """
    obj has no fallback
    """

    def __init__(self, cls, attr_name, value, target_recive_type, recived_type):
        self.cls = cls
        self.attr_name = attr_name
        self.value = value
        self.target_recive_type = target_recive_type
        self.recived_type = recived_type

    def __str__(self):
        return "attr <{}> of class {} recived {}, should recive type is {} but recived type is {}".format(
            str(self.attr_name),
            str(self.cls),
            str(self.value),
            str(self.target_recive_type),
            str(self.recived_type),
        )


class Structure(object):
    """
        base class for structures
    """

    def __post_init__(self, *args, **kwargs):
        self.__class__._check(self)

    @classmethod
    def _check(cls, obj):
        for k, field in cls.__dataclass_fields__.items():
            if hasattr(obj, k):
                obj_attr = getattr(obj, k)
                if obj_attr is noDefault:
                    raise TypeError(f"__init__ missing 1 required argument: '{k}'")
                if field.type == list and type(obj_attr) == InstrumentedList:
                    continue
                if obj_attr and type(obj_attr) != field.type:
                    if not hasattr(cls, "fallback"):
                        raise NoFallbackFound(
                            cls, k, obj_attr, field.type, type(obj_attr)
                        )
                    fallbacked_obj_attr = cls.fallback(k, obj_attr)
                    if type(fallbacked_obj_attr) != field.type:
                        raise AttributesTypeError(cls, k, field.type, type(obj_attr))
                    else:
                        setattr(obj, k, fallbacked_obj_attr)
            else:
                raise AttributesTypeError(cls, k, field.type, None)

    @classmethod
    def verify(cls, func, *args, **kwargs):
        def wrapper(*args, **kwargs):
            output = func(*args, **kwargs)
            cls._check(output)
            return output

        return wrapper

    @classmethod
    def verifys_all(cls, func, *args, **kwargs):
        def wrapper(*args, **kwargs):
            outputs = func(*args, **kwargs)
            checked_outputs = []
            for output in outputs:
                cls._check(output)
                checked_outputs.append(output)
            return checked_outputs

        return wrapper
