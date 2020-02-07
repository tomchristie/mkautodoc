from xml import etree
from xml.dom import minidom
import textwrap


def assert_xml_equal(xml_string, expected_xml_string):
    """
    Assert equality of two xml strings, particularly that the contents of
    each string have the same elements, with the same attributes (e.g. class,
    text) and the same non-xml string contents
    """
    # this prints a human-formatted string of what the test passed in -- useful
    # if you need to modify test expectations after you've modified
    # a rendering and tested it visually
    print(to_readable_error_output(xml_string))

    assert_elements_equal(
        etree.ElementTree.fromstring(tostring(xml_string)),
        etree.ElementTree.fromstring(tostring(expected_xml_string)),
    )


def assert_elements_equal(element, reference_element):
    """
    Assert, recursively, the equality of two etree objects.
    """
    assert (
        element.text == reference_element.text
    ), f"Text doesn't match: {element.text} =/= {reference_element.text}."
    assert (
        element.attrib == reference_element.attrib
    ), f"Attrib doesn't match: {element.attrib} =/= {reference_element.attrib}"
    assert len(element) == len(
        reference_element
    ), f"Expected {len(reference_element)} children but got {len(element)}"
    for sub_element, reference_sub_element in zip(element, reference_element):
        assert_elements_equal(sub_element, reference_sub_element)


def tostring(xml_string):
    """
    Wraps `xml_string` in a div so it can be rendered, even if it has multiple roots.
    """
    return remove_indents(f"<div>{remove_indents(xml_string)}</div>").encode("utf-8")


def to_readable_error_output(xml_string):
    return textwrap.dedent(
        "\n".join(
            minidom.parseString(tostring(xml_string))
            .toprettyxml(indent="  ")
            .split("\n")[2:-2]  # remove xml declaration and div added by `tostring`
        )
    )  # dent by "  "


def remove_indents(html):
    """
    Remove leading whitespace from a string

    e.g.
        input:                    output:
        . <div>                   . <div>
        .    <p>Some Text</p>     . <p>Some Text</p>
        .    <div>                . <div>
        .      Some more text     . Some more text
        .    </div>               . </div>
        . </div>                  . </div>
    """
    lines = [el.lstrip() for el in html.split("\n")]
    return "".join([el for el in lines if el or el != "\n"])
