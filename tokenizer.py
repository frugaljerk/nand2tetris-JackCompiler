"""
Ignores all comments and while space in the input stream, and serialize it into Jack-language tokens.
"""

import re

# Jack Tokens:
keyword = ('class' , 'constructor' , 'function' , 'method' , 'field' , 'static' , 'var' , 'int' , 'char' , 'boolean' ,
            'void' , 'true' , 'false' , 'null' , 'this' , 'let' , 'do' , 'if' , 'else' , 'while' , 'return')
symbol = ('{' , '}' , '(' , ')' , '[' , ']' , '.' , ',' , ';' , '+' , '-' , '*' , '/' , '&' , '|' , '<' , '>' , '=' , '~')

special_symbols = {'<': '&lt;', '>': '&gt;', '\"': '&quot;', '&':'&amp;'}


class Tokenizer:

    def __init__(self, read_file, token_file):
        """
        Initialize Tokenizer object with file objects passed in.
        """
        self.read_file = read_file
        self.token_file = token_file
        self.current_char = None
        self.current_token = ""
        self.tokens = []

    def ignore_comment_space(self, c):
        """
        helper function to check if char is part of a comment or space. If so, continues reading next char
        :param c: char to check
        :return: set current_char to the char after space or comment
        """
        while c in ('/', ' ', '\n', '\t'):
            next = self.read_file.read(1)
            if c == '/' and  next == '/': # ignoring all chars until next line
                while next != '\n':
                    next = self.read_file.read(1)
                c = self.read_file.read(1)
            elif c == '/' and next == '*':  # ignoring all chars until */ encountered
                while not (c == '*' and next == '/'):
                    c = next
                    next = self.read_file.read(1)
                c = self.read_file.read(1)
            elif c == '/' and next == ' ':  # handles 3 / 4
                break
            else:
                c = next

            # TODO: handle if next char is another token. (ie in 4/5)

        self.current_char = c

    def has_more_token(self):
        """Returns True if there is more tokens in input and use advance() to set current_token"""

        if self.current_char == None:
            char = self.read_file.read(1)
        else:
            char = self.current_char  # reuse additional char read and reset current_char to None
            self.current_char = None

        # continue parsing until all comment and space ignored
        self.ignore_comment_space(char)

        # Return false if EOF
        if self.current_char == "":
            return False

        # returns true when current_char ready for to be advanced as a token.
        return True

    def advance(self):
        """
        Gets the next token from the input and makes it the current token.
        :return:
        """
        char = self.current_char

        if char in symbol:
            self.current_token = char
            self.current_char = None

        # Tokenize stringConstant
        elif char == "\"":
            self.current_token += char
            char = self.read_file.read(1)
            while char != "\"":
                self.current_token += char
                char = self.read_file.read(1)
            self.current_char = None

        # Tokenize integerConstant
        elif re.search("\d", char):
            while re.search("\d", char):
                self.current_token += char
                char = self.read_file.read(1)
            self.current_char = char  # save the next char since it could be another token (ie 33+22)

        # Tokenize identifiers
        elif re.search("\w", char):
            while re.search("\w", char):
                self.current_token += char
                char = self.read_file.read(1)
            self.current_char = char

    def token_type(self):
        """
        Return the current type of token as constant.
        """

        if self.current_token in keyword:
            return 'keyword'
        elif self.current_token in symbol:
            return 'symbol'
        elif "\"" in self.current_token:
            return 'stringConstant'
        else:
            if re.search(r'\d', self.current_token[0]):
                return 'integerConstant'
            else:
                return 'identifier'

    def write_tokens(self, compiler_engline):
        """
        write to token xml and add tokens to compileEngline token list.
        :param compiler_tokens:
        :return:
        """
        self.token_file.write('<tokens>\n')
        while self.has_more_token():
            self.advance()
            token_type = self.token_type()
            if token_type == 'stringConstant':
                self.token_file.write(
                    '<' + token_type + '>' + self.current_token[1:] + '</' + token_type + '>' + '\n')
            elif self.current_token in special_symbols:
                self.token_file.write(
                    '<' + token_type + '>' + special_symbols[self.current_token] + '</' + token_type + '>' + '\n'
                )
            else:
                self.token_file.write(
                    '<' + token_type + '>' + self.current_token + '</' + token_type + '>' + '\n')
            compiler_engline.add_tokens(self.current_token)
            self.current_token = ''
        self.token_file.write('</tokens>\n')