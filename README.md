# thsl (Thistle)
### Typed Human-friendly Serialization Language
A typed configuration language and serialization format. Imagine YAML with types.

## Example
```
debug :bool: false
name :str: My Name
graphics:
	target_framerate :int: 60
	fullscreen :bool: false
	resolution:
		width :int: 1920
		height :int: 1080
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

- [x] YAML like syntax
- [x] Type safety (avoids the
[Norway](https://hitchdev.com/strictyaml/why/implicit-typing-removed/) problem)
- [x] Comments
- [x] Trailing Commas
- [ ] String templating
- Compound Types
  - [x] Dictionaries
  - [x] Lists
  - [x] Sets
  - [x] Tuples
- [x] Scalar Types
  - [x] Bools
  - [x] Ints
  - [x] Floats
    - [x] inf
    - [x] -inf
    - [x] -0
    - [x] nan
    - [x] scientific notation
  - [x] Decimals
    - [x] inf
    - [x] -inf
    - [x] -0
    - [x] nan
    - [x] scientific notation
  - [x] Strings
  - [x] Chars
  - [x] Binary
  - [x] Hexes
  - [x] Octals
  - [x] Base64
    - [x] encoding
    - [x] decoding
  - [x] Complex numbers
  - [x] Ranges
    - [x] exclusive
    - [x] inclusive
  - [x] Dates (with the help of the dateutil library)
  - [x] Times (with the help of the dateutil library)
  - [x] DateTimes (with the help of the dateutil library)
  - [x] Intervals (with the help of the tempora library)
  - [x] IP Addresses
  - [x] URLs
  - [x] Environment Variables
  - [x] Paths
  - [x] Semantic Version Numbers (using the semantic_version library)
  - [x] Regex
- [ ] YAML and JSON output
  - conversion would be lossy unless only compatible types are used
- [ ] YAML or JSON input
- [ ] type addon system
- [ ] dump to file
