# thsl (Thistle)
### Typed Human-friendly Serialization Language
A typed configuration and serialization format. Imagine YAML combined with Protobufs,
aiming for the best of both with a little TOML and Amazon Ion thrown in for good
measure.

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
- Type safety (avoids the
[Norway](https://hitchdev.com/strictyaml/why/implicit-typing-removed/) problem)
- Comments
- Trailing Commas
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
  - @nullable
- Code Generation (human-readable as well!)

#### Maybe
- YAML and JSON output

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
human-readable as anything you wrote yourself.

Other features like string templating will allow for reduction of repetative structures
in the config itself.

Finally, another benefit is that if this data must be consumed by multiple languages
then it reduces the number of places that the schema must be maintained even more!

## Lexer TODO:
- [x] scientific notation
- [x] date/times
- [x] ranges
- [ ] heterogeneous lists
- [ ] single line dicts
- [ ] regular tuples
- [ ] single line tuples
- [ ] inheritance
- [ ] decorators
- [ ] fix `value=',]'` with trailing comma

## Parser TODO:
- [x] start
- [ ] nesting
- [ ] string templating

## Other TODO:
- [ ] Finalize grammar and token structure
- [ ] Python code generation
- [ ] Code generation for other languages
- [ ] Parsing for other languages
