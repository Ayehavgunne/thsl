# thsl (Thistle)
### Typed Human-friendly Serialization Language
A typed configuration and serialization format. Imagine YAML combined with Protobufs, aiming for the best of both with a little TOML and Amazon Ion thrown in for good measure.

## Example
```
debug bool: false
name str: My Name
graphics:
	target_framerate int: 600
	fullscreen bool: false
	resolution:
		width int: 1920
		height int: 1080
```

Indentation is done via tabs only

## Features
Not finalized. Subject to change

- YAML like syntax
- Type safety (avoids the [Norway](https://hitchdev.com/strictyaml/why/implicit-typing-removed/) problem)
- Comments
- Trailing Commas
- Compound Types
  - Dictionaries
  - Lists
  - Sets
  - Tuples
    - Regular variety
    - Named Tuples
  - Structs
  - Enums
- Scalar Types
  - Bools
  - Ints
  - Floats
    - inf
    - -inf
    - nan
    - scientific notation
  - Decimals
    - inf
    - -inf
    - nan
    - scientific notation
  - Strings
  - Chars
  - Binary
  - Hexes
  - Octals
  - Base64
  - Complex numbers
  - Ranges
    - exclusive
    - inclusive
  - Dates
  - Times
  - DateTimes
  - Intervals
  - IP Addresses
- Inheritance
- Metadata via decorators
  - @immutable
  - @required
  - @optional

#### Maybe
- Code Generation (human-readable too!)
- Services
- Interchangeable binary and text representations
- Self-describing compact binary output

## Lexer TODO:
- [x] scientific notation
- [x] date/times
- [x] ranges
- [ ] heterogeneous lists
- [ ] single line dicts
- [ ] regular tuples
- [ ] null tuples
- [ ] single line tuples
- [ ] inheritance
- [ ] decorators
- [ ] services
- [ ] fix `value=',]'` with trailing comma

## Parser TODO:
- [x] start
- [ ] nesting

## Other TODO:
- [ ] binary output
- [ ] Python code generation
