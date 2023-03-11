import pytest

from thsl.src.grammar import TokenType
from thsl.src.lexer import Lexer, Token


@pytest.fixture
def lexer():
    return Lexer("test")


@pytest.mark.parametrize(
    ("config", "expected_key"),
    (
        ("my_value @int: 1\n", "my_value"),
        ("'my_value' @int: 1\n", "my_value"),
        ('"my_value" @int: 1\n', "my_value"),
        ("' my_value' @int: 1\n", " my_value"),
        ('" my_value" @int: 1\n', " my_value"),
        ("' my_value ' @int: 1\n", " my_value "),
        ('" my_value " @int: 1\n', " my_value "),
        ("'my_value ' @int: 1\n", "my_value "),
        ('"my_value " @int: 1\n', "my_value "),
        ("int @int: 1\n", "int"),
        ("'int' @int: 1\n", "int"),
        ('"int" @int: 1\n', "int"),
        ("' int' @int: 1\n", " int"),
        ('" int" @int: 1\n', " int"),
        ("' int ' @int: 1\n", " int "),
        ('" int " @int: 1\n', " int "),
        ("'int ' @int: 1\n", "int "),
        ('"int " @int: 1\n', "int "),
        ("1 @int: 1\n", "1"),
        ("1hi @int: 1\n", "1hi"),
    ),
)
def test_key(lexer, config, expected_key):
    lexer.text = config
    expected = Token(
        type=TokenType.KEY,
        value=expected_key,
        line=1,
        indent=0,
    )
    actual = lexer.parse()
    assert actual[0] == expected


@pytest.mark.parametrize(
    ("config",),
    (
        ("my_value @int: 1\n",),
        ("my_value   @int: 1\n",),
        ("my_value   @int:   1\n",),
        ("my_value   @int  :   1\n",),
        ("my_value @int : 1\n",),
        ("my_value @int  1\n",),
        ("my_value @int    1\n",),
        ("my_value   @int    1\n",),
        ("'my_value' @int: 1\n",),
        ('"my_value" @int: 1\n',),
        ("' my_value' @int: 1\n",),
        ('" my_value" @int: 1\n',),
        ("' my_value ' @int: 1\n",),
        ('" my_value " @int: 1\n',),
        ("'my_value ' @int: 1\n",),
        ('"my_value " @int: 1\n',),
        ("int @int: 1\n",),
        ("'int' @int: 1\n",),
        ('"int" @int: 1\n',),
        ("' int' @int: 1\n",),
        ('" int" @int: 1\n',),
        ("' int ' @int: 1\n",),
        ('" int " @int: 1\n',),
        ("'int ' @int: 1\n",),
        ('"int " @int: 1\n',),
    ),
)
def test_type(lexer, config):
    lexer.text = config
    expected = Token(
        type=TokenType.TYPE,
        value="int",
        line=1,
        indent=0,
    )
    actual = lexer.parse()
    assert actual[1] == expected


@pytest.mark.parametrize(
    ("config", "expected_key", "index"),
    (
        ("my_value @bytes: 1110101\n", "1110101", 2),
        ("my_value @bytes  1110101\n", "1110101", 2),
        ("my_value @bytes    1110101\n", "1110101", 2),
        ("my_value @bytes: 1110101 # comment\n", "1110101", 2),
        ("my_value @int: 1\n", "1", 2),
        ("my_value @int: '1'\n", "1", 2),
        ('my_value @int: "1"\n', "1", 2),
        ("my_value @int: -1\n", "-1", 2),
        ("my_value @int: 100_000_000\n", "100000000", 2),
        ("my_value @float: 1\n", "1", 2),
        ("my_value @float: 1.000_000_000\n", "1.000000000", 2),
        ("my_value @float: 1.0\n", "1.0", 2),
        ("my_value @float: -1.0\n", "-1.0", 2),
        ("my_value @float: 1.3e-4\n", "1.3e-4", 2),
        ("my_value @dec: 4\n", "4", 2),
        ("my_value @dec: 1.000_000_000\n", "1.000000000", 2),
        ("my_value @dec: 1.0\n", "1.0", 2),
        ("my_value @dec: -1.0\n", "-1.0", 2),
        ("my_value @dec: 1.3e-4\n", "1.3e-4", 2),
        ("my_value @complex: 3-2i\n", "3-2i", 2),
        ("my_value @hex: deadbeef\n", "deadbeef", 2),
        ("my_value @oct: 7\n", "7", 2),
        ("my_value @char: a\n", "a", 2),
        (
            "my_value @str: Hello my name is Frank Drebin\n",
            "Hello my name is Frank Drebin",
            2,
        ),
        (
            "my_value @str: 'Hello my name is Frank Drebin'\n",
            "Hello my name is Frank Drebin",
            2,
        ),
        (
            'my_value @str: "Hello my name is Frank Drebin"\n',
            "Hello my name is Frank Drebin",
            2,
        ),
        (
            'my_value @str: " Hello my name is Frank Drebin"\n',
            " Hello my name is Frank Drebin",
            2,
        ),
        (
            'my_value @str: " Hello my name is Frank Drebin "\n',
            " Hello my name is Frank Drebin ",
            2,
        ),
        (
            'my_value @str: "Hello my name is Frank Drebin "\n',
            "Hello my name is Frank Drebin ",
            2,
        ),
        (
            """my_value @str: "This
string is
    on multiple
         lines.
"
""",
            "This\nstring is\n    on multiple\n         lines.\n",
            2,
        ),
        # (
        #     'my_value @str: escaping\\n new line\n',
        #     "escaping\n new line",
        #     2
        # ),
        (
            "my_value @base64: VGhlIFNwYW5pc2ggSW5xdWlzaXRpb24h\n",
            "VGhlIFNwYW5pc2ggSW5xdWlzaXRpb24h",
            2,
        ),
        (
            "my_value @base64e: Encode this string to base64\n",
            "Encode this string to base64",
            2,
        ),
        ("my_value @date: 1986-02-10\n", "1986-02-10", 2),
        ("my_value @datetime: 2020-01-01 12:00:00 -6\n", "2020-01-01 12:00:00 -6", 2),
        ("my_value @interval: 1 hour\n", "1 hour", 2),
        ("my_value @ip: 192.168.1.1\n", "192.168.1.1", 2),
        (
            "my_value @url: http://www.example.com/index.html\n",
            "http://www.example.com/index.html",
            2,
        ),
        ("my_value @env: PATH\n", "PATH", 2),
        ("my_value @bool: false\n", "false", 2),
        ("my_value @bool: true\n", "true", 2),
        ("my_value @float: inf\n", "inf", 2),
        ("my_value @float: -inf\n", "-inf", 2),
        ("my_value @float: nan\n", "nan", 2),
        ("my_value @dec: inf\n", "inf", 2),
        ("my_value @dec: -inf\n", "-inf", 2),
        ("my_value @dec: nan\n", "nan", 2),
    ),
)
def test_value(lexer, config, expected_key, index):
    lexer.text = config
    expected = Token(
        type=TokenType.VALUE,
        value=expected_key,
        line=1,
        indent=0,
    )
    actual = lexer.parse()
    expected.line = actual[index].line
    assert actual[index] == expected


def test_nesting(lexer):
    lexer.text = "graphics:\n\ttarget_framerate @int: 60\n"
    expected = [
        Token(type=TokenType.KEY, value="graphics", line=1, indent=0),
        Token(type=TokenType.TYPE, value="unknown", line=1, indent=0),
        Token(type=TokenType.NEWLINE, value="\n", line=1, indent=0),
        Token(type=TokenType.KEY, value="target_framerate", line=2, indent=1),
        Token(type=TokenType.TYPE, value="int", line=2, indent=1),
        Token(type=TokenType.VALUE, value="60", line=2, indent=1),
        Token(type=TokenType.NEWLINE, value="\n", line=2, indent=1),
        Token(type=TokenType.EOF, value="EOF", line=3, indent=0),
    ]
    actual = lexer.parse()
    assert actual == expected


def test_list(lexer):
    lexer.text = "my_list @int:  # comment\n\t- 1\n\t- 2\n\t- 4\n\t- 7\n"
    expected = [
        Token(type=TokenType.KEY, value="my_list", line=1, indent=0),
        Token(type=TokenType.TYPE, value="int", line=1, indent=0),
        Token(type=TokenType.NEWLINE, value="\n", line=1, indent=0),
        Token(type=TokenType.OPERATOR, value="-", line=2, indent=1),
        Token(type=TokenType.VALUE, value="1", line=2, indent=1),
        Token(type=TokenType.NEWLINE, value="\n", line=2, indent=1),
        Token(type=TokenType.OPERATOR, value="-", line=3, indent=1),
        Token(type=TokenType.VALUE, value="2", line=3, indent=1),
        Token(type=TokenType.NEWLINE, value="\n", line=3, indent=1),
        Token(type=TokenType.OPERATOR, value="-", line=4, indent=1),
        Token(type=TokenType.VALUE, value="4", line=4, indent=1),
        Token(type=TokenType.NEWLINE, value="\n", line=4, indent=1),
        Token(type=TokenType.OPERATOR, value="-", line=5, indent=1),
        Token(type=TokenType.VALUE, value="7", line=5, indent=1),
        Token(type=TokenType.NEWLINE, value="\n", line=5, indent=1),
        Token(type=TokenType.EOF, value="EOF", line=6, indent=0),
    ]
    actual = lexer.parse()
    assert actual == expected


def test_one_line_list(lexer):
    lexer.text = "my_list @int: [1, 2, 3,]\n"
    expected = [
        Token(type=TokenType.KEY, value="my_list", line=1, indent=0),
        Token(type=TokenType.TYPE, value="int", line=1, indent=0),
        Token(type=TokenType.OPERATOR, value="[", line=1, indent=0),
        Token(type=TokenType.VALUE, value="1", line=1, indent=0),
        Token(type=TokenType.OPERATOR, value=",", line=1, indent=0),
        Token(type=TokenType.VALUE, value="2", line=1, indent=0),
        Token(type=TokenType.OPERATOR, value=",", line=1, indent=0),
        Token(type=TokenType.VALUE, value="3", line=1, indent=0),
        Token(type=TokenType.OPERATOR, value=",", line=1, indent=0),
        Token(type=TokenType.OPERATOR, value="]", line=1, indent=0),
        Token(type=TokenType.NEWLINE, value="\n", line=1, indent=0),
        Token(type=TokenType.EOF, value="EOF", line=2, indent=0),
    ]
    actual = lexer.parse()
    assert actual == expected


def test_list_heterogeneous(lexer):
    lexer.text = (
        "my_list:\n\t- @int: 1\n\t- @float: 3.14159\n\t- @dec: 2.11\n\t- @str: hello\n"
    )
    expected = [
        Token(type=TokenType.KEY, value="my_list", line=1, indent=0),
        Token(type=TokenType.TYPE, value="unknown", line=1, indent=0),
        Token(type=TokenType.NEWLINE, value="\n", line=1, indent=0),
        Token(type=TokenType.OPERATOR, value="-", line=2, indent=1),
        Token(type=TokenType.TYPE, value="int", line=2, indent=1),
        Token(type=TokenType.VALUE, value="1", line=2, indent=1),
        Token(type=TokenType.NEWLINE, value="\n", line=2, indent=1),
        Token(type=TokenType.OPERATOR, value="-", line=3, indent=1),
        Token(type=TokenType.TYPE, value="float", line=3, indent=1),
        Token(type=TokenType.VALUE, value="3.14159", line=3, indent=1),
        Token(type=TokenType.NEWLINE, value="\n", line=3, indent=1),
        Token(type=TokenType.OPERATOR, value="-", line=4, indent=1),
        Token(type=TokenType.TYPE, value="dec", line=4, indent=1),
        Token(type=TokenType.VALUE, value="2.11", line=4, indent=1),
        Token(type=TokenType.NEWLINE, value="\n", line=4, indent=1),
        Token(type=TokenType.OPERATOR, value="-", line=5, indent=1),
        Token(type=TokenType.TYPE, value="str", line=5, indent=1),
        Token(type=TokenType.VALUE, value="hello", line=5, indent=1),
        Token(type=TokenType.NEWLINE, value="\n", line=5, indent=1),
        Token(type=TokenType.EOF, value="EOF", line=6, indent=0),
    ]
    actual = lexer.parse()
    assert actual == expected


def test_list_of_dicts(lexer):
    lexer.text = "my_list:\n\t- {one @int: 1}\n\t- {two @float: 2}\n"
    expected = [
        Token(type=TokenType.KEY, value="my_list", line=1, indent=0),
        Token(type=TokenType.TYPE, value="unknown", line=1, indent=0),
        Token(type=TokenType.NEWLINE, value="\n", line=1, indent=0),
        Token(type=TokenType.OPERATOR, value="-", line=2, indent=1),
        Token(type=TokenType.OPERATOR, value="{", line=2, indent=1),
        Token(type=TokenType.KEY, value="one", line=2, indent=1),
        Token(type=TokenType.TYPE, value="int", line=2, indent=1),
        Token(type=TokenType.VALUE, value="1", line=2, indent=1),
        Token(type=TokenType.OPERATOR, value="}", line=2, indent=1),
        Token(type=TokenType.NEWLINE, value="\n", line=2, indent=1),
        Token(type=TokenType.OPERATOR, value="-", line=3, indent=1),
        Token(type=TokenType.OPERATOR, value="{", line=3, indent=1),
        Token(type=TokenType.KEY, value="two", line=3, indent=1),
        Token(type=TokenType.TYPE, value="float", line=3, indent=1),
        Token(type=TokenType.VALUE, value="2", line=3, indent=1),
        Token(type=TokenType.OPERATOR, value="}", line=3, indent=1),
        Token(type=TokenType.NEWLINE, value="\n", line=3, indent=1),
        Token(type=TokenType.EOF, value="EOF", line=4, indent=0),
    ]
    actual = lexer.parse()
    assert actual == expected


def test_list_of_dicts_multiline(lexer):
    lexer.text = (
        "my_list:\n\t-\n\t\tone @int: 1\n\t\ttwo @float: 2\n\t-\n\t\tthree @int: 3"
        "\n\t\tfour @int: 4\n"
    )
    expected = [
        Token(type=TokenType.KEY, value="my_list", line=1, indent=0),
        Token(type=TokenType.TYPE, value="unknown", line=1, indent=0),
        Token(type=TokenType.NEWLINE, value="\n", line=1, indent=0),
        Token(type=TokenType.OPERATOR, value="-", line=2, indent=1),
        Token(type=TokenType.TYPE, value="unknown", line=2, indent=1),
        Token(type=TokenType.NEWLINE, value="\n", line=2, indent=1),
        Token(type=TokenType.KEY, value="one", line=3, indent=2),
        Token(type=TokenType.TYPE, value="int", line=3, indent=2),
        Token(type=TokenType.VALUE, value="1", line=3, indent=2),
        Token(type=TokenType.NEWLINE, value="\n", line=3, indent=2),
        Token(type=TokenType.KEY, value="two", line=4, indent=2),
        Token(type=TokenType.TYPE, value="float", line=4, indent=2),
        Token(type=TokenType.VALUE, value="2", line=4, indent=2),
        Token(type=TokenType.NEWLINE, value="\n", line=4, indent=2),
        Token(type=TokenType.OPERATOR, value="-", line=5, indent=1),
        Token(type=TokenType.TYPE, value="unknown", line=5, indent=1),
        Token(type=TokenType.NEWLINE, value="\n", line=5, indent=1),
        Token(type=TokenType.KEY, value="three", line=6, indent=2),
        Token(type=TokenType.TYPE, value="int", line=6, indent=2),
        Token(type=TokenType.VALUE, value="3", line=6, indent=2),
        Token(type=TokenType.NEWLINE, value="\n", line=6, indent=2),
        Token(type=TokenType.KEY, value="four", line=7, indent=2),
        Token(type=TokenType.TYPE, value="int", line=7, indent=2),
        Token(type=TokenType.VALUE, value="4", line=7, indent=2),
        Token(type=TokenType.NEWLINE, value="\n", line=7, indent=2),
        Token(type=TokenType.EOF, value="EOF", line=8, indent=0),
    ]
    actual = lexer.parse()
    assert actual == expected


def test_one_line_dict(lexer):
    lexer.text = "my_dict: {one @int: 1, two @float: 2}\n"
    expected = [
        Token(type=TokenType.KEY, value="my_dict", line=1, indent=0),
        Token(type=TokenType.OPERATOR, value="{", line=1, indent=0),
        Token(type=TokenType.KEY, value="one", line=1, indent=0),
        Token(type=TokenType.TYPE, value="int", line=1, indent=0),
        Token(type=TokenType.VALUE, value="1", line=1, indent=0),
        Token(type=TokenType.OPERATOR, value=",", line=1, indent=0),
        Token(type=TokenType.KEY, value="two", line=1, indent=0),
        Token(type=TokenType.TYPE, value="float", line=1, indent=0),
        Token(type=TokenType.VALUE, value="2", line=1, indent=0),
        Token(type=TokenType.OPERATOR, value="}", line=1, indent=0),
        Token(type=TokenType.NEWLINE, value="\n", line=1, indent=0),
        Token(type=TokenType.EOF, value="EOF", line=2, indent=0),
    ]
    actual = lexer.parse()
    assert actual == expected


def test_set(lexer):
    lexer.text = "my_set @int:\n\t> 1\n\t> 2\n\t> 4\n\t> 7\n"
    expected = [
        Token(type=TokenType.KEY, value="my_set", line=1, indent=0),
        Token(type=TokenType.TYPE, value="int", line=1, indent=0),
        Token(type=TokenType.NEWLINE, value="\n", line=1, indent=0),
        Token(type=TokenType.OPERATOR, value=">", line=2, indent=1),
        Token(type=TokenType.VALUE, value="1", line=2, indent=1),
        Token(type=TokenType.NEWLINE, value="\n", line=2, indent=1),
        Token(type=TokenType.OPERATOR, value=">", line=3, indent=1),
        Token(type=TokenType.VALUE, value="2", line=3, indent=1),
        Token(type=TokenType.NEWLINE, value="\n", line=3, indent=1),
        Token(type=TokenType.OPERATOR, value=">", line=4, indent=1),
        Token(type=TokenType.VALUE, value="4", line=4, indent=1),
        Token(type=TokenType.NEWLINE, value="\n", line=4, indent=1),
        Token(type=TokenType.OPERATOR, value=">", line=5, indent=1),
        Token(type=TokenType.VALUE, value="7", line=5, indent=1),
        Token(type=TokenType.NEWLINE, value="\n", line=5, indent=1),
        Token(type=TokenType.EOF, value="EOF", line=6, indent=0),
    ]
    actual = lexer.parse()
    assert actual == expected


def test_tuple(lexer):
    lexer.text = "my_tuple @int:\n\t) 1\n\t) 2\n\t) 4\n\t) 7\n"
    expected = [
        Token(type=TokenType.KEY, value="my_tuple", line=1, indent=0),
        Token(type=TokenType.TYPE, value="int", line=1, indent=0),
        Token(type=TokenType.NEWLINE, value="\n", line=1, indent=0),
        Token(type=TokenType.OPERATOR, value=")", line=2, indent=1),
        Token(type=TokenType.VALUE, value="1", line=2, indent=1),
        Token(type=TokenType.NEWLINE, value="\n", line=2, indent=1),
        Token(type=TokenType.OPERATOR, value=")", line=3, indent=1),
        Token(type=TokenType.VALUE, value="2", line=3, indent=1),
        Token(type=TokenType.NEWLINE, value="\n", line=3, indent=1),
        Token(type=TokenType.OPERATOR, value=")", line=4, indent=1),
        Token(type=TokenType.VALUE, value="4", line=4, indent=1),
        Token(type=TokenType.NEWLINE, value="\n", line=4, indent=1),
        Token(type=TokenType.OPERATOR, value=")", line=5, indent=1),
        Token(type=TokenType.VALUE, value="7", line=5, indent=1),
        Token(type=TokenType.NEWLINE, value="\n", line=5, indent=1),
        Token(type=TokenType.EOF, value="EOF", line=6, indent=0),
    ]
    actual = lexer.parse()
    assert actual == expected


def test_tokenization(lexer):
    lexer.text = "my_value @bool: false\n"
    expected = [
        Token(type=TokenType.KEY, value="my_value", line=1, indent=0),
        Token(type=TokenType.TYPE, value="bool", line=1, indent=0),
        Token(type=TokenType.VALUE, value="false", line=1, indent=0),
        Token(type=TokenType.NEWLINE, value="\n", line=1, indent=0),
        Token(type=TokenType.EOF, value="EOF", line=2, indent=0),
    ]
    actual = lexer.parse()
    assert actual == expected


def test_multi_heterogeneous_list(lexer):
    lexer.text = (
        "languages:\n\tpython:\n\t\tformatter:\n\t\t\targs:\n\t\t\t\t- @str format"
        '\n\t\t\t\t- @str "-q"\n\t\t\t\t- @str "-q"\n'
    )
    expected = [
        Token(type=TokenType.KEY, value="languages", line=1, indent=0),
        Token(type=TokenType.TYPE, value="unknown", line=1, indent=0),
        Token(type=TokenType.NEWLINE, value="\n", line=1, indent=0),
        Token(type=TokenType.KEY, value="python", line=2, indent=1),
        Token(type=TokenType.TYPE, value="unknown", line=2, indent=1),
        Token(type=TokenType.NEWLINE, value="\n", line=2, indent=1),
        Token(type=TokenType.KEY, value="formatter", line=3, indent=2),
        Token(type=TokenType.TYPE, value="unknown", line=3, indent=2),
        Token(type=TokenType.NEWLINE, value="\n", line=3, indent=2),
        Token(type=TokenType.KEY, value="args", line=4, indent=3),
        Token(type=TokenType.TYPE, value="unknown", line=4, indent=3),
        Token(type=TokenType.NEWLINE, value="\n", line=4, indent=3),
        Token(type=TokenType.OPERATOR, value="-", line=5, indent=4),
        Token(type=TokenType.TYPE, value="str", line=5, indent=4),
        Token(type=TokenType.VALUE, value="format", line=5, indent=4),
        Token(type=TokenType.NEWLINE, value="\n", line=5, indent=4),
        Token(type=TokenType.OPERATOR, value="-", line=6, indent=4),
        Token(type=TokenType.TYPE, value="str", line=6, indent=4),
        Token(type=TokenType.VALUE, value="-q", line=6, indent=4),
        Token(type=TokenType.NEWLINE, value="\n", line=6, indent=4),
        Token(type=TokenType.OPERATOR, value="-", line=7, indent=4),
        Token(type=TokenType.TYPE, value="str", line=7, indent=4),
        Token(type=TokenType.VALUE, value="-q", line=7, indent=4),
        Token(type=TokenType.NEWLINE, value="\n", line=7, indent=4),
        Token(type=TokenType.EOF, value="EOF", line=8, indent=0),
    ]
    actual = lexer.parse()
    assert actual == expected


def test_multi_homogeneous_list(lexer):
    lexer.text = (
        "languages:\n\tpython:\n\t\tformatter:\n\t\t\targs @str:\n\t\t\t\t- format"
        '\n\t\t\t\t- "-q"\n\t\t\t\t- "-q"\n'
    )
    expected = [
        Token(type=TokenType.KEY, value="languages", line=1, indent=0),
        Token(type=TokenType.TYPE, value="unknown", line=1, indent=0),
        Token(type=TokenType.NEWLINE, value="\n", line=1, indent=0),
        Token(type=TokenType.KEY, value="python", line=2, indent=1),
        Token(type=TokenType.TYPE, value="unknown", line=2, indent=1),
        Token(type=TokenType.NEWLINE, value="\n", line=2, indent=1),
        Token(type=TokenType.KEY, value="formatter", line=3, indent=2),
        Token(type=TokenType.TYPE, value="unknown", line=3, indent=2),
        Token(type=TokenType.NEWLINE, value="\n", line=3, indent=2),
        Token(type=TokenType.KEY, value="args", line=4, indent=3),
        Token(type=TokenType.TYPE, value="str", line=4, indent=3),
        Token(type=TokenType.NEWLINE, value="\n", line=4, indent=3),
        Token(type=TokenType.OPERATOR, value="-", line=5, indent=4),
        Token(type=TokenType.VALUE, value="format", line=5, indent=4),
        Token(type=TokenType.NEWLINE, value="\n", line=5, indent=4),
        Token(type=TokenType.OPERATOR, value="-", line=6, indent=4),
        Token(type=TokenType.VALUE, value="-q", line=6, indent=4),
        Token(type=TokenType.NEWLINE, value="\n", line=6, indent=4),
        Token(type=TokenType.OPERATOR, value="-", line=7, indent=4),
        Token(type=TokenType.VALUE, value="-q", line=7, indent=4),
        Token(type=TokenType.NEWLINE, value="\n", line=7, indent=4),
        Token(type=TokenType.EOF, value="EOF", line=8, indent=0),
    ]
    actual = lexer.parse()
    assert actual == expected
