from typing import Optional, Iterable, Callable, Union
from dataclasses import fields
from functools import update_wrapper


def protect_attributes(cls: type):
    """
    Decorator to protect attributes of <dataclasses.dataclass> classes.
    To make this work, assign one of the following metadata values on fields that need protection:
    * `noset` if True will prevent the field from being assigned to in `__setattr__`
    * `nodel` if True will prevent the field from being deleted in `__delattr__`
    * `readonly` is same as setting both `noset` and `nodel` to True.

    Examples:
        @dataclass
        @protect_attributes
        class Person(object):
            id: str = field(metadata={'readonly': True})
            passport_no: str = field(metadata={'nodel': True})
            name: str

        p = Person(id="1234", passport_no="AB12345", name="John Doe")
        p.name = "John Wick"        # succeeds
        p.id = "4567"               # fails
        del p.id                    # fails
        p.passport_no = "AB54321"   # succeeds
        del p.passport_no           # fails

    Args:
        cls: the class to intrument

    Returns: the altered class

    """
    # update post_init method
    def make_post_init(cls: type, method: Callable):
        def post_init(self, *args, **kwargs):
            # populate set of attributes to not set
            noset = set([f.name for f in fields(self) if
                         f.metadata.get("readonly", False) or f.metadata.get("noset", False)])
            if noset:
                self._readonlyattr_noset = noset

            # populate set of attributes to not delete
            nodel = set([f.name for f in fields(self) if
                         f.metadata.get("readonly", False) or f.metadata.get("nodel", False)])
            if nodel:
                self._readonlyattr_nodel = nodel

            # call pre-existing or superclass post_init method of wrapped class
            if method:
                method(self, *args, **kwargs)
            elif hasattr(super(cls, self), "__post_init__"):
                super(cls, self).__post_init__(*args, **kwargs)

        return post_init

    setattr(cls, "__post_init__", make_post_init(cls, getattr(cls, "__post_init__", None)))

    # update setattr method
    def make_setattr(cls: type, method: Callable):
        def new_setattr(self, key, value):
            if "_readonlyattr_noset" not in self.__dict__:
                if method:
                    method(self, key, value)
                else:
                    super(cls, self).__setattr__(key, value)
            elif key in self._readonlyattr_noset:
                raise AttributeError(f'Attribute {key} is protected and cannot be set')
            else:
                if method:
                    method(self, key, value)
                else:
                    super(cls, self).__setattr__(key, value)

        return new_setattr

    setattr(cls, "__setattr__", make_setattr(cls, getattr(cls, "__setattr__", None)))

    # update delattr method
    def make_delattr(cls: type, method: Callable):
        def new_delattr(self, key):
            if "_readonlyattr_nodel" not in self.__dict__:
                if method:
                    method(self, key)
                else:
                    super(cls, self).__delattr__(key)
            elif key in self._readonlyattr_nodel:
                raise AttributeError(f'Attribute {key} is protected and cannot be deleted')
            else:
                if method:
                    method(self, key)
                else:
                    super(cls, self).__delattr__(key)

        return new_delattr

    setattr(cls, "__delattr__", make_delattr(cls, getattr(cls, "__delattr__", None)))

    update_wrapper(protect_attributes, cls)
    return cls
