import markdown


def test_docstring():
    content = """
# Example

::: mocklib.example_function
    :docstring:
"""
    output = markdown.markdown(content, extensions=["mkautodoc"])
    assert output.splitlines() == [
        "<h1>Example</h1>",
        '<div class="autodoc">',
        '<p class="autodoc-signature"><code>mocklib.<strong>example_function</strong></code><span class="autodoc-punctuation">(</span><em class="autodoc-param">a</em><span class="autodoc-punctuation">, </span><em class="autodoc-param">b=None</em><span class="autodoc-punctuation">, </span><em class="autodoc-param">*args</em><span class="autodoc-punctuation">, </span><em class="autodoc-param">**kwargs</em><span class="autodoc-punctuation">)</span></p>',
        '<dd class="autodoc-docstring"><p>This is a function with a <em>docstring</em>.</p></dd>',
        "</div>",
    ]


def test_members():
    content = """
# Example

::: mocklib.ExampleClass
    :docstring:
    :members:
"""
    output = markdown.markdown(content, extensions=["mkautodoc"])
    assert output.splitlines() == [
        "<h1>Example</h1>",
        '<div class="autodoc">',
        '<p class="autodoc-signature"><em>class </em><code>mocklib.<strong>ExampleClass</strong></code><span class="autodoc-punctuation">(</span><span class="autodoc-punctuation">)</span></p>',
        '<dd class="autodoc-docstring"><p>This is a class with a <em>docstring</em>.</p></dd>',
        '<div class="autodoc-members">',
        '<p class="autodoc-signature"><code><strong>example_method</strong></code><span class="autodoc-punctuation">(</span><em class="autodoc-param">self</em><span class="autodoc-punctuation">, </span><em class="autodoc-param">a</em><span class="autodoc-punctuation">, </span><em class="autodoc-param">b=None</em><span class="autodoc-punctuation">)</span></p>',
        '<dd class="autodoc-docstring"><p>This is a method with a <em>docstring</em>.</p></dd>',
        '<p class="autodoc-signature"><code><strong>example_property</strong></code></p>',
        '<dd class="autodoc-docstring"><p>This is a property with a <em>docstring</em>.</p></dd>',
        "</div>",
        "</div>",
    ]
