"""
    Copyright (c) 2007-2019 by the Sphinx team (see
    https://github.com/sphinx-doc/sphinx/blob/v2.4.3/sphinx/util/typing.py
    for more details).

    All rights reserved.

    Redistribution and use in source and binary forms, with or without
    modification, are permitted provided that the following conditions are
    met:

    * Redistributions of source code must retain the above copyright
      notice, this list of conditions and the following disclaimer.

    * Redistributions in binary form must reproduce the above copyright
      notice, this list of conditions and the following disclaimer in the
      documentation and/or other materials provided with the distribution.

    THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
    "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
    LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
    A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
    HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
    SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
    LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
    DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
    THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
    (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
    OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

import sys
import typing
from typing import Any, TypeVar

# type of None
NoneType = type(None)


def stringify(annotation: Any) -> str:
    """Stringify type annotation object."""
    if isinstance(annotation, str):
        return annotation
    elif isinstance(annotation, TypeVar):  # type: ignore
        return annotation.__name__
    elif not annotation:
        return repr(annotation)
    elif annotation is NoneType:  # type: ignore
        return "None"
    elif getattr(annotation, "__module__", None) == "builtins" and hasattr(
        annotation, "__qualname__"
    ):
        return annotation.__qualname__
    elif annotation is Ellipsis:
        return "..."

    if sys.version_info >= (3, 7):  # py37+
        return _stringify_py37(annotation)
    else:
        return _stringify_py36(annotation)


def _stringify_py37(annotation: Any) -> str:
    """stringify() for py37+."""
    module = getattr(annotation, "__module__", None)
    if module == "typing":
        if getattr(annotation, "_name", None):
            qualname = annotation._name
        elif getattr(annotation, "__qualname__", None):
            qualname = annotation.__qualname__
        elif getattr(annotation, "__forward_arg__", None):
            qualname = annotation.__forward_arg__
        else:
            qualname = stringify(annotation.__origin__)  # ex. Union
    elif hasattr(annotation, "__qualname__"):
        qualname = "%s.%s" % (module, annotation.__qualname__)
    else:
        qualname = repr(annotation)

    if getattr(annotation, "__args__", None):
        if qualname == "Union":
            if len(annotation.__args__) == 2 and annotation.__args__[1] is NoneType:  # type: ignore  # NOQA
                return "Optional[%s]" % stringify(annotation.__args__[0])
            else:
                args = ", ".join(stringify(a) for a in annotation.__args__)
                return "%s[%s]" % (qualname, args)
        elif qualname == "Callable":
            args = ", ".join(stringify(a) for a in annotation.__args__[:-1])
            returns = stringify(annotation.__args__[-1])
            return "%s[[%s], %s]" % (qualname, args, returns)
        elif str(annotation).startswith("typing.Annotated"):  # for py39+
            return stringify(annotation.__args__[0])
        elif annotation._special:
            return qualname
        else:
            args = ", ".join(stringify(a) for a in annotation.__args__)
            return "%s[%s]" % (qualname, args)

    return qualname


def _stringify_py36(annotation: Any) -> str:
    """stringify() for py35 and py36."""
    module = getattr(annotation, "__module__", None)
    if module == "typing":
        if getattr(annotation, "_name", None):
            qualname = annotation._name
        elif getattr(annotation, "__qualname__", None):
            qualname = annotation.__qualname__
        elif getattr(annotation, "__forward_arg__", None):
            qualname = annotation.__forward_arg__
        elif getattr(annotation, "__origin__", None):
            qualname = stringify(annotation.__origin__)  # ex. Union
        else:
            qualname = repr(annotation).replace("typing.", "")
    elif hasattr(annotation, "__qualname__"):
        qualname = "%s.%s" % (module, annotation.__qualname__)
    else:
        qualname = repr(annotation)

    if isinstance(annotation, typing.TupleMeta) and not hasattr(  # type: ignore
        annotation, "__tuple_params__"
    ):  # for Python 3.6
        params = annotation.__args__
        if params:
            param_str = ", ".join(stringify(p) for p in params)
            return "%s[%s]" % (qualname, param_str)
        else:
            return qualname
    elif isinstance(annotation, typing.GenericMeta):
        params = None
        if hasattr(annotation, "__args__"):
            # for Python 3.5.2+
            if annotation.__args__ is None or len(annotation.__args__) <= 2:  # type: ignore  # NOQA
                params = annotation.__args__  # type: ignore
            else:  # typing.Callable
                args = ", ".join(
                    stringify(arg) for arg in annotation.__args__[:-1]
                )  # type: ignore
                result = stringify(annotation.__args__[-1])  # type: ignore
                return "%s[[%s], %s]" % (qualname, args, result)
        elif hasattr(annotation, "__parameters__"):
            # for Python 3.5.0 and 3.5.1
            params = annotation.__parameters__  # type: ignore
        if params is not None:
            param_str = ", ".join(stringify(p) for p in params)
            return "%s[%s]" % (qualname, param_str)
    elif (
        hasattr(typing, "UnionMeta")
        and isinstance(annotation, typing.UnionMeta)
        and hasattr(annotation, "__union_params__")  # type: ignore
    ):  # for Python 3.5
        params = annotation.__union_params__
        if params is not None:
            if len(params) == 2 and params[1] is NoneType:  # type: ignore
                return "Optional[%s]" % stringify(params[0])
            else:
                param_str = ", ".join(stringify(p) for p in params)
                return "%s[%s]" % (qualname, param_str)
    elif (
        hasattr(annotation, "__origin__") and annotation.__origin__ is typing.Union
    ):  # for Python 3.5.2+
        params = annotation.__args__
        if params is not None:
            if len(params) == 2 and params[1] is NoneType:  # type: ignore
                return "Optional[%s]" % stringify(params[0])
            else:
                param_str = ", ".join(stringify(p) for p in params)
                return "Union[%s]" % param_str
    elif (
        isinstance(annotation, typing.CallableMeta)
        and getattr(annotation, "__args__", None) is not None  # type: ignore
        and hasattr(annotation, "__result__")
    ):  # for Python 3.5
        # Skipped in the case of plain typing.Callable
        args = annotation.__args__
        if args is None:
            return qualname
        elif args is Ellipsis:
            args_str = "..."
        else:
            formatted_args = (stringify(a) for a in args)
            args_str = "[%s]" % ", ".join(formatted_args)
        return "%s[%s, %s]" % (qualname, args_str, stringify(annotation.__result__))
    elif (
        isinstance(annotation, typing.TupleMeta)
        and hasattr(annotation, "__tuple_params__")  # type: ignore
        and hasattr(annotation, "__tuple_use_ellipsis__")
    ):  # for Python 3.5
        params = annotation.__tuple_params__
        if params is not None:
            param_strings = [stringify(p) for p in params]
            if annotation.__tuple_use_ellipsis__:
                param_strings.append("...")
            return "%s[%s]" % (qualname, ", ".join(param_strings))

    return qualname
