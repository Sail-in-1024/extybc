
__version__ = '1.0.0a1'

import sys
import types
import collections
import re


# types.SimpleNamespace
# ---------------------

class SimpleNamespace:
    """
    An external Implementation of types.SimpleNamespace. 

    The code is from https://docs.python.org/zh-cn/3.15/library/types.html#types.SimpleNamespace. 
    """

    # The code in SimpleNamespace is from https://docs.python.org/zh-cn/3.15/library/types.html#types.SimpleNamespace

    def __init__(self, mapping_or_iterable=(), **kwargs):
        self.__dict__.update(mapping_or_iterable)
        self.__dict__.update(kwargs)

    def __repr__(self):
        items = (f"{k}={v!r}" for k, v in self.__dict__.items())
        return "{}({})".format(type(self).__name__, ", ".join(items))

    def __eq__(self, other):
        if isinstance(self, SimpleNamespace) and isinstance(other, SimpleNamespace):
           return self.__dict__ == other.__dict__
        return NotImplemented

types.SimpleNamespace = SimpleNamespace
del SimpleNamespace

# builtins
# --------

builtins = types.ModuleType(
    'builtins', 

    """
    Built-in functions, types, exceptions, and other objects.

    This module provides direct access to all 'built-in'
    identifiers of Python; for example, builtins.len is
    the full name for the built-in function len().

    This module is not normally accessed explicitly by most
    applications, but can be useful in modules that provide
    objects with the same name as a built-in value, but in
    which the built-in of that name is also needed.
    """
)

sys.modules['builtins'] = builtins

class builtin_function_or_method:

    __module__ = 'builtins'
    
    def __call__(self, *args, **kwargs):
        return self._func(*args, **kwargs)

    def __init__(self, func, name=None):
        self._func = func
        if name is None:
            self.__name__ = name
        else:
            self.__name__ = self
    
    def __repr__(self):
        return f'<built-in function {self.__name__}>'

def _builtin(func_or_name):
    if callable(func_or_name):
        return builtin_function_or_method(func_or_name)
    else:
        def wrapper(func):
            return builtin_function_or_method(func, func_or_name)
        return wrapper

_old = types.SimpleNamespace(
                            isinstance = isinstance,
                            issubclass = issubclass,
                            print = print,
                            str = str,
                            type = type,
                            )

class bytearray:

    def __init__(self, source=None, encoding=None, errors=None):
        pass

@_builtin
def isinstance(__object: object, __classinfo: 'typing.Union[type, Tuple[type]]') -> bool:
    """
    Return whether an object is an instance of a class or of a subclass thereof.

    A tuple, as in ``isinstance(x, (A, B, ...))``, may be given as the target to
    check against. This is equivalent to ``isinstance(x, A) or isinstance(x, B)
    or ...`` etc.
    """
    meta = type(__classinfo)
    if type.__instancecheck__(type, meta):
        if hasattr(meta, '__instancecheck__'):
            return bool(meta.__instancecheck__(__classinfo, __object))
        else:
            for subclass in __classinfo.__subclasses__():
                if issubclass(objtype, subclass):
                    return True
            return False
    elif type.__instancecheck__(tuple, meta):
        for per_classinfo in __classinfo:
            return isinstance(__object, per_classinfo)
    else:
        raise TypeError('isinstance() arg 2 must be a type, a tuple of types, or a union')

@_builtin
def issubclass(__class: type, __classinfo: type) -> bool:
    __classmeta = type(__classinfo)
    if hasattr(__classmeta, '__subclasscheck__'):
        return bool(__classmeta.__subclasscheck__(__classinfo, __class))
    else:
        return _old.issubclass

@_builtin
def print(*objects, sep=' ', end='\n', file=sys.stdout, flush=False):
    if file is None:
        file = sys.stdout
    content = sep.join(map(str, objects)) + end
    file.write(content)

class type(type):
    
    def __init__(self, name, bases, namespace):
        _old.type.__init__(self, name, bases, namespace)
        self._direct_subclasses_ = []

    def __instancecheck__(cls, instance):
        objtype = type(instance)
        if objtype == cls:
            return True
        else:
            for subclass in cls.__subclasses__():
                if issubclass(objtype, subclass):
                    return True
                return False
    
    def __subclasses__(cls=type):
        return cls._direct_subclasses_

class object(metaclass=type):
    ...

class str(object, str):
    ...

_new = types.SimpleNamespace(
                            isinstance = isinstance,
                            issubclass = issubclass,
                            print = print,
                            str = str,
                            type = type,
                            )

def _init(_old=_old, _new=_new):
    print('WARNING: 当前模块（__main__）下的部分内置函数将被替换，替换内容详见源文件')
    main_mod = sys.modules['__main__']
    for key, val in _new.__dict__.items():
        setattr(main_mod, key, val)
    main_mod._old = _old
    main_mod._new = _new

# sys
# ---

sys.__doc__ = """
This module provides access to some objects used or maintained by the
interpreter and to functions that interact strongly with the interpreter.
"""

def getsizeof(__object, __default=None):
    if hasattr(__object, '__sizeof__'):
        size = __object.__sizeof__()
        if isinstance(size, int):
            return size
        else:
            raise TypeError('an integer is required')
    elif __default is not None:
        return __default
    else:
        raise TypeError(f'{__object!r} object is not size-calculatable')

@_builtin
def displayhook(value):
    # 
    if value is None:
        return
    # 将 '_' 设为 None 以避免继续递归
    builtins._ = None
    text = repr(value)
    try:
        sys.stdout.write(text)
    except UnicodeEncodeError:
        bytes = text.encode(sys.stdout.encoding, 'backslashreplace')
        if hasattr(sys.stdout, 'buffer'):
            sys.stdout.buffer.write(bytes)
        else:
            text = bytes.decode(sys.stdout.encoding, 'strict')
            sys.stdout.write(text)
    sys.stdout.write("\n")
    builtins._ = value

sys.__displayhook__ = displayhook
sys.displayhook = sys.__displayhook__

# abc
# ---

abc = types.ModuleType('abc', 'Abstract Base Classes (ABCs) according to PEP 3119.')

class ABCMeta(object, metaclass=type):

    """
    Helper class that provides a standard way to create an ABC using
inheritance.
    """

    def __init__(cls, name, bases, namespace):
        cls._registered_subclasses: list = []

    def __subclasshook__(cls, subclass):
        for registered_subclass in cls._registered_subclasses:
            ...

    def register(cls, subclass):
        """
        Register a virtual subclass of an ABC.

        Returns the subclass, to allow usage as a class decorator.
        """
        if isinstance(subclass, type):
            cls._registered_subclasses.append(subclass)
        else:
            raise TypeError('Can only register classes')

abc.ABCMeta = ABCMeta
del ABCMeta

_new._modules = types.SimpleNamespace(
                                        abc = abc,
                                        )

__all__ = ('_init', '_new', '_old') +  tuple(_new.__dict__.items())

print('欢迎使用 extybc')

del builtin_function_or_method
del _builtin

if __name__ == '__main__':
    MyABC = abc.ABCMeta('MyABC', (), {})
    MyABC.register(bytearray)
    print(isinstance(bytearray, MyABC))