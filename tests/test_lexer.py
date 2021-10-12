import pytest

from src.grammar import TokenType
from src.lexer import Lexer, Token


@pytest.fixture
def lexer():
    return Lexer("test")


@pytest.mark.parametrize(
    ("config", "expected_key"),
    (
        ("my_value .int: 1\n", "my_value"),
        ("'my_value' .int: 1\n", "my_value"),
        ('"my_value" .int: 1\n', "my_value"),
        ("' my_value' .int: 1\n", " my_value"),
        ('" my_value" .int: 1\n', " my_value"),
        ("' my_value ' .int: 1\n", " my_value "),
        ('" my_value " .int: 1\n', " my_value "),
        ("'my_value ' .int: 1\n", "my_value "),
        ('"my_value " .int: 1\n', "my_value "),
        ("int .int: 1\n", "int"),
        ("'int' .int: 1\n", "int"),
        ('"int" .int: 1\n', "int"),
        ("' int' .int: 1\n", " int"),
        ('" int" .int: 1\n', " int"),
        ("' int ' .int: 1\n", " int "),
        ('" int " .int: 1\n', " int "),
        ("'int ' .int: 1\n", "int "),
        ('"int " .int: 1\n', "int "),
        ("1 .int: 1\n", "1"),
        ("1hi .int: 1\n", "1hi"),
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
    actual = list(lexer.analyze())
    assert actual[0] == expected


@pytest.mark.parametrize(
    ("config",),
    (
        ("my_value .int: 1\n",),
        ("my_value .int : 1\n",),
        ("my_value .int  1\n",),
        ("my_value .int    1\n",),
        ("'my_value' .int: 1\n",),
        ('"my_value" .int: 1\n',),
        ("' my_value' .int: 1\n",),
        ('" my_value" .int: 1\n',),
        ("' my_value ' .int: 1\n",),
        ('" my_value " .int: 1\n',),
        ("'my_value ' .int: 1\n",),
        ('"my_value " .int: 1\n',),
        ("int .int: 1\n",),
        ("'int' .int: 1\n",),
        ('"int" .int: 1\n',),
        ("' int' .int: 1\n",),
        ('" int" .int: 1\n',),
        ("' int ' .int: 1\n",),
        ('" int " .int: 1\n',),
        ("'int ' .int: 1\n",),
        ('"int " .int: 1\n',),
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
    actual = list(lexer.analyze())
    assert actual[1] == expected


@pytest.mark.parametrize(
    ("config", "expected_key", "index"),
    (
        ("my_value .bytes: 1110101\n", "1110101", 2),
        ("my_value .bytes  1110101\n", "1110101", 2),
        ("my_value .bytes    1110101\n", "1110101", 2),
        ("my_value .bytes: 1110101 # comment\n", "1110101", 2),
        ("my_value .int: 1\n", "1", 2),
        ("my_value .int: '1'\n", "1", 2),
        ('my_value .int: "1"\n', "1", 2),
        ("my_value .int: -1\n", "-1", 2),
        ("my_value .int: 100_000_000\n", "100000000", 2),
        ("my_value .float: 1\n", "1", 2),
        ("my_value .float: 1.000_000_000\n", "1.000000000", 2),
        ("my_value .float: 1.0\n", "1.0", 2),
        ("my_value .float: -1.0\n", "-1.0", 2),
        ("my_value .float: 1.3e-4\n", "1.3e-4", 2),
        ("my_value .dec: 4\n", "4", 2),
        ("my_value .dec: 1.000_000_000\n", "1.000000000", 2),
        ("my_value .dec: 1.0\n", "1.0", 2),
        ("my_value .dec: -1.0\n", "-1.0", 2),
        ("my_value .dec: 1.3e-4\n", "1.3e-4", 2),
        ("my_value .complex: 3-2i\n", "3-2i", 2),
        ("my_value .hex: deadbeef\n", "deadbeef", 2),
        ("my_value .oct: 7\n", "7", 2),
        ("my_value .char: a\n", "a", 2),
        (
            "my_value .str: Hello my name is Frank Drebin\n",
            "Hello my name is Frank Drebin",
            2,
        ),
        (
            "my_value .str: 'Hello my name is Frank Drebin'\n",
            "Hello my name is Frank Drebin",
            2,
        ),
        (
            'my_value .str: "Hello my name is Frank Drebin"\n',
            "Hello my name is Frank Drebin",
            2,
        ),
        (
            'my_value .str: " Hello my name is Frank Drebin"\n',
            " Hello my name is Frank Drebin",
            2,
        ),
        (
            'my_value .str: " Hello my name is Frank Drebin "\n',
            " Hello my name is Frank Drebin ",
            2,
        ),
        (
            'my_value .str: "Hello my name is Frank Drebin "\n',
            "Hello my name is Frank Drebin ",
            2,
        ),
        # .str: "This
        # string is
        #     on multiple
        #          lines.
        # "
        (
            """my_value .str: "This
string is
    on multiple
         lines.
"\n""",
            "This\nstring is\n    on multiple\n         lines.\n",
            2,
        ),
        # (
        #     'my_value .str: escaping\\n new line\n',
        #     "escaping\n new line",
        #     2
        # ),
        (
            "my_value .base64: VGhlIFNwYW5pc2ggSW5xdWlzaXRpb24h\n",
            "VGhlIFNwYW5pc2ggSW5xdWlzaXRpb24h",
            2,
        ),
        (
            "my_value .base64e: Encode this string to base64\n",
            "Encode this string to base64",
            2,
        ),
        ("my_value .date: 1986-02-10\n", "1986-02-10", 2),
        ("my_value .datetime: 2020-01-01 12:00:00 -6\n", "2020-01-01 12:00:00 -6", 2),
        ("my_value .interval: 1 hour\n", "1 hour", 2),
        ("my_value .ip: 192.168.1.1\n", "192.168.1.1", 2),
        (
            "my_value .url: http://www.example.com/index.html\n",
            "http://www.example.com/index.html",
            2,
        ),
        ("my_value .env: PATH\n", "PATH", 2),
        ("my_value .bool: false\n", "false", 2),
        ("my_value .bool: true\n", "true", 2),
        ("my_value .float: inf\n", "inf", 2),
        ("my_value .float: -inf\n", "-inf", 2),
        ("my_value .float: nan\n", "nan", 2),
        ("my_value .dec: inf\n", "inf", 2),
        ("my_value .dec: -inf\n", "-inf", 2),
        ("my_value .dec: nan\n", "nan", 2),
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
    actual = list(lexer.analyze())
    expected.line = actual[index].line
    assert actual[index] == expected


@pytest.mark.parametrize(
    ("config", "expected_key"),
    (
        (
            """graphics:
\ttarget_framerate .int: 60
""",
            "false",
        ),
        (
            """graphics
\ttarget_framerate .int 60
""",
            "false",
        ),
    ),
)
def test_nesting(lexer, config, expected_key):
    lexer.text = config
    expected = [
        Token(type=TokenType.KEY, value="graphics", line=1, indent=0),
        Token(type=TokenType.NEWLINE, value="\n", line=1, indent=0),
        Token(type=TokenType.KEY, value="target_framerate", line=2, indent=1),
        Token(type=TokenType.TYPE, value="int", line=2, indent=1),
        Token(type=TokenType.VALUE, value="60", line=2, indent=1),
        Token(type=TokenType.NEWLINE, value="\n", line=2, indent=1),
        Token(type=TokenType.EOF, value="EOF", line=3, indent=0),
    ]
    actual = list(lexer.analyze())
    assert actual == expected


def test_tokenization(lexer):
    config = "my_value .bool: false\n"
    lexer.text = config
    expected = [
        Token(type=TokenType.KEY, value="my_value", line=1, indent=0),
        Token(type=TokenType.TYPE, value="bool", line=1, indent=0),
        Token(type=TokenType.VALUE, value="false", line=1, indent=0),
        Token(type=TokenType.NEWLINE, value="\n", line=1, indent=0),
        Token(type=TokenType.EOF, value="EOF", line=2, indent=0),
    ]
    actual = list(lexer.analyze())
    assert actual == expected
