# MkAutoDoc

Python API documention for MkDocs.

This markdown extension adds `autodoc` style support, for use with MkDocs.

![aIAgAAjQpG](https://user-images.githubusercontent.com/647359/66651320-a276ff80-ec2a-11e9-9cec-9eba425d5304.gif)

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

#### 4. Optionally, add styling for the API docs

Update your `mkdocs.yml` to include some custom CSS.

```yaml
[...]
extra_css:
    - css/custom.css
```

Then add a `css/custom.css` file to your documentation.

```css
div.autodoc-docstring {
  padding-left: 20px;
  margin-bottom: 30px;
  border-left: 5px solid rgba(230, 230, 230);
}

div.autodoc-members {
  padding-left: 20px;
  margin-bottom: 15px;
}
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
