"""
Emits VM commands into a file, using VM command syntax.
"""

arithmetic_table = {'-': 'sub', '+': 'add', '=': 'eq', '>':'gt', '<': 'lt' , '&': 'and', '|':'or', '~': 'not'}

class VMWritter:
    def __init__(self, vm_file):
        self.vm_file = vm_file

    def writePush(self, segment, index):
        """
        writes a VM push command
        :param segment: CONST, ARG, LOCAL, STATIC, THIS, THAT, POINTER, TEMP
        :param index: integer
        :return:
        """
        self.vm_file.write(f"push {segment} {index}\n")

    def writePop(self, segment, index):
        """
        writes a VM pop command
        :param segment:
        :param index:
        :return:
        """
        self.vm_file.write(f"pop {segment} {index}\n")



    def writeArithmetic(self, command, unary=False):
        """
        writes a VM arithmetic command.
        :param command: SUB, ADD, NEG, EQ, GT, LT, AND, OR, NOT
        :return:
        """
        if command == '*':
            self.writeCall('Math.multiply', 2)
        elif command == '/':
            self.writeCall('Math.divide', 2)
        elif command == '-' and unary == True:
            self.vm_file.write('neg\n')
        else:
            self.vm_file.write(f"{arithmetic_table[command]}\n")

    def writeLabel(self, label):
        """
        writes a VM label command.
        :param label: string
        :return:
        """
        self.vm_file.write(f"label {label}\n")



    def writeGoto(self, label):
        """
        writes a VM goto command
        :param label: string
        :return:
        """
        self.vm_file.write(f"goto {label}\n")

    def writeIf(self, label):
        """
        writes a VM If-Goto command.
        :param label:
        :return:
        """
        self.vm_file.write(f"if-goto {label}\n")

    def writeCall(self, name, nArgs):
        """
        writes a VM call command.
        :param name:
        :param nArgs:
        :return:
        """
        self.vm_file.write(f"call {name} {nArgs}\n")

    def writeFunction(self, name, nlocals):
        """
        writes a VM function command
        :param name:
        :param nlocals:
        :return:
        """
        self.vm_file.write(f'function {name} {nlocals}\n')



    def writeReturn(self):
        """
        writes a VM return command
        :return:
        """
        self.vm_file.write(f"return\n")