import datetime
import os
import re
from decimal import Decimal
from ipaddress import IPv4Address, IPv4Network, IPv6Address
from math import isnan
from pathlib import Path
from urllib.parse import ParseResult

import semantic_version
import thsl

from dateutil.tz import tzoffset


DATA_DIR = Path(__file__).parent / "data"


def test_bool():
    actual = thsl.load(DATA_DIR / "bool.thsl")
    expected = {"debug": True}
    assert actual == expected


def test_int():
    actual = thsl.load(DATA_DIR / "int.thsl")
    expected = {"num": -3}
    assert actual == expected


def test_str():
    actual = thsl.load(DATA_DIR / "str.thsl")
    expected = {"name": "Frank Drebin"}
    assert actual == expected


def test_str_quotes():
    actual = thsl.load(DATA_DIR / "str_quotes.thsl")
    expected = {"name_quotes": " My name"}
    assert actual == expected


def test_str_single_quotes():
    actual = thsl.load(DATA_DIR / "str_single_quotes.thsl")
    expected = {"name_single_quotes": "My name is Frank Drebin"}
    assert actual == expected


def test_str_escaping():
    actual = thsl.load(DATA_DIR / "str_escaping.thsl")
    expected = {"escaping": 'My "Name '}
    assert actual == expected


# def test_str_escaping_single_quotes():
#     actual = thsl.load(DATA_DIR / "str_escaping_single_quotes.thsl")
#     expected = {"escaping_single_quotes": "My name is {name}"}
#     assert actual == expected


# def test_str_templating():
#     actual = thsl.load(DATA_DIR / "str_templating.thsl")
#     expected = {"template": "My name is Frank Drebin"}
#     assert actual["template"] == expected["template"]


def test_str_multi_line():
    actual = thsl.load(DATA_DIR / "str_multi_line.thsl")
    expected = {"multi_line_str": "This\nstring is\n    on multiple\n         lines.\n"}
    assert actual == expected


def test_char():
    actual = thsl.load(DATA_DIR / "char.thsl")
    expected = {"a_char": "a"}
    assert actual == expected


def test_keys_in_quotes():
    actual = thsl.load(DATA_DIR / "keys_in_quotes.thsl")
    expected = {"keys can be in quotes": 1}
    assert actual == expected


def test_types_as_keys():
    actual = thsl.load(DATA_DIR / "types_as_keys.thsl")
    expected = {"int": 1, "str": "str"}
    assert actual == expected


def test_str_as_int():
    actual = thsl.load(DATA_DIR / "str_as_int.thsl")
    expected = {"my_num": -50}
    assert actual == expected


def test_number_as_key():
    actual = thsl.load(DATA_DIR / "number_as_key.thsl")
    expected = {"1": "one"}
    assert actual == expected


def test_bytes():
    actual = thsl.load(DATA_DIR / "bytes.thsl")
    expected = {"some_bytes": b"\x00u"}
    assert actual == expected


def test_complex():
    actual = thsl.load(DATA_DIR / "complex.thsl")
    expected = {"a_complex": (3 - 2j)}
    assert actual == expected


def test_decimal():
    actual = thsl.load(DATA_DIR / "decimal.thsl")
    expected = {"a_decimal": Decimal("4.2")}
    assert actual == expected


def test_decimal_infinity():
    actual = thsl.load(DATA_DIR / "decimal_infinity.thsl")
    expected = {"infinity": Decimal("inf")}
    assert actual == expected


def test_decimal_neg_infinity():
    actual = thsl.load(DATA_DIR / "decimal_neg_infinity.thsl")
    expected = {"neg_infinity": Decimal("-inf")}
    assert actual == expected


def test_decimal_neg_zero():
    actual = thsl.load(DATA_DIR / "decimal_neg_zero.thsl")
    expected = {"neg_zero": Decimal("-0")}
    assert actual == expected


def test_decimal_nan():
    actual = thsl.load(DATA_DIR / "decimal_nan.thsl")
    expected = {"not_a_number": Decimal("nan")}
    assert actual.keys() == expected.keys()
    assert Decimal.is_nan(actual["not_a_number"])


def test_decimal_scientific_notation():
    actual = thsl.load(DATA_DIR / "decimal_scientific_notation.thsl")
    expected = {"sci_note": Decimal("0.00013")}
    assert actual == expected


def test_float():
    actual = thsl.load(DATA_DIR / "float.thsl")
    expected = {"my_float": 3.0}
    assert actual == expected


def test_float_infinity():
    actual = thsl.load(DATA_DIR / "float_infinity.thsl")
    expected = {"infinity": float("inf")}
    assert actual == expected


def test_float_neg_infinity():
    actual = thsl.load(DATA_DIR / "float_neg_infinity.thsl")
    expected = {"neg_infinity": float("-inf")}
    assert actual == expected


def test_float_nan():
    actual = thsl.load(DATA_DIR / "float_nan.thsl")
    expected = {"not_a_number": float("nan")}
    assert actual.keys() == expected.keys()
    assert isnan(actual["not_a_number"])


def test_float_scientific_notation():
    actual = thsl.load(DATA_DIR / "float_scientific_notation.thsl")
    expected = {"sci_note": 0.00013}
    assert actual == expected


def test_hex():
    actual = thsl.load(DATA_DIR / "hex.thsl")
    expected = {"hexadecimal": 0xDEADBEEF}
    assert actual == expected


def test_oct():
    actual = thsl.load(DATA_DIR / "oct.thsl")
    expected = {"octal": 7}
    assert actual == expected


def test_base64():
    actual = thsl.load(DATA_DIR / "base64.thsl")
    expected = {"base_64": b"The Spanish Inquisition!"}
    assert actual == expected


def test_base64_encoded():
    actual = thsl.load(DATA_DIR / "base64_encoded.thsl")
    expected = {"base_64_encode": b"RW5jb2RlIHRoaXMgc3RyaW5nIHRvIGJhc2U2NA=="}
    assert actual == expected


def test_date():
    actual = thsl.load(DATA_DIR / "date.thsl")
    expected = {"birthday": datetime.date(1986, 2, 10)}
    assert actual == expected


def test_datetime():
    actual = thsl.load(DATA_DIR / "datetime.thsl")
    expected = {
        "new_year": datetime.datetime(2020, 1, 1, 12, 0, tzinfo=tzoffset(None, -21600))
    }
    assert actual == expected


def test_interval():
    actual = thsl.load(DATA_DIR / "interval.thsl")
    expected = {"my_interval": datetime.timedelta(seconds=3600)}
    assert actual == expected


def test_time():
    actual = thsl.load(DATA_DIR / "time.thsl")
    expected = {"alarm": datetime.time(8, 0)}
    assert actual == expected


def test_ip_address():
    actual = thsl.load(DATA_DIR / "ip_address.thsl")
    expected = {"ip_address": IPv4Address("192.168.1.1")}
    assert actual == expected


def test_ip_address_v6():
    actual = thsl.load(DATA_DIR / "ip_address_v6.thsl")
    expected = {"ip_address_v6": IPv6Address("fe80:cd00:0:cde:1257:0:211e:729c")}
    assert actual == expected


def test_ip_network():
    actual = thsl.load(DATA_DIR / "ip_network.thsl")
    expected = {"ip_network": IPv4Network("192.168.0.0/28")}
    assert actual == expected


def test_url():
    actual = thsl.load(DATA_DIR / "url.thsl")
    # noinspection PyArgumentList
    expected = {
        "my_page": ParseResult(
            scheme="http",
            netloc="www.example.com",
            path="/index.html",
            params="",
            query="",
            fragment="",
        )
    }
    assert actual == expected


def test_url_part():
    actual = thsl.load(DATA_DIR / "url_part.thsl")
    # noinspection PyArgumentList
    expected = {
        "url_part": ParseResult(
            scheme="",
            netloc="",
            path="/index/hello/things",
            params="",
            query="",
            fragment="",
        )
    }
    assert actual == expected


def test_env():
    os.environ["MY_ENV_VAR"] = "hello"
    actual = thsl.load(DATA_DIR / "env.thsl")
    expected = {"my_env_var": os.environ["MY_ENV_VAR"]}
    assert actual == expected


def test_path():
    actual = thsl.load(DATA_DIR / "path.thsl")
    expected = {"my_path": Path("/usr/local")}
    assert actual == expected


def test_regex():
    actual = thsl.load(DATA_DIR / "regex.thsl")
    expected = {"my_regex": re.compile("colou?r")}
    assert actual == expected


def test_version():
    actual = thsl.load(DATA_DIR / "version.thsl")
    expected = {"my_version": semantic_version.Version("3.2.1")}
    assert actual == expected


def test_range():
    actual = thsl.load(DATA_DIR / "range.thsl")
    expected = {"my_range": range(1, 5)}
    assert actual == expected


def test_range_inclusive():
    actual = thsl.load(DATA_DIR / "range_inclusive.thsl")
    expected = {"my_range": range(1, 6)}
    assert actual == expected


def test_num_seperators():
    actual = thsl.load(DATA_DIR / "num_seperators.thsl")
    expected = {"number_sep": 100000000}
    assert actual == expected


def test_dict():
    actual = thsl.load(DATA_DIR / "dict.thsl")
    expected = {
        "graphics": {
            "fullscreen": False,
            "resolution": {"height": 1080, "width": 1920},
            "target_framerate": 60,
        }
    }
    assert actual == expected


def test_dict_one_liner():
    actual = thsl.load(DATA_DIR / "dict_one_liner.thsl")
    expected = {
        "dict_one_liner": {
            "one": 1,
            "two": 2.0,
        }
    }
    assert actual == expected


def test_list():
    actual = thsl.load(DATA_DIR / "list.thsl")
    expected = {"homogeneous_list": [1, 2, 4, 7]}
    assert actual == expected


def test_list_heterogeneous():
    actual = thsl.load(DATA_DIR / "list_heterogeneous.thsl")
    expected = {"my_list": [1, 3.14159, Decimal("2.11"), "hello"]}
    assert actual == expected


def test_list_one_liner():
    actual = thsl.load(DATA_DIR / "list_one_liner.thsl")
    expected = {"list_one_liner": [1, 2, 4, 7]}
    assert actual == expected


# def test_list_heterogeneous_one_liner():
#     actual = thsl.load(DATA_DIR / "list_heterogeneous_one_liner.thsl")
#     expected = {"heterogeneous_list_one_liner": [1, 3.14159, Decimal("2.11"), "hello"]}
#     assert actual == expected


def test_list_of_dicts():
    actual = thsl.load(DATA_DIR / "list_of_dicts.thsl")
    expected = {
        "list_of_dicts": [
            {"one": 1},
            {"two": 2},
        ]
    }
    assert actual == expected


def test_set():
    actual = thsl.load(DATA_DIR / "set.thsl")
    expected = {"a_set": {1, 2, 3}}
    assert actual == expected


def test_set_heterogeneous():
    actual = thsl.load(DATA_DIR / "set_heterogeneous.thsl")
    expected = {"typed_set": {1, 2.0, Decimal("3"), "4"}}
    assert actual == expected


# def test_set_heterogeneous_one_liner():
#     actual = thsl.load(DATA_DIR / "set_heterogeneous_one_liner.thsl")
#     expected = {"set_one_liner": {1, 2.0}}
#     assert actual == expected


def test_set_one_liner():
    actual = thsl.load(DATA_DIR / "set_one_liner.thsl")
    expected = {"set_one_liner": {1, 2, 3}}
    assert actual == expected


def test_tuple():
    actual = thsl.load(DATA_DIR / "tuple.thsl")
    expected = {"my_tuple": (1, 2, 3)}
    assert actual == expected


def test_tuple_heterogeneous():
    actual = thsl.load(DATA_DIR / "tuple_heterogeneous.thsl")
    expected = {"typed_tuple": (1, 2.0, Decimal("3"), "4")}
    assert actual == expected


def test_tuple_one_liner():
    actual = thsl.load(DATA_DIR / "tuple_one_liner.thsl")
    expected = {"my_tuple": (1, 2, 3)}
    assert actual == expected


# def test_tuple_heterogeneous_one_liner():
#     actual = thsl.load(DATA_DIR / "tuple_heterogeneous_one_liner.thsl")
#     expected = {"tuple_one_liner": (1, 2.0)}
#     assert actual == expected
