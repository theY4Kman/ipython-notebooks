import collections


# Th[is]? i. (a) test{2,6}\. (Or|is|it?)

T_EOF = -1       # Fake token to mark end of input. Makes parsing a bit easier.
T_STRING = 0     # abcdef\[
T_DOT = 1        # .
T_QUESTION = 2   # ?
T_ASTERISK = 3   # *
T_LBRACE = 4     # {
T_RBRACE = 5     # }
T_LBRACKET = 6   # [
T_RBRACKET = 7   # ]
T_LPAREN = 8     # (
T_RPAREN = 9     # )
T_COMMA = 10     # ,
T_PIPE = 11      # |

# For error reporting purposes
TOKEN_NAMES = {
    T_STRING: 'STRING',
    T_DOT: 'DOT',
    T_QUESTION: 'QUESTION',
    T_ASTERISK: 'ASTERISK',
    T_LBRACE: 'LBRACE',
    T_RBRACE: 'RBRACE',
    T_LBRACKET: 'LBRACKET',
    T_RBRACKET: 'RBRACKET',
    T_LPAREN: 'LPAREN',
    T_RPAREN: 'RPAREN',
    T_COMMA: 'COMMA',
    T_PIPE: 'PIPE',
}


def _tokenize(s):
    SINGLES = {
        '.': T_DOT,
        '?': T_QUESTION,
        '*': T_ASTERISK,
        '{': T_LBRACE,
        '}': T_RBRACE,
        '[': T_LBRACKET,
        ']': T_RBRACKET,
        '(': T_LPAREN,
        ')': T_RPAREN,
        ',': T_COMMA,
        '|': T_PIPE,
    }

    Token = collections.namedtuple('Token', ['type', 'text', 'index'])

    tokens = []
    _literal = []
    _literal_start = None
    i = 0

    def emit(type, text=None, index=None):
        if text is None:
            text = c
        if index is None:
            index = i
        tokens.append(Token(type, text, index))

    def literal():
        nonlocal _literal_start
        if _literal_start is None:
            _literal_start = i
        _literal.append(c)

    def close_literal():
        nonlocal _literal, _literal_start
        if _literal:
            text = ''.join(_literal)
            emit(T_STRING, text, _literal_start)
            _literal = []
            _literal_start = None

    while i < len(s):
        c = s[i]
        if c in SINGLES:
            close_literal()
            emit(SINGLES[c])
        elif c == '\\':
            # TODO: figure out what to really do here
            if s[i+1] in SINGLES:
                i += 1
                literal()
            else:
                raise NotImplemented
        else:
            literal()

        i += 1
    close_literal()

    emit(T_EOF, '')
    return tokens


class Match(object):
    def __init__(self, source, text, position, groups=()):
        self.source = source
        self.text = text
        self.start = position
        self.end = self.start + len(self.text)
        self._groups = (text,) + tuple(groups)

    def group(self, n):
        return self._groups[n]

    def groups(self):
        return self._groups


S_STRING = 0


class Symbol(object):
    def __init__(self, type_, text=None, children=None):
        self.type = type_
        self.text = text
        if children is None:
            children = ()
        self.children = tuple(children)

    def save(self, context, text):
        """Save the text matched for this symbol to the context"""
        context[self] = text

    def text(self, context):
        if self in context:
            return context[self]
        elif self.children:
            return ''.join(c.text(context) for c in self.children)


class RegularExpression(object):
    def __init__(self, source, symbols):
        """
        :type source: str
        :type symbols: list of Symbol
        """
        self.source = source
        self.symbols = symbols
    
    def __repr__(self):
        return 'yre.compile(%r)' % self.source

    def match(self, s):
        context = {}
        source = s
        i = 0
        t = 0
        while i < len(s) and t < len(self.symbols):
            symbol = self.symbols[t]
            s = s[i:]
            if symbol.type == S_STRING:
                if s.startswith(symbol.text):
                    symbol.save(context, symbol.text)
                    i += len(symbol.text)
                    t += 1
                    continue

            return None
        else:
            text = source[:i+1]
            return Match(source, text, 0)


_cache = {}
def compile(s):
    if s in _cache:
        return _cache[s]
    
    tokens = _tokenize(s)
    i = 0
    pieces = []  # Intermediate storage for children
    symbols = []
    stack = []
    expected_ends = []
    
    def emit(type, text=None, children=()):
        nonlocal pieces
        if children is None:
            children = pieces
            pieces = []
        symbols.append(Symbol(type, text, children))
    
    def expect(*types, save=False):
        nonlocal i
        if token.type not in types:
            type_names = ', '.join(TOKEN_NAMES[t] for t in types)
            raise SyntaxError(
                'Unexpected %r, expected one of: %r' % (token, type_names))
        if save:
            pieces.append(token)
        i += 1
        return True
    
    def accept(*types, save=False):
        nonlocal i
        if token.type in types:
            if save:
                pieces.append(token)
            i += 1
            return True
        else:
            return False

    def push(expected_end):
        nonlocal symbols
        stack.append(symbols)
        expected_ends.append(expected_end)
        symbols = []

    def expected_end():
        if expected_ends:
            return expected_ends[-1]
    
    while i < len(tokens):
        token = tokens[i]
        if accept(T_STRING):
            emit(S_STRING, text=token.text)
        elif accept(T_LPAREN):
            push(T_RPAREN)
        elif accept(expected_end()):
            
        else:
            if expected_ends:
                msg = 'Unexpected %r, expected %s' % (
                    token, TOKEN_NAMES[expected_end()])
            else:
                msg = 'Unexpected %r' % (token,)
            raise SyntaxError(msg)
    
    expression = RegularExpression(s, symbols)
    _cache[s] = expression
    return expression


def match(pattern, string):
    return compile(pattern).match(string)


def search(pattern, string):
    return compile(pattern).search(string)
