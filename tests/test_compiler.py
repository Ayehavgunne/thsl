import datetime
from decimal import Decimal
from ipaddress import IPv4Address, IPv4Network, IPv6Address
from urllib.parse import ParseResult

import thsl

from dateutil.tz import tzoffset


def test_parser():
    sample = """debug :bool: true
num :int: -3
name :str: Frank Drebin
name_quotes :str: " My name"
name_single_quotes :str: 'My name is {name}'
escaping :str: "My \\"Name "
escaping_single_quotes :str: 'My name is \{{name}\}'
a_char :char: a
multi_line_str :str: "This
string is
    on multiple
         lines.
"
"keys can be in quotes" :int: 1
int :int: 1
str :str: str
my_num :int: "-50"
1 :str: one
uniform_list :int: [
	1
	2
	4
	7
]
a_set :int: <
	1
	2
	3
>
set_one_liner :int: <1, 2, 3>
#complex_list :dict: [
#	things:
#		one :int: 1
#		two :int: 2
#	other_things:
#		three :int: 3
#		four :int: 4
#]
uniform_list_one_liner :int: [1, 2, 3,]
simple_tuple :int: (1, 2, 3)
#dict_one_liner: {one :int: 1, two :float: 2}
some_bytes :bytes: 1110101
a_complex :complex: 3-2i
a_decimal :dec: 4.2
infinity :float: inf
neg_infinity :float: -inf
not_a_number :dec: nan
sci_note :float: 1.3e-4
hexadecimal :hex: deadbeef
octal :oct: 7
base_64 :base64: VGhlIFNwYW5pc2ggSW5xdWlzaXRpb24h
base_64_encode :base64e: Encode this string to base64
birthday :date: 1986-02-10
new_year :datetime: 2020-01-01 12:00:00 -6
my_interval :interval: 1 hour
alarm :time: 08:00:00AM
ip_address :ip: 192.168.1.1
ip_address_v6 :ip: FE80:CD00:0000:0CDE:1257:0000:211E:729C
ip_network :network: 192.168.0.0/28
my_page :url: http://www.example.com/index.html
range_example :range: 1..5  # non-inclusive
inclusive_example :range: 1...5  # inclusive
number_sep :int: 100_000_000
graphics:
	target_framerate :int: 60
	fullscreen :bool: false
	resolution :dict:
		width :int: 1920
		height :int: 1080
"""
    result = thsl.loads(sample)
    # noinspection PyArgumentList
    expected = {
        "1": "one",
        "a_char": "a",
        "a_complex": (3 - 2j),
        "a_decimal": Decimal("4.2"),
        "a_set": {1, 2, 3},
        "alarm": datetime.time(8, 0),
        "base_64": b"The Spanish Inquisition!",
        "base_64_encode": b"RW5jb2RlIHRoaXMgc3RyaW5nIHRvIGJhc2U2NA==",
        "birthday": datetime.date(1986, 2, 10),
        "debug": True,
        "escaping": 'My "Name ',
        "escaping_single_quotes": "My name is \\{{name}\\}",
        "graphics": {
            "fullscreen": False,
            "resolution": {"height": 1080, "width": 1920},
            "target_framerate": 60,
        },
        "hexadecimal": "0xdeadbeef",
        "inclusive_example": range(1, 6),
        "infinity": float("inf"),
        "int": 1,
        "ip_address": IPv4Address("192.168.1.1"),
        "ip_address_v6": IPv6Address("fe80:cd00:0:cde:1257:0:211e:729c"),
        "ip_network": IPv4Network("192.168.0.0/28"),
        "keys can be in quotes": 1,
        "multi_line_str": "This\nstring is\n    on multiple\n         lines.\n",
        "my_interval": datetime.timedelta(seconds=3600),
        "my_num": -50,
        "my_page": ParseResult(
            scheme="http",
            netloc="www.example.com",
            path="/index.html",
            params="",
            query="",
            fragment="",
        ),
        "name": "Frank Drebin",
        "name_quotes": " My name",
        "name_single_quotes": "My name is {name}",
        "neg_infinity": float("-inf"),
        "new_year": datetime.datetime(2020, 1, 1, 12, 0, tzinfo=tzoffset(None, -21600)),
        "not_a_number": Decimal("NaN"),
        "num": -3,
        "number_sep": 100000000,
        "octal": "0o7",
        "range_example": range(1, 5),
        "sci_note": 0.00013,
        "set_one_liner": {1, 2, 3},
        "simple_tuple": (1, 2, 3),
        "some_bytes": b"\x00u",
        "str": "str",
        "uniform_list": [1, 2, 4, 7],
        "uniform_list_one_liner": [1, 2, 3],
    }
    for key in result:
        if key == "not_a_number":
            assert Decimal.is_nan(result[key])
        else:
            assert result[key] == expected[key]
