from typing import Dict, List


def example_function(a, b=None, *args, **kwargs):
    """
    This is a function with a *docstring*.
    """


def annotated_function(
    a: int, b: List[Dict[str, float]] = None, *args, **kwargs
) -> bool:
    """
    This function has annotations.
    """


class ExampleClass:
    """
    This is a class with a *docstring*.
    """

    def __init__(self):
        """
        This is an __init__ with a *docstring*.
        """

    def example_method(self, a, b=None):
        """
        This is a method with a *docstring*.
        """

    @property
    def example_property(self):
        """
        This is a property with a *docstring*.
        """


async def example_async_function():
    """
    This is a coroutine function as can be seen by the *async* keyword.
    """
