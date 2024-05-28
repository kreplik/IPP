<?php

$SYNTAX_ERROR = 23; # argument's syntax error
$HEADER_ERROR = 21; # header not found
$COMMAND_LINE_ERROR = 10; # too much parameters
$OPCODE_ERROR = 22; # unknown OPCODE

ini_set('display_errors', 'stderr');

    if($argc > 2)
    {
        # too much  parameters set
        exit($COMMAND_LINE_ERROR);
    }
    else if($argc == 2)
    {
        if($argv[1] == "--help")
        {
            # prints help
        echo("Help: Skript typu filtr (parse.php v jazyce PHP 8.1)
        nacte ze standardniho vstupu zdrojovy kod v IPPcode23,
        zkontroluje lexikalni a syntaktickou spravnost kodu
        a vypise na standardni vystup XML reprezentaci programu.\n");
        exit(0);
        }
        else{
            # found unknown parameter
            exit($COMMAND_LINE_ERROR);
        }
    }

    $xw = xmlwriter_open_memory();
    xmlwriter_set_indent($xw, 1);
    $res = xmlwriter_set_indent_string($xw, ' ');
    xmlwriter_start_document($xw, '1.0', 'UTF-8');
    xmlwriter_start_element($xw, 'program');
    xmlwriter_start_attribute($xw, 'language');
    xmlwriter_text($xw, 'IPPcode23');
    xmlwriter_end_attribute($xw);

$counter = 0; # for instruction's order
$header = false; # checks if the header was found
$head = 0; # checks if there is more than one header
$comment = false; # checks for comment written on single line

/** 
* Function that checks if the argument matches with the selected regular expression
* and prints argument's parameters and their types using XMLWriter library.
* @param $argument A string that refers to argument which is about to be checked.
* @param $arg_position Number from 1 to 3 that specifies the position of argument.
* @param $regex Number from 1 to 4 to specify which regular expression has to string match with.
* @param $memory Memory for XMLWriter library
*/
function printing_args($argument, $arg_position, $regex, $memory) : void {
    #regular expressions 
    $var = '/^(GF|LF|TF)+@([a-zA-Z\_\$\-\&\;\%\*\!\?][0-9]*)+/m';
    $int = "/^(int)\@[(\-|\+)]?((0[xX]?)?[0-9a-fA-F])?[0-9]+/m";
    $bool = "/^(bool)\@(true|false)$/u";
    $string = '/^(string)\@([a-žA-Z0-9\$\-\&\;\/\%\*\!\?\,\§\<\>\=\(\)]?([\\\\\\\\]?[0-9]{3})*)*/m';
    $label = "/^(?!int@|bool@|string@|nil@|GF@|LF@|TF@)[a-zA-Z0-9\_\$\-\&\;\%\*\!\?]+/m";
    $null = "/^nil\@nil$/";
    $type = "/(int|bool|string)$/";

    
    if($regex == 1) #regex for variable
    {
        # stores matched characters in array $matches
        preg_match_all($var, $argument, $matches, PREG_SET_ORDER); 
        # checks if the array contains the same amount of characters as argument
        if((strlen($matches[0][0]) == strlen($argument)) && strlen($argument) != 0)
        {
            xmlwriter_start_element($memory, 'arg1');
            xmlwriter_start_attribute($memory, 'type');
            xmlwriter_text($memory, 'var');
            xmlwriter_end_attribute($memory);
            xmlwriter_text($memory, $argument);
            xmlwriter_end_element($memory);
        }
        else{
            exit($GLOBALS['SYNTAX_ERROR']); # argument does not match with selected regex
        }
        return;
    } 

    if($regex == 2) #regex for constant
    {
        preg_match_all($var, $argument,$matches, PREG_SET_ORDER);

        if((strlen($matches[0][0]) == strlen($argument)) && strlen($argument) != 0)
        {
            if($arg_position == 1){
                xmlwriter_start_element($memory, 'arg1');
            }
            if($arg_position == 2){
                xmlwriter_start_element($memory, 'arg2');
            }
            if($arg_position == 3){
                xmlwriter_start_element($memory, 'arg3');
            }
            xmlwriter_start_attribute($memory, 'type');
            xmlwriter_text($memory, 'var');
            xmlwriter_end_attribute($memory);
            xmlwriter_text($memory, $argument);
            xmlwriter_end_element($memory);
            return;
        }

        $param = explode('@', $argument); # to print value after '@'
        preg_match_all($int, $argument,$matches, PREG_SET_ORDER);

        if((strlen($matches[0][0]) == strlen($argument)) && strlen($argument) != 0)
        {
            if($arg_position == 1){
                xmlwriter_start_element($memory, 'arg1');
            }
            if($arg_position == 2){
                xmlwriter_start_element($memory, 'arg2');
            }
            if($arg_position == 3){
                xmlwriter_start_element($memory, 'arg3');
            }
            xmlwriter_start_attribute($memory, 'type');
            xmlwriter_text($memory, 'int');
            xmlwriter_end_attribute($memory);
            xmlwriter_text($memory, $param[1]);
            xmlwriter_end_element($memory);
            return;
        }

        preg_match_all($bool, $argument,$matches, PREG_SET_ORDER);

        if((strlen($matches[0][0]) == strlen($argument)) && strlen($argument) != 0)
        {
            if($arg_position == 1){
                xmlwriter_start_element($memory, 'arg1');
            }
            if($arg_position == 2){
                xmlwriter_start_element($memory, 'arg2');
            }
            if($arg_position == 3){
                xmlwriter_start_element($memory, 'arg3');
            }
            xmlwriter_start_attribute($memory, 'type');
            xmlwriter_text($memory, 'bool');
            xmlwriter_end_attribute($memory);
            xmlwriter_text($memory, $param[1]);
            xmlwriter_end_element($memory);
            return;
        }
        
        preg_match_all($string, $argument,$matches, PREG_SET_ORDER);

        if((strlen($matches[0][0]) == strlen($argument)) && strlen($argument) != 0)
        {
            if($arg_position == 1){
                xmlwriter_start_element($memory, 'arg1');
            }
            if($arg_position == 2){
                xmlwriter_start_element($memory, 'arg2');
            }
            if($arg_position == 3){
                xmlwriter_start_element($memory, 'arg3');
            }
            xmlwriter_start_attribute($memory, 'type');
            xmlwriter_text($memory, 'string');
            xmlwriter_end_attribute($memory);
            xmlwriter_text($memory,$param[1]);
            xmlwriter_end_element($memory);
            return;
        }

        preg_match_all($null, $argument,$matches, PREG_SET_ORDER);

        if((strlen($matches[0][0]) == strlen($argument)) && strlen($argument) != 0)
        {
            if($arg_position == 1){
                xmlwriter_start_element($memory, 'arg1');
            }
            if($arg_position == 2){
                xmlwriter_start_element($memory, 'arg2');
            }
            if($arg_position == 3){
                xmlwriter_start_element($memory, 'arg3');
            }
            xmlwriter_start_attribute($memory, 'type');
            xmlwriter_text($memory, 'nil');
            xmlwriter_end_attribute($memory);
            xmlwriter_text($memory, $param[1]);
            xmlwriter_end_element($memory);
            return;
        }
    }

    if($regex == 3) #regex for type
    {
        preg_match_all($type, $argument,$matches, PREG_SET_ORDER);
        if((strlen($matches[0][0]) == strlen($argument)) && strlen($argument) != 0)
        {
            if($arg_position == 1){
                xmlwriter_start_element($memory, 'arg1');
            }
            if($arg_position == 2){
                xmlwriter_start_element($memory, 'arg2');
            }
            if($arg_position == 3){
                xmlwriter_start_element($memory, 'arg3');
            }
            xmlwriter_start_attribute($memory, 'type');
            xmlwriter_text($memory, 'type');
            xmlwriter_end_attribute($memory);
            xmlwriter_text($memory, $argument);
            xmlwriter_end_element($memory);
        }
        else{
            exit($GLOBALS['SYNTAX_ERROR']);
        }
        return;
    }

    if($regex == 4) #regex for label
    {
        preg_match_all($label, $argument,$matches, PREG_SET_ORDER);

        if((strlen($matches[0][0]) == strlen($argument)) && strlen($argument) != 0)
        {
            if($arg_position == 1){
                xmlwriter_start_element($memory, 'arg1');
            }
            if($arg_position == 2){
                xmlwriter_start_element($memory, 'arg2');
            }
            if($arg_position == 3){
                xmlwriter_start_element($memory, 'arg3');
            }
            xmlwriter_start_attribute($memory, 'type');
            xmlwriter_text($memory, 'label');
            xmlwriter_end_attribute($memory);
            xmlwriter_text($memory, $argument);
            xmlwriter_end_element($memory);        
        }
        else{       
            exit($GLOBALS['SYNTAX_ERROR']);
        }
        return;
    }       
     #argument does not match with any of the regular expressions
     exit($GLOBALS['SYNTAX_ERROR']);
}

/**
 * Prints instruction's opcode and order using XMLWriter library;
 * @param $order Order of the instruction.
 * @param $opcode Opcode of the instruction.
 * @param $memory Memory for XMLWriter library.
 */
function opcode($order, $opcode, $memory) : void
{
    xmlwriter_start_element($memory,'instruction');
    xmlwriter_start_attribute($memory, 'order');
    xmlwriter_text($memory, $order);
    xmlwriter_start_attribute($memory, 'opcode');
    xmlwriter_text($memory, $opcode);
    xmlwriter_end_attribute($memory);
    return;
}

while($line = fgets(STDIN))
{
# array of instruction's opcode and arguments
$separated = preg_split('/\s+/', trim($line));
$comment_line = str_split($separated[0]);

if($comment_line[0] != '#' && !(empty($separated[0]))){
    # the line is not empty and is not a comment
    if($header == false){
        # looking for header
        $separated = explode('#', $separated[0]);

        if(strtoupper($separated[0]) == ".IPPCODE23")
        {
            # found a header
            $header = true;
        }
        else{
            # header was not found
            exit($HEADER_ERROR);
        }
    }
}
else if($comment_line[0] == '#' || (empty($separated[0]))){
    # line starts with comment or is empty
        $comment = true;
}

# For instructions, that have only 2 arguments, to skip printing the 3rd one.
$skip = false;

# For instructions, that shares the types of arguments.
# Is used to give printing_args() the right parameter for choosing regular expression.
$regex_code = 1;

switch($separated[0] = strtoupper($separated[0])){
    # OPCODES
    case 'CALL':
    case 'JUMP':
    case 'LABEL':
        $regex_code +=2;
    case 'EXIT':
    case 'PUSHS':
    case 'DPRINT':
    case 'WRITE':
        $regex_code++;
    case 'DEFVAR':
    case 'POPS':
        $counter++;

        opcode($counter, $separated[0], $xw);

        $argument = explode('#', $separated[1]);

        printing_args($argument[0],1,$regex_code,$xw);
        
        # checking, if there is a start of a comment in argument
        if(!str_contains($separated[1], '#'))
        {
            if(!empty($separated[2]))
            {
                $comment = str_split($separated[2]);
                if($comment[0] != '#')
                {
                    # found extra argument
                    exit($SYNTAX_ERROR);
                }
            }
        }
        xmlwriter_end_element($xw);
        break;
    
    case 'RETURN':
    case 'BREAK':
    case 'CREATEFRAME':
    case 'PUSHFRAME':
    case 'POPFRAME';
        $counter++;

        opcode($counter, $separated[0], $xw);

        if(!empty($separated[1]))
        {
            $comment = str_split($separated[1]);
            if($comment[0] != '#')
            {
                exit($SYNTAX_ERROR);
            }    
        }
        xmlwriter_end_element($xw);          
        break;

    case 'JUMPIFEQ':
    case 'JUMPIFNEQ':
        $regex_code +=3;
    case 'TYPE':
    case 'INT2CHAR':
    case 'STRLEN':
    case 'MOVE':
    case 'NOT':
        $skip = true;
    case 'CONCAT':
    case 'STRI2INT':
    case 'ADD':
    case 'SUB':
    case 'MUL':
    case 'IDIV':
    case 'SETCHAR':
    case 'GETCHAR':
    case 'LT':
    case 'GT':
    case 'EQ':
    case 'AND':   
    case 'OR':
        $counter++;

        opcode($counter, $separated[0], $xw);

        printing_args($separated[1],1,$regex_code,$xw);

        if(empty($separated[2]))
        {
            exit($SYNTAX_ERROR);
        }

        # skips printing 3rd argument
        if($skip == true && $regex_code != 4)
        {
            $argument = explode('#', $separated[2]);

            printing_args($argument[0],2,2,$xw);

            if(!str_contains($separated[2],'#'))
            {
                if(!empty($separated[3]))
                {
                    $comment = str_split($separated[3]);
                    if($comment[0] != '#')
                    {
                        exit($SYNTAX_ERROR);
                    }
                }
            }
        }
        
        if($skip == false || $regex_code == 4)
        {
            printing_args($separated[2],2,2,$xw);

            if(empty($separated[3]))
            {
                exit($SYNTAX_ERROR);
            }
            if(!empty($separated[4]))
            {
                $comment = str_split($separated[4]);
                if($comment[0] != '#')
                {
                exit($SYNTAX_ERROR);
                }
            }
            $argument = explode('#', $separated[3]);

            printing_args($argument[0],3,2,$xw);
        }
        xmlwriter_end_element($xw);
        break;

    case 'READ':
        $counter++;

        opcode($counter, $separated[0], $xw);

        printing_args($separated[1],1,1,$xw);

        if(empty($separated[2]))
        {
                exit($SYNTAX_ERROR);
        }
        if(!empty($separated[3]))
        {
            $comment = str_split($separated[2]);
            if($comment[0] != '#')
            {
            exit($SYNTAX_ERROR);
            }
        }
        $argument = explode('#', $separated[2]);

        printing_args($argument[0],2,3,$xw);

        xmlwriter_end_element($xw); 
        break;
    
    case '.IPPCODE23':
        $head++;
        if($head > 1)
        {
            # one header was already found, this one is extra
            exit($OPCODE_ERROR);
        }
        break;

    default:
        if($comment == true)
        {
            # found a line that starts with a comment
            break;
        }
        # unknown opcode
        exit($OPCODE_ERROR);
    }
}
xmlwriter_end_element($xw);

echo(xmlwriter_output_memory($xw)); # prints output to STDOUT
?>