
__author__ = "Adam Nieslanik"
__login__ = "xniesl00"

import argparse
import xml.etree.ElementTree as etree
import sys
import fileinput


class Arguments:
    """A class for parsing command line parameters"""
    def __init__(self):
        self.args = None
        
    def parse(self,id):
        """returns source file, prints help with --help parameter"""
        parser = argparse.ArgumentParser(add_help=False)
        parser.add_argument('-h','--help',action='store_true')
        parser.add_argument('--source',type=str)
        parser.add_argument('--input',type=str)
        self.args = parser.parse_args()
        
        if self.args.help is True:
            if len(sys.argv) > 2:
                exit(ErrorCodes.script_Error)
            else:
                print("Skript nacte XML reprezentaci programu a tento program s vyuzitim vstupu dle parametru prikazove radky interpretuje a generuje vystup")
                exit(ErrorCodes.success)
        if self.args.source == None and self.args.input == None:
            exit(ErrorCodes.script_Error)
        if id == 1:
            return self.args.source
        if id == 2:
            return self.args.input
    
    
class ErrorCodes:
    """Class that represents error codes program exits with"""
    success = 0
    script_Error = 10
    input_Error = 11
    output_Error = 12
    xml_formatError = 31
    xml_structError = 32
    semanticError = 52
    typeError = 53
    variableError = 54
    frameError = 55
    existError = 56
    valueError = 57
    stringError = 58

class XML:
    """Class for parsing XML source file.
            Attributes:
            self.xml: input XML file
            self.out: parsed XML file
            self.root: XML file root
            self.rightOrder: checks for right instruction order
            self.parsed_instructions: list of parsed instruction before sort
            self.parsed_instructionsSort: sorted list of parsed instructions
            self.sorted: sorted instruction's order codes, this list helps sorting whole instruction list
            self.labelList: dictionary with labels name and their values(order codes)
    """
    def __init__(self,input) -> None:
        self.xml = input
        self.out = None
        if self.xml == None:
            self.out = etree.parse(sys.stdin)
        else:
            try:
                self.out = etree.parse(self.xml)
            except:
                exit(ErrorCodes.xml_formatError)
            else:
                self.out = etree.parse(self.xml)
        self.root = self.out.getroot()
        self.rightOrder = 1
        self.parsed_instructions = []
        self.parsed_instructionsSort = []
        self.sorted = []
        self.labelList = {}


    def xmlParse(self):
            """Parse XML root"""
            ops = []
            if self.root.tag != 'program':
                exit(ErrorCodes.xml_structError)

            # main loop that creates list of instruction with their order, opcode and arguments
            for child in self.root:
                self.instruction = []
                
                # checking the right XML structure
                if child.tag != 'instruction':
                    exit(ErrorCodes.xml_structError)
                try:
                    opcode = child.attrib['opcode']
                    order = int(child.attrib['order'])
                except:
                    exit(ErrorCodes.xml_structError)
                else:
                    opcode = child.attrib['opcode']
                    order = int(child.attrib['order'])
                if order < 1:
                    exit(ErrorCodes.xml_structError)
                
                # appends instruction's order to the list
                self.instruction.append(order)
                
                # if duplicit order, exit with error
                if order not in ops:
                    ops.append(order)
                else:
                    exit(ErrorCodes.xml_structError)
                
                # appends instruction's opcode to the list
                self.instruction.append(opcode)

                y = 0 # represents instruction's arguments count
                for x,childnumber in enumerate(child,1): # for checking the right order of arguments
                        y +=1
                
                cnt = 1
                while cnt <= y:
                    # if wrong argument number found, exit with error
                    for number,childArgs in enumerate(child,1):
                        if number > 3:
                            exit(ErrorCodes.xml_structError)
                        if y == 1:
                            if childArgs.tag not in ['arg1']:
                                exit(ErrorCodes.xml_structError)
                        if y == 2:
                            if childArgs.tag not in ['arg2','arg1']:
                                exit(ErrorCodes.xml_structError)
                        if y == 3:
                            if childArgs.tag not in ['arg3','arg2','arg1']:
                                exit(ErrorCodes.xml_structError)
                            
                        operands = [] # clear operands list for each instruction

                        # appends instruction's arguments in right order
                        if childArgs.tag == 'arg' + str(cnt):
                            cnt +=1
                            type = childArgs.attrib['type']
                            if childArgs.text != None:
                                op = childArgs.text.strip()
                            else:
                                op = childArgs.text
                            operands.append(type)

                            # casts int arguments to integer
                            if type == 'int':
                                try:
                                    operands.append(int(op))
                                except:
                                    exit(ErrorCodes.xml_structError)
                                else:
                                    operands.append(int(op))
                            
                            # cast bool arguments to boolean
                            if type == 'bool':
                                if op == 'true':
                                    op = True
                                else:
                                    op = False
                                operands.append(op)

                            # replace escape sequences with right character
                            if type == 'string':
                                if op is not None:
                                    i = op.count('\\') # number of escape characters

                                    for x in range(i):
                                        escape_index = op.find('\\') # index of the beginning of escape character
                                        if escape_index != -1:
                                            escape = op[escape_index + 1:escape_index + 4] # gets the next 3 numbers after the beginning of escape seq.
                                            escape_replace = chr(int(escape)) # converts these numbers to character
                                            op = op.replace('\\'+ escape,escape_replace) # replace the escape seq.  with converted character

                            # appends operand to the instruction's operands list               
                            operands.append(op)
                            
                            # store the label in self.labelList, if label has already been stored, exit with error
                            if opcode == 'LABEL':
                                try:
                                    bool(self.labelList[op])
                                except:
                                    self.labelList[op] = order
                                else:
                                    exit(ErrorCodes.semanticError)
                            
                            # appends whole instruction's operands list to the instruction
                            self.instruction.append(operands)

                # append instruction with order, opcode and operands to the list
                self.parsed_instructions.append(self.instruction)

            # to the end of the list inserts 'END' to check if we interpreted each instruction
            self.parsed_instructions.append('END')

            # sort order codes the get instructions in right order
            self.sorted = ops.sort()
            
            i = 0
            j = 0
            
            # loops through instruction list until all instruction are in right order
            while j < len(ops):
                    x = self.parsed_instructions[i] # x = instruction's order code
                    
                    if x == 'END':
                        i = 0
                        
                    elif x[0] == ops[j]:
                        self.parsed_instructionsSort.append(x)  # replace instruction's order code to get the instruction's sorted by order codes
                        j +=1

                    else:
                        i +=1

            # gives back the 'END' to the list        
            self.parsed_instructionsSort.append('END')
         
            # return sorted list of instructions
            return self.parsed_instructionsSort
       
    
    def getLabel(self):
        """returns list of stored label names"""
        return self.labelList
    

class Start:
    """ Class that retrieves input file from command line parameter.
            Attributes:
                input_file: file with XML source code
    """

    def get_input(self):
        """returns source code file"""
        input = Arguments()
        input_file = input.parse(1)
        return input_file
    
class Instructions:
    """Class that represents every instruction.
        Attributes:
            input_file: cource code file
            self.xml_instruction: represents XML class with input file as parameter
            self.order: to interpret instructions in required order
            self.GlobalList: represents Global Frame
            self.TempList: represents Temporary Frame
            self.LocalList: represents frame stack(Local Frame)
            self.stack: data stack
            self.callStack: stores values with return adresses
            self.operandsSort: the get the right instruction after jump instructions
            self.inputList: for reading lines from stdin (READ instruction)
            self.line: line in stdin file (READ instruction)
            self.instructionList: list of sorted instructions
    """
    def __init__(self) -> None:  
        input_file = Start.get_input(self)
        self.xml_instruction = XML(input_file)
        self.order = 0
        self.GlobalList = {}
        self.TempList = {}
        self.LocalList = []
        self.stack = []
        self.callStack = []
        self.operandsSort = []
        self.inputList = []
        self.line = 0
        self.instructionList = self.xml_instruction.xmlParse()

        # to get the position of order in instruction list
        for num,instruction in enumerate(self.instructionList):
            self.operandsSort.append(instruction[0])
        
    def get_instructions(self): 
        """returns instruction in required order to be interpreted"""   
        index = self.order
        self.order += 1
        return self.instructionList[index]
    
    def get_type(self,operand):
        """returns type of operand"""
        operand_type = operand[0]
        return operand_type
    
    def set_value(self,dest,source):
        """sets source value to destination"""
        dest = source
        
        return dest
        
    def get_value(self,op):
            """ returns variable's value depending on frame"""
            op_frame,op_name = op.split('@')

            # gets variable from Global List
            if op_frame == 'GF':
                self.checkExist(op_name,1)
                op = self.GlobalList[op_name]

            # gets variable from top of Local Frame list
            elif op_frame == 'LF':
                self.checkExist(op_name,2)
                frame = self.getFrame()
                op = frame[op_name]

            # gets variable from Temporary Frame, checks if frame/variable exists
            elif op_frame == 'TF':
                try:
                    if self.TempList['init'] == False:
                        pass
                except:
                    exit(ErrorCodes.frameError)
                else:
                    if self.TempList['init'] == False:
                        exit(ErrorCodes.frameError)
                self.checkExist(op_name,3)
                frame = self.TempList
                op = frame[op_name]

            # undefined variable
            if op == None:
                exit(ErrorCodes.existError)
                
            return op
    
    def set_to_var(self,op,op2):
        """sets result of operation to the variable in right frame"""
        op_frame,op_name = op.split('@')

        # sets value to variable in Global List
        if op_frame == 'GF':
                self.checkExist(op_name,1)
                self.GlobalList[op_name] = self.set_value(op_name,op2)

        # sets value to variable in Local Frame
        if op_frame == 'LF':
                self.checkExist(op_name,2)
                frame = self.popFrame()
                frame[op_name] = self.set_value(op_name,op2)
                self.LocalList.append(frame)

        # sets value to variable in Temporary Frame, checks is variable/frame exist
        if op_frame == 'TF':
            try:
                if self.TempList['init'] == False:
                    pass
            except:
                exit(ErrorCodes.frameError)
            else:
                if self.TempList['init'] == False:
                    exit(ErrorCodes.frameError)
            self.checkExist(op_name,3)
            self.TempList[op_name] = self.set_value(op_name,op2)

    def getOp1(self,instruction):
        """ returns first operand"""
        instructionOp1 = instruction[2]
        return instructionOp1[1]
    
    def getOp2(self,instruction):
        """ returns second operand"""
        instructionOp2 = instruction[3]
        return instructionOp2[1]
    
    def getOp3(self,instruction):
        """ return third operand"""
        instructionOp3 = instruction[4]
        return instructionOp3[1]
    
    def checkExist(self,variable_name,frameId):
        """ Checks, if variable has been defined in the frame.
            Attributes:
                self.variable_name: name of variable to be checked
        """
        #variable_name = variable_name

        # frameId represents each frame
        # frameId = 1 is ID for Global List
        if frameId == 1:
            if not variable_name in self.GlobalList:
                exit(ErrorCodes.variableError)

        # frameId = 2 is ID for Local Frame
        elif frameId == 2:
            try:
                frame = self.getFrame()
            except:
                exit(ErrorCodes.frameError)
            else:
                frame = self.getFrame()

            if not variable_name in frame:
                exit(ErrorCodes.variableError)

        # frameId = 3 is ID for Temporary Frame
        elif frameId == 3:
            try:
                if self.TempList['init'] == False:
                    pass
            except:
                exit(ErrorCodes.frameError)
            else:
                if self.TempList['init'] == False:
                    exit(ErrorCodes.frameError)
                elif not variable_name in self.TempList:
                    exit(ErrorCodes.variableError)
    
    def pushStack(self,instruction_argument):
        """ Push value to the stack
            Attributes:
                self.argument: argument of instruction
        """
        argument = instruction_argument
        self.stack.append(argument)
        
    def popStack(self):
        """ Pop value from stack"""

        # if stack is empty, exit with error
        if not bool(self.stack):
            exit(ErrorCodes.existError)
        value = self.stack.pop()
        return value
        
    def getFrame(self):
        """ Returns frame from the top of Local List"""

        # if Local List is empty, exit with error
        try:
            tempFrame = self.LocalList[-1]
        except:
            exit(ErrorCodes.frameError)
        else:
            tempFrame = self.LocalList[-1]
        return tempFrame
    
    def popFrame(self):
        """ Returns frame and pops this frame from Local List"""

        # if Local list is empty, exit with error
        if not bool(self.LocalList):
            exit(ErrorCodes.frameError)

        frame = self.LocalList.pop()
        return frame
    
class Run(Instructions):
    """ Class that represents interpreting each instruction
        Attributes:
            self.stdin: represents file to read from. (READ instruction)
    """
    def __init__(self) -> None:
        super().__init__()
        self.stdin = None
        
    def run_instruction(self):
        """ Gets instruction from instruction list and starts to interpret it"""
        self.instruction = self.get_instructions()

        # for case-insensitive opcodes     
        instruction_opcode = str.upper(self.instruction[1])

        # if we reached to the end of the instruction list, exit program with SUCCESS
        if self.instruction == 'END':
            exit(ErrorCodes.success)
        
        # find execute() metod for the right class
        match instruction_opcode:
            case 'WRITE':
                WRITE.execute(self,self.instruction)
                return
            case 'READ':
                READ.execute(self,self.instruction)
                return
            case 'MOVE':
                MOVE.execute(self,self.instruction)
                return
            case 'ADD':
                ADD.execute(self,self.instruction)
                return
            case 'SUB':
                SUB.execute(self,self.instruction)
                return
            case 'MUL':
                MUL.execute(self,self.instruction)
                return
            case 'IDIV':
                IDIV.execute(self,self.instruction)
                return
            case 'DEFVAR':
                DEFVAR.execute(self,self.instruction)
                return
            case 'LABEL':
                LABEL.execute(self,self.instruction)
                return
            case 'JUMP':
                JUMP.execute(self,self.instruction)
                return
            case 'JUMPIFEQ':
                JUMPIFEQ.execute(self,self.instruction)
                return
            case 'JUMPIFNEQ':
                JUMPIFNEQ.execute(self,self.instruction)
                return
            case 'PUSHS':
                PUSHS.execute(self,self.instruction)
                return
            case 'POPS':
                POPS.execute(self,self.instruction)
                return
            case 'EXIT':
                EXIT.execute(self,self.instruction)
                return
            case 'LT':
                LT.execute(self,self.instruction)
                return
            case 'GT':
                GT.execute(self,self.instruction)
                return
            case 'EQ':
                EQ.execute(self,self.instruction)
                return
            case 'LABEL':
                LABEL.execute(self,self.instruction)
                return
            case 'TYPE':
                TYPE.execute(self,self.instruction)
                return
            case 'DPRINT':
                DPRINT.execute(self,self.instruction)
                return
            case 'CALL':
                CALL.execute(self,self.instruction)
                return
            case 'RETURN':
                RETURN.execute(self,self.instruction)
                return
            case 'CREATEFRAME':
                CREATEFRAME.execute(self)
                return
            case 'PUSHFRAME':
                PUSHFRAME.execute(self)
                return
            case 'POPFRAME':
                POPFRAME.execute(self)
                return
            case 'AND':
                AND.execute(self,self.instruction)
                return
            case 'OR':
                OR.execute(self,self.instruction)
                return
            case 'NOT':
                NOT.execute(self,self.instruction)
                return
            case 'INT2CHAR':
                INT2CHAR.execute(self,self.instruction)
                return
            case 'STRI2INT':
                STRI2INT.execute(self,self.instruction)
                return
            case 'STRLEN':
                STRLEN.execute(self,self.instruction)
                return
            case 'CONCAT':
                CONCAT.execute(self,self.instruction)
                return
            case 'SETCHAR':
                SETCHAR.execute(self,self.instruction)
                return
            case 'GETCHAR':
                GETCHAR.execute(self,self.instruction)
                return
            case 'BREAK':
                BREAK.execute(self)

            # invalid opcode
            case _:
                exit(ErrorCodes.xml_structError)


""" Each instruction's classes inherit metods and attributes from Instruction class,
 checks operand types and values, and performs interpreting the instruction.
"""

class WRITE(Instructions):
    def init(self) -> None:
        super().__init__()

    def operandsCheck(self,instruction):
        """ Checks for right operand type"""
    
        types = ['string','var','bool','int','nil']
        self.argument1 = instruction[2]
        self.operand_type = self.get_type(self.argument1)
        if not self.operand_type in types:
            exit(ErrorCodes.typeError)

    def execute(self,instruction):
        self.instruction = instruction
        WRITE.operandsCheck(self,self.instruction)
        op1 = self.getOp1(instruction)

        if self.operand_type == 'var':
            op1 = self.get_value(op1)

        if self.operand_type == 'bool' or isinstance(op1,bool):
            if op1:
                op1 = 'true'
            else:
                op1 = 'false'

        if self.operand_type == 'nil' or op1 == 'nil':
            op1 = ''
        
        print(op1,end='')

class MOVE(Instructions):
    def __init__(self) -> None:
        super().__init__()
        
    def operandsCheck(self,instruction):
        """ Checks for right operand type"""

        types = ['var']
        self.argument1 = instruction[2]
        try:
            self.argument2 = instruction[3]
        except:
            exit(ErrorCodes.xml_structError)
        else:
            self.argument2 = instruction[3]
        self.operand_type1 = self.get_type(self.argument1)
        if not self.operand_type1 in types:
            exit(ErrorCodes.typeError)
            
        self.operand_type2 = self.get_type(self.argument2)
        types = ['var','int','bool','nil','string']
        if not self.operand_type2 in types:
            exit(ErrorCodes.typeError)

    def execute(self,instruction):
        self.instruction = instruction
        MOVE.operandsCheck(self,self.instruction)
        op1 = self.getOp1(instruction)
        op2 = self.getOp2(instruction)

        if self.operand_type2 == 'var':
            op2 = self.get_value(op2)

        if op2 is None:
            op2 = ''

        self.set_to_var(op1,op2)
        
    
class DEFVAR(Instructions):
    def __init__(self) -> None:
        super().__init__()
        
    def operandsCheck(self,instruction):
        """ Checks for right operand type"""

        types = ['var']
        try:
            self.argument1 = instruction[2]
        except:
            exit(ErrorCodes.xml_structError)
        else:
            self.operand_type = self.get_type(self.argument1)
            if not self.operand_type in types:
                exit(ErrorCodes.typeError)

    def execute(self,instruction):
        self.instruction = instruction
        DEFVAR.operandsCheck(self,self.instruction)
        op1 = self.getOp1(instruction)
        op1_frame,op1_name = op1.split('@')

        if op1_frame == 'GF':
            try:
                bool(self.GlobalList[op1_name])
            except:
                self.GlobalList[op1_name] = None
            else:
                exit(ErrorCodes.semanticError)

        if op1_frame == 'LF':
            frame = self.popFrame()
            try:
                bool(frame[op1_name])
            except:
                frame[op1_name] = None
                self.LocalList.append(frame)
            else:
                exit(ErrorCodes.semanticError)

        if op1_frame == 'TF':
            try:
                bool(self.TempList[op1_name])
            except:
                try:
                    if self.TempList['init'] == True:
                        pass   
                except:
                    exit(ErrorCodes.frameError)
                else:
                    if self.TempList['init'] == True:
                        self.TempList[op1_name] = None 
                    else:
                        exit(ErrorCodes.frameError)
            else:
                exit(ErrorCodes.semanticError)

            
    
class ADD(Instructions):
    def __init__(self) -> None:
        super().__init__()
        
    def operandsCheck(self,instruction):
        """ Checks for right operand type"""

        types = ['var']
        self.argument1 = instruction[2]
        self.argument2 = instruction[3]
        self.argument3 = instruction[4]
        self.operand_type1 = self.get_type(self.argument1)
        if not self.operand_type1 in types:
            exit(ErrorCodes.typeError)

        self.operand_type2 = self.get_type(self.argument2)
        types = ['var','int']
        if not self.operand_type2 in types:
            exit(ErrorCodes.typeError)
        
        self.operand_type3 = self.get_type(self.argument3)
        if not self.operand_type3 in types:
            exit(ErrorCodes.typeError)

    def execute(self,instruction):
        self.instruction = instruction
        ADD.operandsCheck(self,self.instruction)

        op1 = self.getOp1(instruction)
        op2 = self.getOp2(instruction)
        op3 = self.getOp3(instruction)

        if self.operand_type2 == 'var':
            op2 = self.get_value(op2)
       
        if self.operand_type3 == 'var':
            op3 = self.get_value(op3)

        if not isinstance(op2,int) or not isinstance(op3,int):
            exit(ErrorCodes.typeError)
        
        self.set_to_var(op1,op2 + op3)
        

class SUB(Instructions):
    def __init__(self) -> None:
        super().__init__()
        
    def operandsCheck(self,instruction):
        """ Checks for right operand type"""

        types = ['var']
        self.argument1 = instruction[2]
        self.argument2 = instruction[3]
        self.argument3 = instruction[4]
        self.operand_type1 = self.get_type(self.argument1)
        if not self.operand_type1 in types:
            exit(ErrorCodes.typeError)
            
        self.operand_type2 = self.get_type(self.argument2)
        types = ['var','int']
        if not self.operand_type2 in types:
            exit(ErrorCodes.typeError)
        
        self.operand_type3 = self.get_type(self.argument3)
        if not self.operand_type3 in types:
            exit(ErrorCodes.typeError)

    def execute(self,instruction):
        self.instruction = instruction
        SUB.operandsCheck(self,self.instruction)

        op1 = self.getOp1(instruction)
        op2 = self.getOp2(instruction)
        op3 = self.getOp3(instruction)

        if self.operand_type2 == 'var':
            op2 = self.get_value(op2)
       
        if self.operand_type3 == 'var':
            op3 = self.get_value(op3)

        if not isinstance(op2,int) or not isinstance(op3,int):
            exit(ErrorCodes.typeError)
        
        self.set_to_var(op1,op2 - op3)

class MUL(Instructions):
    def __init__(self) -> None:
        super().__init__()
        
    def operandsCheck(self,instruction):
        """ Checks for right operand type"""

        types = ['var']
        self.argument1 = instruction[2]
        self.argument2 = instruction[3]
        self.argument3 = instruction[4]
        self.operand_type1 = self.get_type(self.argument1)
        if not self.operand_type1 in types:
            exit(ErrorCodes.typeError)
            
        self.operand_type2 = self.get_type(self.argument2)
        types = ['var','int']
        if not self.operand_type2 in types:
            exit(ErrorCodes.typeError)
        
        self.operand_type3 = self.get_type(self.argument3)
        if not self.operand_type3 in types:
            exit(ErrorCodes.typeError)

    def execute(self,instruction):
        self.instruction = instruction
        MUL.operandsCheck(self,self.instruction)

        op1 = self.getOp1(instruction)
        op2 = self.getOp2(instruction)
        op3 = self.getOp3(instruction)

       
        if self.operand_type2 == 'var':
            op2 = self.get_value(op2)
       
        if self.operand_type3 == 'var':
            op3 = self.get_value(op3)

        if not isinstance(op2,int) or not isinstance(op3,int):
            exit(ErrorCodes.typeError)
        
        self.set_to_var(op1,op2 * op3)
        
class IDIV(Instructions):
    def __init__(self) -> None:
        super().__init__()
        
    def operandsCheck(self,instruction):
        """ Checks for right operand type"""

        types = ['var']
        self.argument1 = instruction[2]
        self.argument2 = instruction[3]
        self.argument3 = instruction[4]
        self.operand_type1 = self.get_type(self.argument1)
        if not self.operand_type1 in types:
            exit(ErrorCodes.typeError)
            
        self.operand_type2 = self.get_type(self.argument2)
        types = ['var','int']
        if not self.operand_type2 in types:
            exit(ErrorCodes.typeError)
        
        self.operand_type3 = self.get_type(self.argument3)
        if not self.operand_type3 in types:
            exit(ErrorCodes.typeError)

    def execute(self,instruction):
        self.instruction = instruction
        IDIV.operandsCheck(self,self.instruction)

        op1 = self.getOp1(instruction)
        op2 = self.getOp2(instruction)
        op3 = self.getOp3(instruction)
       
        if self.operand_type2 == 'var':
            op2 = self.get_value(op2)
       
        if self.operand_type3 == 'var':
            op3 = self.get_value(op3)

        if not isinstance(op2,int) or not isinstance(op3,int):
            exit(ErrorCodes.typeError)

        if op3 == 0:
            exit(ErrorCodes.valueError)
        
        self.set_to_var(op1,op2 // op3)
        

class LT(Instructions):
    def __init__(self) -> None:
        super().__init__()
        
    def operandsCheck(self,instruction):
        """ Checks for right operand type"""

        types = ['var']
        self.argument1 = instruction[2]
        self.argument2 = instruction[3]
        self.argument3 = instruction[4]
        self.operand_type1 = self.get_type(self.argument1)
        if not self.operand_type1 in types:
            exit(ErrorCodes.typeError)
            
        self.operand_type2 = self.get_type(self.argument2)
        types = ['var','int','bool','string']
        if not self.operand_type2 in types:
            exit(ErrorCodes.typeError)
        
        self.operand_type3 = self.get_type(self.argument3)
        if not self.operand_type3 in types:
            exit(ErrorCodes.typeError)

    def execute(self,instruction):
        self.instruction = instruction
        skip = False
        LT.operandsCheck(self,self.instruction)

        op1 = self.getOp1(instruction)
        op2 = self.getOp2(instruction)
        op3 = self.getOp3(instruction)

        if self.operand_type2 == 'var':
            op2 = self.get_value(op2)
       
        if self.operand_type3 == 'var':
            op3 = self.get_value(op3)

        if type(op2) is int:    
            if type(op3) is not int:
                exit(ErrorCodes.typeError)
        
        if isinstance(op2,bool):
            if not isinstance(op3,bool):
                exit(ErrorCodes.typeError)
        
        if isinstance(op2,str) or op2 is None:
            if not isinstance(op3,str) and (op3 is not None):
                exit(ErrorCodes.typeError)
            if op3 is None or op2 is None:
                if op2 is None and op3 is not None:
                    self.set_to_var(op1,True)
                    skip = True
                if op2 is not None and op3 is None:
                    self.set_to_var(op1,False)
                    skip = True
            else:
                for i,character in enumerate(op2):
                    if ord(op2[i]) < ord(op3[i]):
                        self.set_to_var(op1,True)
                        skip = True
                        break
                    if ord(op2[i]) > ord(op3[i]):
                        self.set_to_var(op1,False)
                        skip = True
                        break
        if not skip:
            self.set_to_var(op1,op2 < op3)

class GT(Instructions):
    def __init__(self) -> None:
        super().__init__()
        
    def operandsCheck(self,instruction):
        """ Checks for right operand type"""

        types = ['var']
        self.argument1 = instruction[2]
        self.argument2 = instruction[3]
        self.argument3 = instruction[4]
        self.operand_type1 = self.get_type(self.argument1)
        if not self.operand_type1 in types:
            exit(ErrorCodes.typeError)
            
        self.operand_type2 = self.get_type(self.argument2)
        types = ['var','int','bool','string']
        if not self.operand_type2 in types:
            exit(ErrorCodes.typeError)
        
        self.operand_type3 = self.get_type(self.argument3)
        if not self.operand_type3 in types:
            exit(ErrorCodes.typeError)

    def execute(self,instruction):
        skip = False
        self.instruction = instruction
        GT.operandsCheck(self,self.instruction)

        op1 = self.getOp1(instruction)
        op2 = self.getOp2(instruction)
        op3 = self.getOp3(instruction)

        if self.operand_type2 == 'var':
            op2 = self.get_value(op2)
       
        if self.operand_type3 == 'var':
            op3 = self.get_value(op3)

        if type(op2) is int:
            if type(op3) is not int:
                exit(ErrorCodes.typeError)
        
        if isinstance(op2,bool):
            if not isinstance(op3,bool):
                exit(ErrorCodes.typeError)
        
        if isinstance(op2,str) or op2 is None:
            if not isinstance(op3,str) and (op3 is not None):
                exit(ErrorCodes.typeError)
            if op3 is None or op2 is None:
                if op2 is None and op3 is not None:
                    self.set_to_var(op1,False)
                    skip = True
                if op2 is not None and op3 is None:
                    self.set_to_var(op1,True)
                    skip = True
            else:
                for i,character in enumerate(op2):
                    if ord(op2[i]) > ord(op3[i]):
                        self.set_to_var(op1,True)
                        skip = True
                        break
                    if ord(op2[i]) < ord(op3[i]):
                        self.set_to_var(op1,False)
                        skip = True
                        break
        if not skip:
            self.set_to_var(op1,op2 > op3)

class EQ(Instructions):
    def __init__(self) -> None:
        super().__init__()
        
    def operandsCheck(self,instruction):
        """ Checks for right operand type"""

        types = ['var']
        self.argument1 = instruction[2]
        self.argument2 = instruction[3]
        self.argument3 = instruction[4]
        self.operand_type1 = self.get_type(self.argument1)
        if not self.operand_type1 in types:
            exit(ErrorCodes.typeError)
            
        self.operand_type2 = self.get_type(self.argument2)
        types = ['var','int','bool','string','nil']
        if not self.operand_type2 in types:
            exit(ErrorCodes.typeError)
        
        self.operand_type3 = self.get_type(self.argument3)
        if not self.operand_type3 in types:
            exit(ErrorCodes.typeError)

    def execute(self,instruction):
        skip = False
        self.instruction = instruction
        EQ.operandsCheck(self,self.instruction)

        op1 = self.getOp1(instruction)
        op2 = self.getOp2(instruction)
        op3 = self.getOp3(instruction)

        if self.operand_type2 == 'var':
            op2 = self.get_value(op2)
       
        if self.operand_type3 == 'var':
            op3 = self.get_value(op3)
        
        if op2 is None:
            op2 = ''
        if op3 is None:
            op3 = ''

        if self.operand_type2 == 'nil' or self.operand_type3 == 'nil' or op2 == 'nil' or op3 == 'nil':
            if self.operand_type2 == 'nil' and self.operand_type3 == 'nil':
                value = True

            elif self.operand_type2 == 'var' and self.operand_type3 == 'var':
                if op2 == op3:
                    value = True
                else:
                    value = False

            else:
                value = False

            self.set_to_var(op1,value)
            return
        
        if type(op2) is int:
            if type(op3) is not int and op3 != 'nil':
                exit(ErrorCodes.typeError)
        
        if isinstance(op2,bool):
            if not isinstance(op3,bool) and op3 != 'nil':
                exit(ErrorCodes.typeError)
        
        if isinstance(op2,str) or op2 is None:
            if not isinstance(op3,str) and (op3 is not None):
                exit(ErrorCodes.typeError)
            if op3 is None or op2 is None:
                if op2 is None and op3 is not None:
                    self.set_to_var(op1,False)
                    skip = True
                if op2 is not None and op3 is None:
                    self.set_to_var(op1,False)
                    skip = True
            
        if not skip:
            self.set_to_var(op1,op2 == op3)

class LABEL(Instructions):
    def __init__(self) -> None:
        super().__init__()
        
    def operandsCheck(self,instruction):
        """ Checks for right operand type"""

        types = ['label']
        self.argument1 = instruction[2]
        self.operand_type = self.get_type(self.argument1)
        if not self.operand_type in types:
            exit(55)

    def execute(self,instruction):
        self.instruction = instruction
        LABEL.operandsCheck(self,self.instruction)
        op1 = self.getOp1(self.instruction)
        self.label = self.xml_instruction.getLabel()
        return

class JUMP(Instructions):
    def __init__(self) -> None:
        super().__init__()
        
    def operandsCheck(self,instruction):
        """ Checks for right operand type"""

        types = ['label']
        self.argument1 = instruction[2]
        self.operand_type = self.get_type(self.argument1)
        if not self.operand_type in types:
            exit(ErrorCodes.typeError)

    def execute(self,instruction):
        self.instruction = instruction
        self.label = self.xml_instruction.getLabel()
        JUMP.operandsCheck(self,self.instruction)

        op1 = self.getOp1(instruction)
        try:
            self.order = self.label[op1]
        except:
            exit(ErrorCodes.semanticError)
        else:
            index = self.label[op1]
            self.order = self.operandsSort.index(index)
            

class JUMPIFEQ(Instructions):
    def __init__(self) -> None:
        super().__init__()
        
    def operandsCheck(self,instruction):
        """ Checks for right operand type"""

        types = ['label']
        
        self.argument1 = instruction[2]
        self.argument2 = instruction[3]
        self.argument3 = instruction[4]
        self.operand_type1 = self.get_type(self.argument1)
        if not self.operand_type1 in types:
            exit(ErrorCodes.typeError)
            
        self.operand_type2 = self.get_type(self.argument2)
        types = ['var','int','bool','string','nil']
        if not self.operand_type2 in types:
            exit(ErrorCodes.typeError)
        
        self.operand_type3 = self.get_type(self.argument3)
        if not self.operand_type3 in types:
            exit(ErrorCodes.typeError)

    def execute(self,instruction):
        self.instruction = instruction
        self.label = self.xml_instruction.getLabel()
        JUMPIFEQ.operandsCheck(self,self.instruction)
        op1 = self.getOp1(instruction)  
        op2 = self.getOp2(instruction)
        op3 = self.getOp3(instruction)

        if self.operand_type2 == 'var':
            op2 = self.get_value(op2)
       
        if self.operand_type3 == 'var':
            op3 = self.get_value(op3)
        
        if op2 is None:
            op2 = ''
        if op3 is None:
            op3 = ''

        if self.operand_type2 == 'nil' or self.operand_type3 == 'nil' or op2 == 'nil' or op3 == 'nil':
            if self.operand_type2 == 'nil' and self.operand_type3 == 'nil':
                value = True

            elif self.operand_type2 == 'var' and self.operand_type3 == 'var':
                if op2 == op3:
                    value = True
                else:
                    value = False

            else:
                value = False

            try:
                index = self.label[op1]
            except:
                exit(ErrorCodes.semanticError)
            else:
                if value:
                    index = self.label[op1]
                    self.order = self.operandsSort.index(index)
                    return
                else:
                    return
        
        if type(op2) is int:
            if type(op3) is not int:
                exit(ErrorCodes.typeError)
        
        if isinstance(op2,bool):
            if not isinstance(op3,bool):
                exit(ErrorCodes.typeError)
        
        if isinstance(op2,str):
            if not isinstance(op3,str):
                exit(ErrorCodes.typeError)
        
        if op2 is None or op3 is None:
            value = False
        else:
            value = (op2 == op3)
        
        try:
            index = self.label[op1]
        except:
            exit(ErrorCodes.semanticError)
        else:
            if value:
                index = self.label[op1]
                self.order = self.operandsSort.index(index)
                
        
class JUMPIFNEQ(Instructions):
    def __init__(self) -> None:
        super().__init__()
        
    def operandsCheck(self,instruction):
        """ Checks for right operand type"""

        types = ['label']
        self.argument1 = instruction[2]
        self.argument2 = instruction[3]
        self.argument3 = instruction[4]
        self.operand_type1 = self.get_type(self.argument1)
        if not self.operand_type1 in types:
            exit(ErrorCodes.typeError)
            
        self.operand_type2 = self.get_type(self.argument2)
        types = ['var','int','bool','string','nil']
        if not self.operand_type2 in types:
            exit(ErrorCodes.typeError)
        
        self.operand_type3 = self.get_type(self.argument3)
        if not self.operand_type3 in types:
            exit(ErrorCodes.typeError)

    def execute(self,instruction):
        self.instruction = instruction
        self.label = self.xml_instruction.getLabel()
        JUMPIFNEQ.operandsCheck(self,self.instruction)

        op1 = self.getOp1(instruction)
        op2 = self.getOp2(instruction)
        op3 = self.getOp3(instruction)

        if self.operand_type2 == 'var':
            op2 = self.get_value(op2)
       
        if self.operand_type3 == 'var':
            op3 = self.get_value(op3)
        
        if op2 is None:
            op2 = ''
        if op3 is None:
            op3 = ''

        if self.operand_type2 == 'nil' or self.operand_type3 == 'nil' or op2 == 'nil' or op3 == 'nil':
            if self.operand_type2 == 'nil' and self.operand_type3 == 'nil':
                value = True

            elif self.operand_type2 == 'var' and self.operand_type3 == 'var':
                if op2 == op3:
                    value = True
                else:
                    value = False

            else:
                value = False

            try:
                index = self.label[op1]
            except:
                exit(ErrorCodes.semanticError)
            else:
                if not value:
                    index = self.label[op1]
                    self.order = self.operandsSort.index(index)
                    return
                else:
                    return
        
        if type(op2) is int:
            if type(op3) is not int:
                exit(ErrorCodes.typeError)
        
        if isinstance(op2,bool):
            if not isinstance(op3,bool):
                exit(ErrorCodes.typeError)
        
        if isinstance(op2,str):
            if not isinstance(op3,str):
                exit(ErrorCodes.typeError)
        
        if op2 is None or op3 is None:
            value = False
        else:
            value = (op2 == op3)
        
        try:
            index = self.label[op1]
        except:
            exit(ErrorCodes.semanticError)
        else:
            if not value:
                index = self.label[op1]
                self.order = self.operandsSort.index(index)
        

class POPS(Instructions):
    def __init__(self) -> None:
        super().__init__()
        
    def operandsCheck(self,instruction):
        """ Checks for right operand type"""

        types = ['var']
        self.argument1 = instruction[2]
        self.operand_type = self.get_type(self.argument1)
        if not self.operand_type in types:
            exit(ErrorCodes.typeError)

    def execute(self,instruction):
        self.instruction = instruction
        POPS.operandsCheck(self, self.instruction)

        op1 = self.getOp1(instruction)
        op1_frame, op1_name = op1.split('@')

        self.set_to_var(op1, self.popStack())

class PUSHS(Instructions):
    def __init__(self) -> None:
        super().__init__()
        
    def operandsCheck(self,instruction):
        """ Checks for right operand type"""

        types = ['var','int','bool','string','nil']
        self.argument1 = instruction[2]
        self.operand_type = self.get_type(self.argument1)
        if not self.operand_type in types:
            exit(ErrorCodes.typeError)

    def execute(self,instruction):
        self.instruction = instruction
        PUSHS.operandsCheck(self, self.instruction)

        op1 = self.getOp1(instruction)

        if self.operand_type == 'var':
            op1 = self.get_value(op1)

        self.pushStack(op1)
       
class EXIT(Instructions):
    def __init__(self) -> None:
        super().__init__()
        
    def operandsCheck(self,instruction):
        """ Checks for right operand type"""

        types = ['var','int']
        self.argument1 = instruction[2]
        self.operand_type = self.get_type(self.argument1)
        if not self.operand_type in types:
            exit(ErrorCodes.typeError)

    def execute(self,instruction):
        self.instruction = instruction
        EXIT.operandsCheck(self, self.instruction)

        op1 = self.getOp1(instruction)

        if self.operand_type == 'var':
            op1 = self.get_value(op1)
        
        if type(op1) != int:
            exit(ErrorCodes.typeError)

        if op1 < 0 or op1 > 49:
            exit(ErrorCodes.valueError)

        exit(op1)

class DPRINT(Instructions):
    def __init__(self) -> None:
        super().__init__()
        
    def operandsCheck(self,instruction):
        """ Checks for right operand type"""

        types = ['var','int','bool','string','nil']
        self.argument1 = instruction[2]
        self.operand_type = self.get_type(self.argument1)
        if not self.operand_type in types:
            exit(ErrorCodes.typeError)

    def execute(self,instruction):
        self.instruction = instruction
        DPRINT.operandsCheck(self, self.instruction)

        op1 = self.getOp1(instruction)
        
        if self.operand_type == 'var':
            op1 = self.get_value(op1)

        if self.operand_type == 'bool':
            if op1 == 'true':
                op1 = True
            else:
                op1 = False

        sys.stderr.write(op1)

class BREAK(Instructions):
    def __init__(self) -> None:
        super().__init__()
    def execute(self):
        output = "Instruction order: " + str(self.order) + '\n'
        sys.stderr.write(output)

class CALL(Instructions):
    def __init__(self) -> None:
        super().__init__()
        
    def operandsCheck(self,instruction):
        """ Checks for right operand type"""

        types = ['label']
        self.argument1 = instruction[2]
        self.operand_type = self.get_type(self.argument1)
        if not self.operand_type in types:
            exit(ErrorCodes.typeError)

    def execute(self,instruction):
        self.instruction = instruction
        self.label = self.xml_instruction.getLabel()
        CALL.operandsCheck(self,self.instruction)

        op1 = self.getOp1(instruction)
        self.callStack.append(self.order)
        try:
            index = self.label[op1]
        except:
            exit(ErrorCodes.semanticError)
        else:
            self.order = self.label[op1]

class RETURN(Instructions):
    def __init__(self) -> None:
        super().__init__()

    def execute(self,instruction):
        self.instruction = instruction

        if not bool(self.callStack):
            exit(ErrorCodes.existError)

        self.order = self.callStack.pop()

class CREATEFRAME(Instructions):
    def __init__(self) -> None:
        super().__init__()

    def execute(self):
        self.TempList['init'] = True

class PUSHFRAME(Instructions):
    def __init__(self) -> None:
        super().__init__()
    
    def execute(self):
        try:
            if self.TempList['init'] == True:
                pass
        except:
            exit(ErrorCodes.frameError)
        else:
            if self.TempList['init'] == False:
                exit(ErrorCodes.frameError)
            else:
                self.LocalList.append(self.TempList)
        self.TempList = {}
        self.TempList['init'] = False
        

class POPFRAME(Instructions):
    def __init__(self) -> None:
        super().__init__()

    def execute(self):
        if not bool(self.LocalList):
            exit(ErrorCodes.frameError)

        self.TempList = self.LocalList.pop()
        self.TempList['init'] = True

class AND(Instructions):
    def __init__(self) -> None:
        super().__init__()

    def operandsCheck(self,instruction):
        """ Checks for right operand type"""

        types = ['var']
        self.argument1 = instruction[2]
        self.argument2 = instruction[3]
        self.argument3 = instruction[4]
        self.operand_type1 = self.get_type(self.argument1)
        if not self.operand_type1 in types:
            exit(ErrorCodes.typeError)
            
        self.operand_type2 = self.get_type(self.argument2)
        types = ['var','bool']
        if not self.operand_type2 in types:
            exit(ErrorCodes.typeError)
        
        self.operand_type3 = self.get_type(self.argument3)
        if not self.operand_type3 in types:
            exit(ErrorCodes.typeError)

    def execute(self,instruction):
        self.instruction = instruction
        AND.operandsCheck(self,self.instruction)

        op1 = self.getOp1(instruction)
        op2 = self.getOp2(instruction)
        op3 = self.getOp3(instruction)

        if self.operand_type2 == 'var':
            op2 = self.get_value(op2)
       
        if self.operand_type3 == 'var':
            op3 = self.get_value(op3)
       

        if not isinstance(op2,bool) or not isinstance(op3,bool):
            exit(ErrorCodes.typeError)
        
        self.set_to_var(op1,op2 and op3)

class OR(Instructions):
    def __init__(self) -> None:
        super().__init__()

    def operandsCheck(self,instruction):
        """ Checks for right operand type"""

        types = ['var']
        self.argument1 = instruction[2]
        self.argument2 = instruction[3]
        self.argument3 = instruction[4]
        self.operand_type1 = self.get_type(self.argument1)
        if not self.operand_type1 in types:
            exit(ErrorCodes.typeError)
            
        self.operand_type2 = self.get_type(self.argument2)
        types = ['var','bool']
        if not self.operand_type2 in types:
            exit(ErrorCodes.typeError)
        
        self.operand_type3 = self.get_type(self.argument3)
        if not self.operand_type3 in types:
            exit(ErrorCodes.typeError)

    def execute(self,instruction):
        self.instruction = instruction
        OR.operandsCheck(self,self.instruction)

        op1 = self.getOp1(instruction)
        op2 = self.getOp2(instruction)
        op3 = self.getOp3(instruction)

        if self.operand_type2 == 'var':
            op2 = self.get_value(op2)
       
        if self.operand_type3 == 'var':
            op3 = self.get_value(op3)

        if not isinstance(op2,bool) or not isinstance(op3,bool):
            exit(ErrorCodes.typeError)
        
        self.set_to_var(op1,op2 or op3)

class NOT(Instructions):
    def __init__(self) -> None:
        super().__init__()

    def operandsCheck(self,instruction):
        """ Checks for right operand type"""

        types = ['var']
        self.argument1 = instruction[2]
        self.argument2 = instruction[3]
       
        self.operand_type1 = self.get_type(self.argument1)
        if not self.operand_type1 in types:
            exit(ErrorCodes.typeError)
            
        self.operand_type2 = self.get_type(self.argument2)
        types = ['var','bool']
        if not self.operand_type2 in types:
            exit(ErrorCodes.typeError)
        

    def execute(self,instruction):
        self.instruction = instruction
        NOT.operandsCheck(self,self.instruction)

        op1 = self.getOp1(instruction)
        op2 = self.getOp2(instruction)

        if self.operand_type2 == 'var':
            op2 = self.get_value(op2)
       
        if not isinstance(op2,bool):
            exit(ErrorCodes.typeError)
        
        self.set_to_var(op1,not op2)


class READ(Instructions):
    def __init__(self) -> None:
        super().__init__()
        
    def operandsCheck(self,instruction):
        """ Checks for right operand type"""

        types = ['var']
        self.argument1 = instruction[2]
        self.argument2 = instruction[3]
        self.operand_type1 = self.get_type(self.argument1)
        if not self.operand_type1 in types:
            exit(ErrorCodes.typeError)
        
        types = ['type']
        self.operand_type2 = self.get_type(self.argument2)
        if not self.operand_type2 in types:
            exit(ErrorCodes.typeError)

    def execute(self,instruction):
        self.instruction = instruction
        READ.operandsCheck(self,self.instruction)
        op1 = self.getOp1(instruction)
        op2_name = self.getOp2(instruction)
        op1_frame,op1_name = op1.split('@')
        if op1_frame == "GF":
            self.checkExist(op1_name,1)
        if op1_frame == "LF":
            self.checkExist(op1_name,2)
        if op1_frame == "TF":
            self.checkExist(op1_name,3)

        stdin = Arguments.parse(self,2)
        if stdin is None:
            value = input()
            file = False
        else:
            file = True
            for value in fileinput.input(files=stdin):
                if value is None:
                    value = 'nil'
                self.inputList.append(value)

        if file:
            try:
                value = self.inputList[self.line]
            except:
                value = 'nil'
            else:
                value = self.inputList[self.line]
                if value is None:
                    value = ''
                value = value.strip()
            self.line +=1

        if op2_name not in ['string','int','bool']:
            exit(ErrorCodes.typeError)

        if op2_name == 'int':
            try:
                value = int(value)
            except:
                value = 'nil'
            else:
                value = int(value)
        
        if op2_name == 'bool':
            if value == 'true':
                value = 'true'
            else:
                value = 'false'

        if op2_name == 'string':
            if not isinstance(value,str):
                value = 'nil'

        if value is None:
            value = None
        
        self.set_to_var(op1,value)

class TYPE(Instructions):
    def __init__(self) -> None:
        super().__init__()

    def operandsCheck(self,instruction):
        """ Checks for right operand type"""

        types = ['var']
        self.argument1 = instruction[2]
        self.argument2 = instruction[3]
        
        self.operand_type1 = self.get_type(self.argument1)

        if not self.operand_type1 in types:
            exit(ErrorCodes.typeError)

        types = ['var','string','bool','nil','int']
        self.operand_type2 = self.get_type(self.argument2)

        if not self.operand_type2 in types:
            exit(ErrorCodes.typeError)

    def execute(self,instruction):
        self.instruction = instruction
        TYPE.operandsCheck(self,self.instruction)
        op1 = self.getOp1(self.instruction)
        op2 = self.getOp2(self.instruction)

        if self.operand_type2 == 'var':
            op2_frame,op2_name = op2.split('@')
            if op2_frame == 'GF':
                self.checkExist(op2_name,1)
                op2 = self.GlobalList[op2_name]

            elif op2_frame == 'LF':
                self.checkExist(op2_name,2)
                frame = self.getFrame()
                op2 = frame[op2_name]

            elif op2_frame == 'TF':
                try:
                    if self.TempList['init'] == False:
                        pass
                except:
                    exit(ErrorCodes.frameError)
                else:
                    if self.TempList['init'] == False:
                        exit(ErrorCodes.frameError)
                self.checkExist(op2_name,3)
                frame = self.TempList
                op2 = frame[op2_name]
        
        if self.operand_type2 == 'nil' or op2 == 'nil':
            op2 = 'nil'
            self.set_to_var(op1,op2)
            return
            
        if op2 == None:
            op2 = ''
        
        if op2 != '':
            op2 = type(op2)

        if op2 == str and op2 != '':
            op2 = 'string'

        if op2 == int:
            op2 = 'int'

        if op2 == bool:
            op2 = 'bool'

        self.set_to_var(op1,op2)

class INT2CHAR(Instructions):
    def __init__(self) -> None:
        super().__init__()
        
    def operandsCheck(self,instruction):
        """ Checks for right operand type"""

        types = ['var']
        self.argument1 = instruction[2]
        self.argument2 = instruction[3]
    
        self.operand_type1 = self.get_type(self.argument1)

        if not self.operand_type1 in types:
            exit(ErrorCodes.typeError)

        self.operand_type2 = self.get_type(self.argument2)

        types = ['var','int']
        if not self.operand_type2 in types:
            exit(ErrorCodes.typeError)
  
    def execute(self,instruction):
        self.instruction = instruction
        INT2CHAR.operandsCheck(self,self.instruction)

        op1 = self.getOp1(instruction)
        op2 = self.getOp2(instruction)

        if self.operand_type2 == 'var':
            op2 = self.get_value(op2)

        if type(op2) != int:
            exit(ErrorCodes.typeError)
        
        try:
            chr(op2)
        except:
            exit(ErrorCodes.stringError)
        else:
            self.set_to_var(op1,chr(op2))

class CONCAT(Instructions):
    def __init__(self) -> None:
        super().__init__()

    def operandsCheck(self,instruction):
        """ Checks for right operand type"""

        types = ['var']
        self.argument1 = instruction[2]
        self.argument2 = instruction[3]
        self.argument3 = instruction[4]
        self.operand_type1 = self.get_type(self.argument1)

        if not self.operand_type1 in types:
            exit(ErrorCodes.typeError)

        self.operand_type2 = self.get_type(self.argument2)

        types = ['var','string']
        if not self.operand_type2 in types:
            exit(ErrorCodes.typeError)
        
        self.operand_type3 = self.get_type(self.argument3)

        if not self.operand_type3 in types:
            exit(ErrorCodes.typeError)

    def execute(self,instruction):
        self.instruction = instruction
        CONCAT.operandsCheck(self,self.instruction)

        op1 = self.getOp1(instruction)
        op2 = self.getOp2(instruction)
        op3 = self.getOp3(instruction)

        if self.operand_type2 == 'var':
            op2 = self.get_value(op2)
       
        if self.operand_type3 == 'var':
            op3 = self.get_value(op3)
        
        if op3 is None:
            op3 = ''
        if op2 is None:
            op2 = ''

        if not isinstance(op2,str) or not isinstance(op3,str):
                exit(ErrorCodes.typeError)
        
        if op2 == 'nil' or op3 == 'nil':
            exit(ErrorCodes.typeError)
        
        self.set_to_var(op1,op2 + op3)

class STRLEN(Instructions):
    def __init__(self) -> None:
        super().__init__()

    def operandsCheck(self,instruction):
        """ Checks for right operand type"""

        types = ['var']
        self.argument1 = instruction[2]
        self.argument2 = instruction[3]

        self.operand_type1 = self.get_type(self.argument1)

        if not self.operand_type1 in types:
            exit(ErrorCodes.typeError)

        self.operand_type2 = self.get_type(self.argument2)

        types = ['var','string']
        if not self.operand_type2 in types:
            exit(ErrorCodes.typeError)
       
    def execute(self,instruction):
        self.instruction = instruction
        STRLEN.operandsCheck(self,self.instruction)

        op1 = self.getOp1(instruction)
        op2 = self.getOp2(instruction)

        if self.operand_type2 == 'var':
            op2 = self.get_value(op2)

        if not isinstance(op2,str) and op2 != None:
            exit(ErrorCodes.typeError)
        if op2 == 'nil':
            exit(ErrorCodes.typeError)
        
        try:
            value = len(op2)
        except:
            value = 0
        else:
            value = len(op2)
        self.set_to_var(op1,value)

class GETCHAR(Instructions):
    def __init__(self) -> None:
        super().__init__()

    def operandsCheck(self,instruction):
        """ Checks for right operand type"""

        types = ['var']
        self.argument1 = instruction[2]
        self.argument2 = instruction[3]
        self.argument3 = instruction[4]
        self.operand_type1 = self.get_type(self.argument1)

        if not self.operand_type1 in types:
            exit(ErrorCodes.typeError)

        self.operand_type2 = self.get_type(self.argument2)

        types = ['var','string']
        if not self.operand_type2 in types:
            exit(ErrorCodes.typeError)
        
        types = ['var','int']
        self.operand_type3 = self.get_type(self.argument3)

        if not self.operand_type3 in types:
            exit(ErrorCodes.typeError)

    def execute(self,instruction):
        self.instruction = instruction
        GETCHAR.operandsCheck(self,self.instruction)

        op1 = self.getOp1(instruction)
        op2 = self.getOp2(instruction)
        op3 = self.getOp3(instruction)

        if self.operand_type2 == 'var':
            op2 = self.get_value(op2)
       
        if self.operand_type3 == 'var':
            op3 = self.get_value(op3)

        if op2 == 'nil':
            exit(ErrorCodes.typeError)

        if op3 >= len(op2) or op3 < 0:
            exit(ErrorCodes.stringError)

        value = op2[op3]
        
        self.set_to_var(op1,value)

class SETCHAR(Instructions):
    def __init__(self) -> None:
        super().__init__()
    
    def operandsCheck(self,instruction):
        """ Checks for right operand type"""

        types = ['var']
        self.argument1 = instruction[2]
        self.argument2 = instruction[3]
        self.argument3 = instruction[4]
        self.operand_type1 = self.get_type(self.argument1)

        if not self.operand_type1 in types:
            exit(ErrorCodes.typeError)

        self.operand_type2 = self.get_type(self.argument2)

        types = ['var','int']
        if not self.operand_type2 in types:
            exit(ErrorCodes.typeError)
        
        types = ['var','string']
        self.operand_type3 = self.get_type(self.argument3)

        if not self.operand_type3 in types:
            exit(ErrorCodes.typeError)

    def execute(self,instruction):
        self.instruction = instruction
        SETCHAR.operandsCheck(self,self.instruction)

        op1 = self.getOp1(instruction)
        op2 = self.getOp2(instruction)
        op3 = self.getOp3(instruction)

        op1_string = self.get_value(op1)
        
        if self.operand_type2 == 'var':
            op2 = self.get_value(op2)
       
        if self.operand_type3 == 'var':
            op3 = self.get_value(op3)

        if not isinstance(op1_string,str):
            exit(ErrorCodes.typeError)
        if op3 == 'nil' or op1_string == 'nil':
            exit(ErrorCodes.typeError)
        if op3 == None:
            exit(ErrorCodes.stringError)

        if len(op3) > 1:
            op3 = op3[0]
        if op2 >= len(op1) or op2 < 0:
            exit(ErrorCodes.stringError)
        
        replace = op1_string[op2]
    
        op1_string = op1_string.replace(replace, op3)
        
        self.set_to_var(op1,op1_string)

class STRI2INT(Instructions):
    def __init__(self) -> None:
        super().__init__()

    def operandsCheck(self,instruction):
        """ Checks for right operand type"""

        types = ['var']
        self.argument1 = instruction[2]
        self.argument2 = instruction[3]
        self.argument3 = instruction[4]
        self.operand_type1 = self.get_type(self.argument1)

        if not self.operand_type1 in types:
            exit(ErrorCodes.typeError)

        self.operand_type2 = self.get_type(self.argument2)

        types = ['var','string']
        if not self.operand_type2 in types:
            exit(ErrorCodes.typeError)
        
        types = ['var','int']
        self.operand_type3 = self.get_type(self.argument3)

        if not self.operand_type3 in types:
            exit(ErrorCodes.typeError)

    def execute(self,instruction):
        self.instruction = instruction
        STRI2INT.operandsCheck(self,self.instruction)

        op1 = self.getOp1(instruction)
        op2 = self.getOp2(instruction)
        op3 = self.getOp3(instruction)

        if self.operand_type2 == 'var':
            op2 = self.get_value(op2)
       
        if self.operand_type3 == 'var':
            op3 = self.get_value(op3)

        if op2 == 'nil':
            exit(ErrorCodes.typeError)

        if op3 >= len(op2) or op3 < 0:
            exit(ErrorCodes.stringError)

        value = op2[op3]
    
        
        self.set_to_var(op1,ord(value))
    
         
class __main__:
    init = Run()
    while True:
        init.run_instruction()
    
