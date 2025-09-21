package lexer

enum LexerContext:
  case Root

class Lexer(input: String):
    private var pos: Int = 0
    private var line: Int = 0
    private var column: Int = 0
    private var word: String = ""
    private var context: LexerContext = LexerContext.Root
    private var current_char: Option[Char] = None
    private var eof: Boolean = false
