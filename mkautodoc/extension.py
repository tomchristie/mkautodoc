from markdown import Markdown
from markdown.extensions import Extension
from markdown.blockprocessors import BlockProcessor
from markdown.util import etree
import importlib
import inspect
import re
import typing


# Fuzzy regex for determining source lines in __init__ that look like
# attribute assignments.  Eg. `self.counter = 0`
SET_ATTRIBUTE = re.compile(r"^(?:[ \t]*)self[.]([A-Za-z0-9_]+) *=")

# Fuzzy regex for a doc comment, e.g. `#: This is a comment`.
DOC_COMMENT = re.compile(r"(?:[ \t]*)#: (.*)")


def import_from_string(import_str: str) -> typing.Any:
    module_str, _, attr_str = import_str.rpartition(".")

    try:
        module = importlib.import_module(module_str)
    except ImportError as exc:
        module_name = module_str.split(".", 1)[0]
        if exc.name != module_name:
            raise exc from None
        raise ValueError(f"Could not import module {module_str!r}.")

    try:
        return getattr(module, attr_str)
    except AttributeError as exc:
        raise ValueError(f"Attribute {attr_str!r} not found in module {module_str!r}.")


def get_params(signature: inspect.Signature) -> typing.List[str]:
    """
    Given a function signature, return a list of parameter strings
    to use in documentation.

    Eg. test(a, b=None, **kwargs) -> ['a', 'b=None', '**kwargs']
    """
    params = []
    render_pos_only_separator = True
    render_kw_only_separator = True

    for parameter in signature.parameters.values():
        value = parameter.name
        if parameter.default is not parameter.empty:
            value = f"{value}={parameter.default!r}"

        if parameter.kind is parameter.VAR_POSITIONAL:
            render_kw_only_separator = False
            value = f"*{value}"
        elif parameter.kind is parameter.VAR_KEYWORD:
            value = f"**{value}"
        elif parameter.kind is parameter.POSITIONAL_ONLY:
            if render_pos_only_separator:
                render_pos_only_separator = False
                params.append("/")
        elif parameter.kind is parameter.KEYWORD_ONLY:
            if render_kw_only_separator:
                render_kw_only_separator = False
                params.append("*")
        params.append(value)

    return params


def last_iter(seq: typing.Sequence) -> typing.Iterator:
    """
    Given an sequence, return a two-tuple (item, is_last) iterable.

    See: https://stackoverflow.com/a/1633483/596689
    """
    it = iter(seq)
    item = next(it)
    is_last = False

    for next_item in it:
        yield item, is_last
        item = next_item

    is_last = True
    yield item, is_last


def trim_docstring(docstring: typing.Optional[str]) -> str:
    """
    Trim leading indent from a docstring.

    See: https://www.python.org/dev/peps/pep-0257/#handling-docstring-indentation
    """
    if not docstring:
        return ""

    # Convert tabs to spaces (following the normal Python rules)
    # and split into a list of lines:
    lines = docstring.expandtabs().splitlines()
    # Determine minimum indentation (first line doesn't count):
    indent = 1000
    for line in lines[1:]:
        stripped = line.lstrip()
        if stripped:
            indent = min(indent, len(line) - len(stripped))

    # Remove indentation (first line is special):
    trimmed = [lines[0].strip()]
    if indent < 1000:
        for line in lines[1:]:
            trimmed.append(line[indent:].rstrip())

    # Strip off trailing and leading blank lines:
    while trimmed and not trimmed[-1]:
        trimmed.pop()
    while trimmed and not trimmed[0]:
        trimmed.pop(0)

    # Return a single string:
    return "\n".join(trimmed)


def is_private(identifier: str) -> bool:
    return identifier.startswith("_")


def find_instance_attributes(cls: typing.Type) -> typing.List[typing.Tuple[str, str]]:
    """
    Given a class, return a list of (name, description) tuples for its instance attributes.
    
    * Name is inferred from statements in the form of 'self.<name> = ...'.
    * Description comes from an optional block of '#: ...' comments above the attribute definition.
    """
    attributes = []
    lines, _ = inspect.getsourcelines(cls.__init__)
    description_comments: typing.List[str] = []

    for index, line in enumerate(lines):
        stripped = line.strip()

        m = DOC_COMMENT.match(stripped)
        if m:
            comment = m.group(1)
            description_comments.append(comment)
            continue

        m = SET_ATTRIBUTE.match(stripped)
        if m:
            name = m.group(1)
            description = " ".join(description_comments)
            description_comments = []
            if not is_private(name):
                attributes.append((name, description))
        else:
            description_comments = []

    return attributes


class AutoDocProcessor(BlockProcessor):

    CLASSNAME = "autodoc"
    RE = re.compile(r"(?:^|\n)::: ?([:a-zA-Z0-9_.]*) *(?:\n|$)")
    RE_SPACES = re.compile("  +")

    def __init__(self, parser, md=None):
        super().__init__(parser=parser)
        self.md = md

    def test(self, parent: etree.Element, block: etree.Element) -> bool:
        sibling = self.lastChild(parent)
        return bool(
            self.RE.search(block)
            or (
                block.startswith(" " * self.tab_length)
                and sibling is not None
                and sibling.get("class", "").find(self.CLASSNAME) != -1
            )
        )

    def run(self, parent: etree.Element, blocks: etree.Element) -> None:
        sibling = self.lastChild(parent)
        block = blocks.pop(0)
        m = self.RE.search(block)

        if m:
            block = block[m.end() :]  # removes the first line

        block, theRest = self.detab(block)

        if m:
            import_string = m.group(1)
            item = import_from_string(import_string)

            autodoc_div = etree.SubElement(parent, "div")
            autodoc_div.set("class", self.CLASSNAME)

            self.render_signature(autodoc_div, item, import_string)
            for line in block.splitlines():
                if line.startswith(":docstring:"):
                    docstring = trim_docstring(item.__doc__)
                    self.render_docstring(autodoc_div, item, docstring)
                elif line.startswith(":members:"):
                    members = line.split()[1:] or None
                    self.render_members(autodoc_div, item, members=members)

        if theRest:
            # This block contained unindented line(s) after the first indented
            # line. Insert these lines as the first block of the master blocks
            # list for future processing.
            blocks.insert(0, theRest)

    def render_instance_attributes(self, elem: etree.Element, cls: typing.Type) -> None:
        for name, description in find_instance_attributes(cls):
            attribute_elem = etree.SubElement(elem, "div")
            attribute_elem.set("class", "autodoc-signature")

            name_elem = etree.SubElement(attribute_elem, "code")
            main_name_elem = etree.SubElement(name_elem, "strong")
            main_name_elem.text = name

            description_elem = etree.SubElement(attribute_elem, "div")
            description_elem.set("class", "autodoc-docstring")

            md = Markdown(extensions=self.md.registeredExtensions)
            description_elem.text = md.convert(description)

    def render_signature(
        self, elem: etree.Element, item: typing.Any, import_string: str
    ) -> None:
        module_string, _, name_string = import_string.rpartition(".")

        # Eg: `some_module.attribute_name`
        signature_elem = etree.SubElement(elem, "div")
        signature_elem.set("class", "autodoc-signature")

        if inspect.isclass(item):
            qualifier_elem = etree.SubElement(signature_elem, "em")
            qualifier_elem.text = "class "

        name_elem = etree.SubElement(signature_elem, "code")
        if module_string:
            name_elem.text = module_string + "."
        main_name_elem = etree.SubElement(name_elem, "strong")
        main_name_elem.text = name_string

        # If this is a property, then we're done.
        if not callable(item):
            return

        # Eg: `(a, b='default', **kwargs)``
        signature = inspect.signature(item)

        bracket_elem = etree.SubElement(signature_elem, "span")
        bracket_elem.text = "("
        bracket_elem.set("class", "autodoc-punctuation")

        if signature.parameters:
            for param, is_last in last_iter(get_params(signature)):
                param_elem = etree.SubElement(signature_elem, "em")
                param_elem.text = param
                param_elem.set("class", "autodoc-param")

                if not is_last:
                    comma_elem = etree.SubElement(signature_elem, "span")
                    comma_elem.text = ", "
                    comma_elem.set("class", "autodoc-punctuation")

        bracket_elem = etree.SubElement(signature_elem, "span")
        bracket_elem.text = ")"
        bracket_elem.set("class", "autodoc-punctuation")

    def render_docstring(
        self, elem: etree.Element, item: typing.Any, docstring: str
    ) -> None:
        docstring_elem = etree.SubElement(elem, "div")
        docstring_elem.set("class", "autodoc-docstring")

        md = Markdown(extensions=self.md.registeredExtensions)
        docstring_elem.text = md.convert(docstring)

    def render_members(
        self, elem: etree.Element, item: typing.Any, members: typing.List[str] = None
    ) -> None:
        members_elem = etree.SubElement(elem, "div")
        members_elem.set("class", "autodoc-members")

        if inspect.isclass(item):
            self.render_instance_attributes(members_elem, item)

        if members is None:
            members = sorted([attr for attr in dir(item) if not is_private(attr)])

        info_items = []
        for attribute_name in members:
            attribute = getattr(item, attribute_name)
            docs = trim_docstring(getattr(attribute, "__doc__", ""))
            info = (attribute_name, docs)
            info_items.append(info)

        for attribute_name, docs in info_items:
            attribute = getattr(item, attribute_name)
            self.render_signature(members_elem, attribute, attribute_name)
            self.render_docstring(members_elem, attribute, docs)


class MKAutoDocExtension(Extension):
    def extendMarkdown(self, md: Markdown) -> None:
        md.registerExtension(self)
        processor = AutoDocProcessor(md.parser, md=md)
        md.parser.blockprocessors.register(processor, "mkautodoc", 110)


def makeExtension():
    return MKAutoDocExtension()
