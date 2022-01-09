"""
Provides a symbol table abstraction. The symbol table associates the identifier names found in the program with
identifier properties needed for compilation: type, kind and running index. The symbol table for jack program has
two nested scopes (class/ subroutine).
"""

class symbolTable:
    # create a new empty symbol table: { name : (type, kind, index) }


    def __init__(self):
        self.current_scope = None
        self.symbol_table = {}


    def startSubroutine(self):
        """
        starts a new subroutine scope (ie reset the subroutine's symbol table)
        :return:
        """
        # saves the keys with 'argument' and 'local' value to delete

        keys_to_pop = []
        for name in self.symbol_table:
            if self.KindOf(name) in ('argument', 'local'):
                keys_to_pop.append(name)

        # delete the elements
        for key in keys_to_pop:
            self.symbol_table.pop(key)



    def define(self, name, type, kind):
        """
        defines a new identifier of a given name, type and kind and assign it a running index. Static and Field
        identifiers have a class scope, ARGS and VAR identifiers have a subroutine scope.
        :param name: String
        :param type: String
        :param kind: Static, Field, ARG, VAR
        :return:
        """
        index = self.VarCount(kind)
        self.symbol_table[name] = (type, kind, index)




    def VarCount(self, kind):
        """
        Returns the number of variable of a given kind already defined in the given current scope.
        :param kind: Static, Field, ARG, or VAR
        :return: int
        """
        values = self.symbol_table.values()
        count = 0
        for t in values:
            if kind in t:
                count += 1
        return count



    def KindOf(self, name):
        """
        Return the kind of the named identifier in the current scope. If the identifier is unknown in the current scope
        return NONE.
        :param name: string
        :return: STATIC, FIELD, ARG, VAR, or NONE
        """
        if self.symbol_table.get(name) == None:
            return None
        else:
            return self.symbol_table[name][1]


    def Typeof(self, name):
        """
        Return the type of the named identifier in the current scope.
        :param name: string
        :return: String
        """
        if self.symbol_table.get(name) == None:
            return None
        else:
            return self.symbol_table[name][0]

    def IndexOf(self, name):
        """
        Return the index assigned to the named identifier.
        :param name: String
        :return: Int
        """
        return self.symbol_table[name][2]

