# MkAutoDoc

Python API documention for MkDocs.

This markdown extension adds `autodoc` style support, for use with MkDocs.

## Usage

#### 1. Include the extension in you `mkdocs.yml` config file:

```yaml
[...]
markdown_extensions:
  - admonition
  - codehilite
  - mkautodoc
```

#### 2. Ensure the library you want to document is importable.

This will depend on how your documentation building is setup, but
you may need to use `pip install -e .` or modify `PYTHONPATH` in your docs build script.

#### 3. Use the `:::` block syntax to add autodoc blocks to your documentation.

```markdown
# API documentation

::: my_library.some_function
    :docstring:

::: my_library.SomeClass
    :docstring:
    :members:
```

## Notes

#### The :docstring: declaration.

Renders the docstring of the associated function, method, or class.

#### The `:members:` declaration.

Renders documentation for member attributes of the associated class.
Currently handles methods and properties.
Instance attributes set during `__init__` are not currently recognised.

May optionally accept a list of member attributes that should be documented. For example:

```markdown
::: my_library.SomeClass
    :docstring:
    :members: currency vat_registered calculate_expenses
```
