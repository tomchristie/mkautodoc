import markdown
from .assertions import assert_xml_equal


def test_annotated_function():
    content = """
# Example

::: mocklib.annotated_function
    :docstring:
"""
    output = markdown.markdown(content, extensions=["mkautodoc"])
    assert_xml_equal(
        output,
        """\
<h1>Example</h1>
<div class="autodoc">
  <div class="autodoc-signature autodoc-signature__long">
    <code>
      mocklib.
      <strong>annotated_function</strong>
    </code>
    <span class="autodoc-punctuation">(</span>
    <span class="autodoc-param-definition">
      <em class="autodoc-param autodoc-param-name">a</em>
      <span class="autodoc-punctuation">: </span>
      <span class="autodoc-type-annotation">int</span>
      <span class="autodoc-punctuation">, </span>
    </span>
    <span class="autodoc-param-definition">
      <em class="autodoc-param autodoc-param-name">b</em>
      <span class="autodoc-punctuation">: </span>
      <span class="autodoc-type-annotation">List[Dict[str, float]]</span>
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
    <span class="autdoc-punctuation"> -&gt; </span>
    <span class="autodoc-type-annotation">bool</span>
  </div>
  <div class="autodoc-docstring">
    <p>This function has annotations.</p>
  </div>
</div>""",
    )
