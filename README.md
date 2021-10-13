# thsl (Thistle)
### Typed Human-friendly Serialization Language
A typed configuration language and serialization format. Imagine YAML crossed with
Protobufs.

## Example
```
debug .bool: false
name .str: My Name
graphics:
	target_framerate .int: 60
	fullscreen .bool: false
	resolution:
		width .int: 1920
		height .int: 1080
```

Indentation is done via tabs only

## Features
Not finalized. Subject to change

- [x] YAML like syntax
- [x] Type safety (avoids the
[Norway](https://hitchdev.com/strictyaml/why/implicit-typing-removed/) problem)
- [x] Comments
- Trailing Commas
- Validation
- String templating
- Compound Types
  - Dictionaries
  - Lists
  - Sets
  - Tuples
    - Regular variety
    - Named Tuples
  - Structs
  - Enums
- [x] Scalar Types
  - [x] Bools
  - [x] Ints
  - [x] Floats
    - [x] inf
    - [x] -inf
    - [x] nan
    - [x] scientific notation
  - [x] Decimals
    - [x] inf
    - [x] -inf
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
  - [x] Dates
  - [x] Times
  - [x] DateTimes
  - [x] Intervals
  - [x] IP Addresses
  - [x] URLs
- Inheritance
- Interfaces
- Type Aliases
- Metadata via decorators
  - @immutable
  - @required
  - @optional
  - @nullable
- Code Generation (human-readable as well!)

#### Maybe
- YAML and JSON output
  - conversion would be lossy unless only compatible types are used
- zlib (de)compression

## Benefits
With a grammar that is powerful enough to represent most language structures from a
variety of languages you no longer need to maintain two sources of truth, the data and
the schema. YAML and JSON are great, but they usually force the code maintainers to
structure the data as only the most basic of types and then in the code they must
cast/parse them to what is really needed. thsl tries to do away with that by allowing
everything about the data to be described in one place. Then the language can consume
the data in one of two ways. In places where dynamically reading the data is sufficient
then each language can generate the relavent data structures on the fly and use it.

`But what about IDE auto-complete?`

To help with that there will be full code generation that strives to be as close to the
thsl representation as possible in the target language. This means it will be just as
human-readable as anything you wrote yourself. However, with proper tooling/plugins,
even this might not be needed.

Other features like string templating will allow for reduction of repetative structures
in the config itself.

Finally, another benefit is that if this data must be consumed by multiple languages
then it reduces the number of places that a schema must be maintained even more! Imagine
having a Python backend with an Angular frontend. They must share a set of data and both
have to keep their models in sync. With thsl you can decouple the data structure and
maintain it in one place.

## Lexer TODO:
- [x] scientific notation
- [x] date/times
- [x] ranges
- [ ] heterogeneous lists
- [ ] single line dicts
- [ ] regular tuples
- [ ] single line tuples
- [ ] decorators
- [ ] fix `value=',]'` with trailing comma

## Parser TODO:
- [x] start
- [x] nesting
- [x] set fields without a value to a sane default that is not null
- [ ] string templating

## Other TODO:
- [ ] Finalize grammar and token structure
- [ ] Python code generation
- [ ] Code generation for other languages
- [ ] Parsing for other languages
