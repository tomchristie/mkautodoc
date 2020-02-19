import markdown
from .assertions import assert_xml_equal


def test_docstring():
    content = """
# Example

::: mocklib.example_function
    :docstring:
"""
    output = markdown.markdown(content, extensions=["mkautodoc"])
    assert_xml_equal(
        output,
        """\
<h1>Example</h1>
<div class="autodoc">
  <div class="autodoc-signature">
    <code>
      mocklib.
      <strong>example_function</strong>
    </code>
    <span class="autodoc-punctuation">(</span>
    <span class="autodoc-param-definition">
      <em class="autodoc-param autodoc-param-name">a</em>
      <span class="autodoc-punctuation">, </span>
    </span>
    <span class="autodoc-param-definition">
      <em class="autodoc-param autodoc-param-name">b</em>
      <span class="autodoc-punctuation">=</span>
      <span class="autodoc-param-default">None</span>
      <span class="autodoc-punctuation">, </span>
    </span>
    <span class="autodoc-param-definition">
      <em class="autodoc-param autodoc-param-name">*args</em>
      <span class="autodoc-punctuation">, </span>
    </span>
    <span class="autodoc-param-definition">
      <em class="autodoc-param autodoc-param-name">**kwargs</em>
    </span>
    <span class="autodoc-punctuation">)</span>
  </div>
  <div class="autodoc-docstring">
    <p>
      This is a function with a <em>docstring</em>.
    </p>
  </div>
</div>""",
    )


def test_async_function():
    content = """
::: mocklib.example_async_function
"""
    output = markdown.markdown(content, extensions=["mkautodoc"])
    assert_xml_equal(
        output,
        """\
<div class="autodoc">
  <div class="autodoc-signature">
    <em class="autodoc-qualifier">async </em>
    <code>
      mocklib.
      <strong>example_async_function</strong>
    </code>
    <span class="autodoc-punctuation">(</span>
    <span class="autodoc-punctuation">)</span>
  </div>
</div>""",
    )


def test_members():
    content = """
# Example

::: mocklib.ExampleClass
    :docstring:
    :members:
"""
    output = markdown.markdown(content, extensions=["mkautodoc"])
    assert_xml_equal(
        output,
        """\
<h1>Example</h1>
<div class="autodoc">
  <div class="autodoc-signature">
    <em class="autodoc-qualifier">class </em>
    <code>
      mocklib.
      <strong>ExampleClass</strong>
    </code>
    <span class="autodoc-punctuation">(</span>
    <span class="autodoc-punctuation">)</span>
  </div>
  <div class="autodoc-docstring">
    <p>
      This is a class with a <em>docstring</em>.
    </p>
  </div>
  <div class="autodoc-members">
    <div class="autodoc-signature">
      <code>
        <strong>example_method</strong>
      </code>
      <span class="autodoc-punctuation">(</span>
      <span class="autodoc-param-definition">
        <em class="autodoc-param autodoc-param-name">self</em>
        <span class="autodoc-punctuation">, </span>
      </span>
      <span class="autodoc-param-definition">
        <em class="autodoc-param autodoc-param-name">a</em>
        <span class="autodoc-punctuation">, </span>
      </span>
      <span class="autodoc-param-definition">
        <em class="autodoc-param autodoc-param-name">b</em>
        <span class="autodoc-punctuation">=</span>
        <span class="autodoc-param-default">None</span>
      </span>
      <span class="autodoc-punctuation">)</span>
    </div>
    <div class="autodoc-docstring">
      <p>
        This is a method with a <em>docstring</em>.
      </p>
    </div>
    <div class="autodoc-signature">
      <code>
        <strong>example_property</strong>
      </code>
    </div>
    <div class="autodoc-docstring">
      <p>
        This is a property with a <em>docstring</em>.
      </p>
    </div>
  </div>
</div>""",
    )
