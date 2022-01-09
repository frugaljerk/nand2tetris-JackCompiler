
import compilationEngine, tokenizer
import os

INPUT = r"C:\Users\HSapi\Documents\Computer Science\Nand2Tetris\projects\11\Pong"

def file_or_directory(path):
    """
    Yield a file if path is a file or yield files if path is a directory.
    :param path: os path or path-like object containing .jack file(s)
    :return: yield a tuple of opened file for reading, .xml file for writing tokens and .xml file for writing compilation.
    """
    # helper function to create .xml files.
    def xml_helper(f, read_file):
        root, ext = os.path.splitext(f)
        directory = os.path.join(path, 'my_jack')
        os.makedirs(directory, exist_ok=True)
        token_output = open(os.path.join(directory, root + 'T.xml'), "w")
        compile_output = open(os.path.join(directory, root + '.xml'), "w")
        vm_output = open(os.path.join(directory, root + '.vm'), "w")
        return tuple((read_file, token_output, compile_output, vm_output))

    # path is a single .jack file
    if os.path.isfile(path):
        read_file = open(path, 'r')
        file = os.path.basename(path)
        # make path without file name for creating folder
        path = os.path.dirname(path)
        yield xml_helper(file, read_file)
    # path is a directory containing multi .jack files
    else:
        filelist = os.listdir(path)
        for file in filelist:
            if file.endswith(".jack"):
                read_file = open(os.path.join(path,file), 'r')
                yield xml_helper(file, read_file)

if __name__ == "__main__":

    file_objects = file_or_directory(INPUT)
    for read_file, token_file, compile_file, vm_file in file_objects:
        print(read_file)
        tokenizer_object = tokenizer.Tokenizer(read_file, token_file)
        compile_object = compilationEngine.CompilationEngline(compile_file, vm_file)

        # write on token_file and stores token list in compileEngine object
        tokenizer_object.write_tokens(compile_object)

        # write on compile_file
        compile_object.add_tokens(tokenizer_object.tokens)
        compile_object.compileClass()



