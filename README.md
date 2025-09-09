# thsl (Thistle)
### Typed Human-friendly Serialization Language
A typed configuration language and serialization format. Imagine YAML with types.

## Example
```
debug @bool: false
name @str: My Name
graphics:
	target_framerate @int: 60
	fullscreen @bool: false
	resolution:
		width @int: 1920
		height @int: 1080
```

Indentation is done via tabs only

See [sample.thsl](https://github.com/Ayehavgunne/thsl/blob/main/sample.thsl) for more.

## Install
This is currently a beta level project

```commandline
pip install thsl
```

## Usage
```python
>>> from pathlib import Path
>>> import thsl

>>> data = thsl.load(Path("data.thsl"))
{
  'debug': False,
  'name': 'My Name',
  'graphics': {
    'target_framerate': 60,
    'fullscreen': False,
    'resolution': {
      'width': 1920,
      'height': 1080
    }
  }
}
```

## Features
Not finalized. Subject to change

- [ ] YAML like syntax
- [ ] Type safety (avoids the
[Norway](https://hitchdev.com/strictyaml/why/implicit-typing-removed/) problem)
- [ ] Comments
- [ ] Trailing commas
- [ ] String templating
- [ ] String escaping
- Compound types
  - [ ] Dictionaries
  - [ ] Lists
  - [ ] Sets
  - [ ] Tuples
- [ ] Scalar types
  - [ ] Bools
  - [ ] Ints
  - [ ] Floats
    - [ ] inf
    - [ ] -inf
    - [ ] -0
    - [ ] nan
    - [ ] Scientific notation
  - [ ] Decimals
    - [ ] inf
    - [ ] -inf
    - [ ] -0
    - [ ] nan
    - [ ] Scientific notation
  - [ ] Strings
  - [ ] Chars
  - [ ] Binary
  - [ ] Hexes
  - [ ] Octals
  - [ ] Base64
    - [ ] encoding
    - [ ] decoding
  - [ ] Complex numbers
  - [ ] Ranges
    - [ ] exclusive
    - [ ] inclusive
  - [ ] Dates (with the help of the dateutil library)
  - [ ] Times (with the help of the dateutil library)
  - [ ] DateTimes (with the help of the dateutil library)
  - [ ] Intervals (with the help of the tempora library)
  - [ ] IP addresses
  - [ ] URLs
  - [ ] Environment variables
  - [ ] Paths
  - [ ] Semantic version numbers (using the semantic_version library)
  - [ ] Regex
- [ ] Type addon system
- [ ] Dump to file

## TODO
