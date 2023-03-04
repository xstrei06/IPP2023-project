<?php

ini_set('display_errors', 'stderr');

class parse_args {

    function __construct($argc, $argv) {
        if ($argc > 2) {
            fwrite(STDERR, "Too many arguments\n");
            exit(10);
        }
        if ($argc == 2) {
            if ($argv[1] == "--help") {
                $this->write_help();
            }
            else {
                exit(10);
            }
        }
    }

    public function write_help() {
        echo "Usage: parse.php [--help]\n";
        echo "Program takes input from STDIN and outputs XML to stdout.\n";
        exit(0);
    }
}

class parse_file {

    public $input;
    public $lines;

    function __construct() {
        $this->input = file_get_contents('php://stdin', 'r');
        $this->lines = explode("\n", $this->input);
        $this->lines = array_map(array($this, 'remove_comments'), $this->lines);
        $this->lines = preg_replace('/\s+/', ' ', $this->lines);
        $this->lines = array_map('trim', $this->lines);
        $this->lines = array_values(array_filter($this->lines));
        $this->check_header();
    }

    public function check_header() {
        $index = 0;
        foreach ($this->lines as $line){
            $line = explode(' ', $line);
            $line[0] = strtoupper($line[0]);
            $this->lines[$index] = $line;
            $index++;
        }
        if (strcmp($this->lines[0][0], ".IPPCODE23")) {
            exit(21);
        }
    } 

    public function remove_comments($x) {
        $x = explode('#', $x)[0];
        return $x;
    }
}

class parse_instruction {

    public $name;
    public $arg1 = NULL;
    public $arg2 = NULL;
    public $arg3 = NULL;

    function __construct($line) {
        $this->check_params($line);
    }

    public function check_params($line) {
        $this->name = $line[0];
        switch ($line[0]) {
            case "INT2CHAR":
            case "STRLEN":
            case "MOVE":
            case "TYPE":
            case "NOT":
                if (count($line) != 3) {
                    exit(23);
                }
                if ($this->check_var($line[1])){
                    exit(23);
                }else{
                    $this->arg1 = $line[1];
                }
                if ($this->check_symb($line[2])) {
                    exit(23);
                }else{
                    $this->arg2 = $line[2];
                }
                break;
            case "CREATEFRAME":
            case "PUSHFRAME":
            case "POPFRAME":
            case "RETURN":
            case "BREAK":
                if (count($line) != 1) {
                    exit(23);
                }
                break;
            case "DEFVAR":
            case "POPS":
                if (count($line) != 2) {
                    exit(23);
                }
                if ($this->check_var($line[1])){
                    exit(23);
                }else{
                    $this->arg1 = $line[1];
                }
                break;
            case "LABEL":
            case "CALL":
            case "JUMP":
                if (count($line) != 2) {
                    exit(23);
                }
                if ($this->check_label($line[1])) {
                    exit(23);
                }else{
                    $this->arg1 = $line[1];
                }
                break;
            case "DPRINT":
            case "PUSHS":
            case "WRITE":
            case "EXIT":
                if (count($line) != 2) {
                    exit(23);
                }
                if ($this->check_symb($line[1])) {
                    exit(23);
                }else{
                    $this->arg1 = $line[1];
                }
                break;
            case "STRI2INT":
            case "GETCHAR":
            case "SETCHAR":
            case "CONCAT":
            case "IDIV":
            case "ADD":
            case "SUB":
            case "MUL":
            case "AND":
            case "LT":
            case "GT":
            case "EQ":
            case "OR":
                if (count($line) != 4) {
                    exit(23);
                }
                if ($this->check_var($line[1])){
                    exit(23);
                }else{
                    $this->arg1 = $line[1];
                }
                if ($this->check_symb($line[2])) {
                    exit(23);
                }else{
                    $this->arg2 = $line[2];
                }
                if ($this->check_symb($line[3])) {
                    exit(23);
                }else{
                    $this->arg3 = $line[3];
                }
                break;
            case "READ":
                if (count($line) != 3) {
                    exit(23);
                }
                if ($this->check_var($line[1])){
                    exit(23);
                }else{
                    $this->arg1 = $line[1];
                }
                if ($this->check_type($line[2])) {
                    exit(23);
                }else{
                    $this->arg2 = $line[2];
                }
                break;
            case "JUMPIFEQ":
            case "JUMPIFNEQ":
                if (count($line) != 4) {
                    exit(23);
                }
                if ($this->check_label($line[1])) {
                    exit(23);
                }else{
                    $this->arg1 = $line[1];
                }
                if ($this->check_symb($line[2])) {
                    exit(23);
                }else{
                    $this->arg2 = $line[2];
                }
                if ($this->check_symb($line[3])) {
                    exit(23);
                }else{
                    $this->arg3 = $line[3];
                }
                break;
            default:
                exit(22);
        }
    }

    public function check_symb($symb) {
        if (preg_match('/^(LF|GF|TF)@[a-zA-Z_$&%!?-][a-zA-Z_$&%!?0-9-]*$/', $symb)){
            return 0;
        }elseif (preg_match('/^int@[+-]?0$/', $symb)) { #zero
            return 0;
        }elseif (preg_match('/^int@[+-]?[1-9][0-9]*(_[0-9]+)*$/', $symb)) { #decimal number
            return 0;
        }elseif (preg_match('/^int@[+-]?0[xX][0-9a-fA-F]+(_[0-9a-fA-F]+)*$/', $symb)) { #hexadecimal number
            return 0;
        }elseif (preg_match('/^int@[+-]?0[oO]?[0-7]+(_[0-7]+)*$/', $symb)) { #octal number
            return 0;
        }elseif(preg_match('/^nil@nil$/', $symb)){
            return 0;
        }elseif(preg_match('/^bool@(true|false)$/', $symb)){
            return 0;
        }elseif(preg_match('/^string@([^#\\\]|(\\\\[0-9]{3}))*$/', $symb)){
            return 0;
        }else{
            return 1;
        }
    }

    public function check_var($var) {
        if (preg_match('/^(LF|GF|TF)@[a-zA-Z_$&%*!?-][a-zA-Z_$&%*!?0-9-]*$/', $var)) {
            return 0;
        }
        return 1;
    }

    public function check_label($label) {
        if (preg_match('/^[a-zA-Z_$&%*!?-][a-zA-Z_$&%*!?0-9-]*$/', $label)) {
            return 0;
        }
        return 1;
    }

    public function check_type($type) {
        if (preg_match('/^(int|string|bool)$/', $type) == 0) {
            return 1;
        }
        return 0;
    }
}

$args = new parse_args($argc, $argv);

$file = new parse_file();

$header = 0;
$instructions = array();

foreach($file->lines as $line) {
    if ($header == 0) {
        $header++;
        continue;
    }
    $instructions[] = new parse_instruction($line);
}

$xml_out = new write_xml($instructions);

class write_xml {
    public $xml;
    public $types = ["int", "string", "bool", "nil"];

    function __construct($instructions) {
        $this->xml = new XMLWriter();
        $this->xml->openMemory();
        $this->xml->startDocument('1.0', 'UTF-8');
        $this->xml->setIndent(true);
        $this->xml->setIndentString("    ");
        $this->xml->startElement('program');
        $this->xml->writeAttribute('language', 'IPPcode23');
        $this->write_instructions($instructions);
        $this->end_xml();
    }
        
    public function write_instructions($instructions) {
        $id = 1;
        foreach($instructions as $instruction) {
            $this->xml->startElement('instruction');
            $this->xml->writeAttribute('order', $id);
            $this->xml->writeAttribute('opcode', $instruction->name);
            if($instruction->arg1 != NULL){
                $this->write_arg($instruction->arg1, 1);
            }
            if($instruction->arg2 != NULL){
                $this->write_arg($instruction->arg2, 2);
            }
            if($instruction->arg3 != NULL){
                $this->write_arg($instruction->arg3, 3);
            }
            $this->xml->endElement();
            $id++;
        }
    }

    public function write_arg($arg, $id) {
        $this->xml->startElement('arg' . $id);
        if(str_starts_with($arg, 'GF@') || str_starts_with($arg, 'LF@') || str_starts_with($arg, 'TF@')) {
            $this->xml->writeAttribute('type', 'var');
        }
        else if(str_starts_with($arg, 'int@')) {
            $arg = explode('@', $arg, 2)[1];
            $this->xml->writeAttribute('type', 'int');
        }
        else if(str_starts_with($arg, 'bool@')) {
            $arg = explode('@', $arg, 2)[1];
            $this->xml->writeAttribute('type', 'bool');
        }
        else if(str_starts_with($arg, 'string@')) {
            $arg = explode('@', $arg, 2)[1];
            $this->xml->writeAttribute('type', 'string');
        }
        else if(str_starts_with($arg, 'nil@')) {
            $arg = explode('@', $arg, 2)[1];
            $this->xml->writeAttribute('type', 'nil');
        }
        else if(in_array($arg, $this->types)) {
            $this->xml->writeAttribute('type', 'type');
        }
        else {
            $this->xml->writeAttribute('type', 'label');
        }
        $this->xml->text($arg);
        $this->xml->endElement();
    }

    public function end_xml() {
        $this->xml->endElement();
        $this->xml->endDocument();
        echo $this->xml->flush();
    }
}
?>