import os
import re
import tokenizer, symbolTable, VMWriter
"""
Gets input from Tokenizer and emits its output to and output file.
"""
jack_operators = ('+', '-', '*', '/', '&', '|', '<', '>','=')


def token_type(token):
    """
    Return the current type of token as constant.
    """
    if token in tokenizer.keyword:
        return 'keyword'
    elif token in tokenizer.symbol:
        return 'symbol'
    elif "\"" in token:
        return 'stringConstant'
    else:
        if re.search(r'\d', token[0]):
            return 'integerConstant'
        else:
            return 'identifier'

class CompilationEngline:

    def __init__(self, compile_file, vm_file):
        self.tokens = []
        self.temp_token = None
        self.compile_file = compile_file
        # initialize a symbol table
        self.symbol_table = symbolTable.symbolTable()
        self.class_name = None  # className of the .jack file compiled
        self.vm_file = VMWriter.VMWritter(vm_file)
        self.while_count = 0
        self.if_count = 0

    def add_tokens(self, token):
        """
        Building up token list from tokenizer input
        :param token:
        :return:
        """
        self.tokens.append(token)

    def eat(self, token=None):
        """
        if token given, check popped token against parameter token match, else raise error
        :param token:
        :return: token popped from token list
        """
        popped = self.tokens.pop(0)
        if token == None:
            return popped
        elif popped == token:
            return popped
        else:
            raise TypeError(f"Expect {token} token followed by {self.tokens[:20]}, but {popped} popped")

    def check_token(self):
        """
        check what is the next token without popping from the token list
        :return: token
        """
        return self.tokens[0]

    def write(self, xml_code):
        """
        write xml_code to compile_file
        :param xml_code:
        :return:
        """
        self.compile_file.write(xml_code)

    def write_token(self, token):
        """
        write terminal token in xml_code with respective token_type
        :param token:
        :return: token
        """
        type = token_type(token)
        if type == 'stringConstant':  # remove the leading double quote from the stringConstant
            self.compile_file.write(f"<{type}>" + token[1:] + f'</{type}>' + '\n')
        elif token in tokenizer.special_symbols:
            self.compile_file.write(
                '<' + type + '>' + tokenizer.special_symbols[token] + '</' + type + '>' + '\n'
            )
        else:
            self.compile_file.write(f"<{type}>" + token + f'</{type}>' + '\n')

        return token

    def compileClass(self):
        """
        compile a complete class.
        :return:
        """

        # handles class keyword
        self.write('<class>\n')
        self.write_token(self.eat('class'))
        # handles className and '{'
        self.class_name = self.write_token(self.eat())
        self.write_token(self.eat('{'))

        # handles classVarDec and subRoutineDec recursively
        self.compileClassVarDec()

        # handles SubroutineDec recursively
        self.compileSubroutine()

        # handles enclosing '}'

        self.write_token(self.eat('}'))
        self.write('</class>\n')

    def compileClassVarDec(self):
        """
        compiles a static declaration or a field declaration.
        :param token: current token passed in
        :return:
        """
        # token passed in should be 'static' or 'field'

        # handles 'static' or 'field' keyword
        while self.check_token() in ('field', 'static'):
            self.write('<classVarDec>\n')

            # consume token, add token to current_variable, and write to XML file
            kind = self.write_token(self.eat())

            # handles type and varName
            type = self.write_token(self.eat())
            name = self.write_token(self.eat())

            self.symbol_table.define(name, type, kind)

            # handles (, varName)*
            while self.check_token() == ',':
                self.write_token(self.eat(','))  # writes ','
                name = self.write_token(self.eat())  # writes varName
                self.symbol_table.define(name, type, kind)
            # handles ';'
            self.write_token(self.eat(';'))
            self.write('</classVarDec>\n')

    def compileSubroutine(self):
        """
        compiles a complete method, function, or constructor.
        :param token: current token passed in for writing
        :return:
        """

        # handles keywords: constructor, function, or method
        while self.check_token() in ('constructor', 'function', 'method'):
            self.write('<subroutineDec>\n')
            # remove symbols from previous subroutine
            self.symbol_table.startSubroutine()
            subroutine_type = self.write_token(self.eat())
            if subroutine_type == 'method':
                # in methods declaration: argument 0 is always name this, and type is set to class name
                self.symbol_table.define('this', self.class_name, 'argument')





            # handles (type|void), subroutineName, and '('
            self.write_token(self.eat())  # (type|void)
            subroutineName = self.write_token(self.eat())
            self.write_token(self.eat('('))

            self.compileParameterList()



            # handles subroutineBody
            self.write('<subroutineBody>\n')
            self.write_token(self.eat('{'))
            # handles varDec
            self.compileVarDec()

            # writes VM code for function after function var declarations.
            self.vm_file.writeFunction(f'{self.class_name}.{subroutineName}', self.symbol_table.VarCount('local'))

            if subroutine_type == 'method':
                # VM code for method callee
                self.vm_file.writePush('argument', 0)
                self.vm_file.writePop('pointer', 0)

            elif subroutine_type == 'constructor':
                self.vm_file.writePush('constant', self.symbol_table.VarCount('field'))
                self.vm_file.writeCall('Memory.alloc', 1)
                self.vm_file.writePop('pointer', 0)

            # handles statements next
            self.compileStatements()
            self.write_token(self.eat('}'))
            self.write('</subroutineBody>\n')

            # print(self.symbol_table.symbol_table)
            self.write('</subroutineDec>\n')

    def compileParameterList(self):
        """
        compiles a possibly empty parameter list, not including the enclosing '()'
        :return:
        """
        # writes paramList even if empty
        self.write('<parameterList>\n')
        # next token == ')' signals end of paramList
        token = self.check_token()
        if token != ')':
            type = self.write_token(self.eat())  # type
            name = self.write_token(self.eat())  # varName
            self.symbol_table.define(name, type, 'argument')
            while self.check_token() == ',':
                self.write_token(self.eat(','))  # more param, writes ','
                type = self.write_token(self.eat())  # more type varName
                name = self.write_token(self.eat())
                self.symbol_table.define(name, type, 'argument')

        self.write('</parameterList>\n')
        self.write_token(self.eat(')'))  # writes the ')'

    def compileVarDec(self):
        """
        compiles a var declaration.
        :return:
        """
        # writes 'var' token and varDec:

        while self.check_token() == 'var':
            self.write('<varDec>\n')
            self.write_token(self.eat('var'))
            # handles type varName
            type = self.write_token(self.eat())
            name = self.write_token(self.eat())
            self.symbol_table.define(name, type, 'local')

            # handles list of varName if ',' present

            while self.check_token() == ',':
                self.write_token(self.eat(','))
                name = self.write_token(self.eat())
                self.symbol_table.define(name, type, 'local')

            self.write_token(self.eat(';'))  # writes the ';' at the end of varDec
            self.write('</varDec>\n')

    def compileStatements(self):
        """
        compiles a sequence of statements, not including the enclosing '{}'
        :return:
        """
        self.write('<statements>\n')
        token = self.check_token()
        while token != '}':
            # check type of statement with the token given
            if token == 'let':
                self.compileLet()
            elif token == 'if':
                self.if_count += 1
                self.compileIf()

            elif token == 'while':
                self.while_count += 1
                self.compileWhile()
            elif token == 'do':
                self.compileDo()
            elif token == 'return':
                self.compileReturn()
            else:
                raise TypeError(f"Statement type error: {self.tokens[:20]}")
            token = self.check_token()
        self.write('</statements>\n')

    def compileDo(self):
        """
        compiles a do statement.
        :return:
        """
        self.write('<doStatement>\n')
        self.write_token(self.eat('do'))
        # handles subroutine call
        function_name = self.write_token(self.eat())  # function_name = subroutineName, varName or className

        if self.check_token() == '(': # subroutineName()
            self.vm_file.writePush('pointer', 0)
            # continue compiling Expressionlist
            self.write_token(self.eat('('))
            arg_count = self.compileExpressionList()
            self.write_token(self.eat(')'))

            function_name = self.class_name + '.' + function_name
            arg_count += 1

        else: # className | varName.subroutineName()
            self.write_token(self.eat('.'))

            if self.symbol_table.Typeof(function_name):  # function_name == varName
                if self.symbol_table.KindOf(function_name) == 'field':  # push the varName object into stack
                    self.vm_file.writePush('this', self.symbol_table.IndexOf(function_name))
                else:
                    self.vm_file.writePush(self.symbol_table.KindOf(function_name),
                                           self.symbol_table.IndexOf(function_name))
                function_name = self.symbol_table.Typeof(function_name) + '.' + self.write_token(self.eat())  # varName.subroutineName
                arg_count = 1  # start with 1 arg as the method object itself
            else:  # function_name == className
                function_name = function_name + '.' + self.write_token(self.eat())  # className.subroutineName
                arg_count = 0

            # continue compiling Expressionlist
            self.write_token(self.eat('('))
            arg_count += self.compileExpressionList()
            self.write_token(self.eat(')'))


        self.write_token(self.eat(';'))
        # writes to call VM codes
        self.vm_file.writeCall(function_name, arg_count)
        # do subroutine returns void: therefore pop temp 0
        self.vm_file.writePop('temp', 0)
        self.write('</doStatement>\n')

    def compileLet(self):
        """
        compiles a let statement.
        :return:
        """
        self.write('<letStatement>\n')
        self.write_token(self.eat('let'))  # writes 'let' keyword

        varName = self.write_token(self.eat())  # writes varName

        # next token could be '[' or '='
        # handles ('[' expression ']')? if token != '='
        if self.check_token() == '[':
            # # VM code for varName[expression]:
            self.vm_file.writePush(self.symbol_table.KindOf(varName), self.symbol_table.IndexOf(varName))
            self.write_token(self.eat('['))  # [
            # VM code for computing and pushing the value of expression1
            self.compileExpression()  # expression
            self.write_token(self.eat(']'))   # ]
            # ADD the offset from expression 1.
            self.vm_file.writeArithmetic('+')

            # VM code for computing and pushing the value of expression2
            self.write(self.eat('='))
            self.compileExpression()

            self.vm_file.writePop('temp', 0)  # // temp 0 = the value of expression2
            self.vm_file.writePop('pointer', 1)
            self.vm_file.writePush('temp', 0)
            self.vm_file.writePop('that', 0)


        else:
            self.write_token(self.eat('='))
            self.compileExpression()

            # handles object
            if self.symbol_table.KindOf(varName) == 'field':
                self.vm_file.writePop('this', self.symbol_table.IndexOf(varName))
            else:
                self.vm_file.writePop(self.symbol_table.KindOf(varName), self.symbol_table.IndexOf(varName))

        self.write_token(self.eat(';'))
        self.write('</letStatement>\n')

    def compileWhile(self):
        """
        compiles a while statement.
        :return:
        """
        self.write('<whileStatement>\n')
        self.write_token(self.eat('while'))

        while_count = self.while_count

        # while label for VM code label L1
        self.vm_file.writeLabel('W' + str(while_count) + 'true')

        self.write_token(self.eat('('))
        self.compileExpression()
        self.write_token(self.eat(')'))
        # VM code for not, if-goto L2
        self.vm_file.writeArithmetic('~')
        self.vm_file.writeIf('W' + str(while_count) + 'false')

        self.write_token(self.eat('{'))
        self.compileStatements()
        self.write_token(self.eat('}'))

        # VM code for goto L1
        self.vm_file.writeGoto('W' + str(while_count) + 'true')

        # VM code for L2
        self.vm_file.writeLabel('W' + str(while_count) + 'false')


        self.write('</whileStatement>\n')

    def compileReturn(self):
        """
        compiles a return statement.
        :return:
        """
        self.write('<returnStatement>\n')
        self.write_token(self.eat('return'))
        if self.check_token() != ';':
            self.compileExpression()
            self.write_token(self.eat(';'))
        else:
            self.write_token(self.eat(';'))
            # return void: push constant 0
            self.vm_file.writePush('constant', 0)
        self.vm_file.writeReturn()
        self.write('</returnStatement>\n')

    def compileIf(self):
        """
        compiles a If statement, possibly with a trailing else clause
        :return:
        """
        current_if_count = self.if_count

        self.write('<ifStatement>\n')
        self.write_token(self.eat('if'))
        self.write_token(self.eat('('))
        self.compileExpression()
        self.write_token(self.eat(')'))

        # VM Code not to negate expression
        self.vm_file.writeArithmetic('~')
        # VM Code for if-go L1
        self.vm_file.writeIf(f'{self.class_name}IF' + str(current_if_count) + 'true')


        self.write_token(self.eat('{'))
        self.compileStatements()
        self.write_token(self.eat('}'))





        # handles else statements
        if self.check_token() == 'else':

            # VM code for goto L2
            self.vm_file.writeGoto(f'{self.class_name}IF' + str(current_if_count) + 'false')
            self.write_token(self.eat('else'))

            # VM code for label L1
            self.vm_file.writeLabel(f'{self.class_name}IF' + str(current_if_count) + 'true')

            self.write_token(self.eat('{'))
            self.compileStatements()
            self.write_token(self.eat('}'))

            # VM code for label L2
            self.vm_file.writeLabel(f'{self.class_name}IF' + str(current_if_count) + 'false')

        else:
            # VM code for label L1
            self.vm_file.writeLabel(f'{self.class_name}IF' + str(current_if_count) + 'true')

        self.write('</ifStatement>\n')

    def compileExpression(self):
        """
        compiles an expression.
        :return:
        """
        self.write('<expression>\n')

        self.compileTerm()
        while self.check_token() in jack_operators:
            token = self.write_token(self.eat())
            self.compileTerm()
            self.vm_file.writeArithmetic(token)

        self.write('</expression>\n')



    def compileTerm(self):
        """
        compiles a term.
        :return:
        """
        self.write('<term>\n')

        if token_type(self.check_token()) == 'identifier':

            if self.tokens[1] == '[': # varName [ expression ]
                varName = self.write_token(self.eat())
                self.vm_file.writePush(self.symbol_table.KindOf(varName), self.symbol_table.IndexOf(varName))
                self.write_token(self.eat('['))
                self.compileExpression()
                self.write_token(self.eat(']'))
                # VM code to access value of arry[i] and put on top of stack
                self.vm_file.writeArithmetic('+')
                self.vm_file.writePop('pointer', 1)
                self.vm_file.writePush('that', 0)

            elif self.tokens[1] == '.':  # subroutine call: varName|className . subroutineName ( ExpressionList )
                function_name = self.write_token(self.eat())  # varName|className
                # check if varName or className
                if self.symbol_table.symbol_table.get(function_name):
                    if self.symbol_table.KindOf(function_name) == 'field':
                        self.vm_file.writePush('this', self.symbol_table.IndexOf(function_name))
                    else:
                        self.vm_file.writePush(self.symbol_table.KindOf(function_name), self.symbol_table.IndexOf(function_name))
                    # function_name is varName/object
                    function_name = self.symbol_table.Typeof(function_name)  # convert function Name to className
                    arg_count = 1
                else:
                    # function_name is className
                    arg_count = 0

                self.write_token(self.eat('.'))
                function_name = function_name + '.' + self.write_token(self.eat())  # subroutineName
                self.write_token(self.eat('('))
                arg_count += self.compileExpressionList()
                self.write_token(self.eat(')'))
                # VM code to call the function
                self.vm_file.writeCall(function_name, arg_count)

            elif self.tokens[1] == '(': # subroutine call: subroutineName ( ExpressionList )
                function_name = self.write_token(self.eat())  # subroutineName
                self.write_token(self.eat('('))
                arg_count = self.compileExpressionList()
                self.write_token(self.eat(')'))
                self.vm_file.writeCall(function_name, arg_count)

            else:  # varName
                token = self.write_token(self.eat())

                if self.symbol_table.KindOf(token) == 'field':
                    self.vm_file.writePush('this', self.symbol_table.IndexOf(token))
                else:
                    self.vm_file.writePush(self.symbol_table.KindOf(token), self.symbol_table.IndexOf(token))



        elif self.check_token() == '(':
            self.write_token(self.eat('('))
            self.compileExpression()
            self.write_token(self.eat(')'))
        elif self.check_token() in ('-', '~'):
            token = self.write_token(self.eat())
            self.compileTerm()
            self.vm_file.writeArithmetic(token, unary=True)
        else:
            # keywordConstant, stringConstant, integerConstant
            token = self.write_token(self.eat())

            if token in ('null', 'false'):
                self.vm_file.writePush('constant', 0)
            elif token == 'true':
                self.vm_file.writePush('constant', 1)
                self.vm_file.writeArithmetic('-', unary=True)
            elif token == 'this':
                self.vm_file.writePush('pointer', 0)
            elif token[0] == '\"':  # handles string constant
                string_constant = token[1:]  # removing the leading "
                self.vm_file.writePush('constant', len(string_constant))
                self.vm_file.writeCall('String.new', 1)
                for char in string_constant:
                    self.vm_file.writePush('constant', ord(char))
                    self.vm_file.writeCall('String.appendChar', 2)
            else:
                self.vm_file.writePush('constant', token)


        self.write('</term>\n')

    def compileExpressionList(self):
        """
        Compiles a possibly empty a comma seperated list of expressions.
        :return: number of expressions
        """
        self.write('<expressionList>\n')
        exp_count = 0
        while self.check_token() != ')':
            self.compileExpression()
            exp_count += 1
            while self.check_token() == ',':
                self.write_token(self.eat(','))
                self.compileExpression()
                exp_count += 1

        self.write('</expressionList>\n')

        return exp_count