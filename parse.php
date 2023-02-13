<?php

ini_set('display_errors', 'stderr');

if ($argc > 2) {
    echo "Too many arguments\n";
    exit(10);
}

if ($argc == 2) {
    if ($argv[1] == "--help") {
        echo "Usage: php parse.php [--help]\n";
        echo "Takes input from STDIN\n";
        exit(0);
    }
}

function fce($x) {
    $x = explode('#', $x)[0];
    return $x;
}

function check_symb($symb) {
    if (preg_match('/^(LF|GF|TF)@[a-zA-Z_$&%!?-][a-zA-Z_$&%!?0-9-]*$/', $symb)){
        return 0;
    }elseif (preg_match('/^int@[+-]?[0-9]+$/', $symb)) {
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

function check_var($var) {
    if (preg_match('/^(LF|GF|TF)@[a-zA-Z_$&%!?-][a-zA-Z_$&%!?0-9-]*$/', $var) == 0) {
        return 1;
    }
    return 0;
}

function check_label($label) {
    if (preg_match('/^[a-zA-Z_$&%!?-][a-zA-Z_$&%!?0-9-]*$/', $label)) {
        return 0;
    }
    return 1;
}

function check_type($type) {
    if (preg_match('/^(int|string|bool)$/', $type) == 0) {
        return 1;
    }
    return 0;
}

$input = file_get_contents('php://stdin', 'r');
$lines = explode("\n", $input);
$lines = array_map('fce', $lines);
$lines = preg_replace('/\s+/', ' ', $lines);
$lines = array_map('trim', $lines);
$lines = array_values(array_filter($lines));

$index = 0;

foreach ($lines as $line){
    $line = explode(' ', $line);
    $line[0] = strtoupper($line[0]);
    $lines[$index] = $line;
    $index++;
}
if (strcmp($lines[0][0], ".IPPCODE23")) {
    exit(21);
}

$header = 0;

foreach($lines as $line) {
    if ($header == 0) {
        $header++;
        continue;
    }
    switch ($line[0]) {
        case "MOVE":
            if (count($line) != 3) {
                exit(23);
            }
            if (check_var($line[1])) {
                exit(23);
            }
            if (check_symb($line[2])) {
                exit(23);
            }
            break;
        case "CREATEFRAME":
            if (count($line) != 1) {
                exit(23);
            }
            break;
        case "PUSHFRAME":
            if (count($line) != 1) {
                exit(23);
            }
            break;
        case "POPFRAME":
            if (count($line) != 1) {
                exit(23);
            }
            break;
        case "DEFVAR":
            if (count($line) != 2) {
                exit(23);
            }
            if (check_var($line[1])){
                echo "kurva";
                exit(23);
            };
            break;
        case "CALL":
            if (count($line) != 2) {
                exit(23);
            }
            if (check_label($line[1])){
                exit(23);
            };
            break;
        case "RETURN":
            if (count($line) != 1) {
                exit(23);
            }
            break;
        case "PUSHS":
            if (count($line) != 2) {
                exit(23);
            }
            if (check_symb($line[1])) {
                exit(23);
            }
            break;
        case "POPS":
            if (count($line) != 2) {
                exit(23);
            }
            if (check_var($line[1])){
                exit(23);
            };
            break;
        case "ADD":
            if (count($line) != 4) {
                exit(23);
            }
            if (check_var($line[1])){
                exit(23);
            }
            if (check_symb($line[2])) {
                exit(23);
            }
            if (check_symb($line[3])) {
                exit(23);
            }
            break;
        case "SUB":
            if (count($line) != 4) {
                exit(23);
            }
            if (check_var($line[1])){
                exit(23);
            }
            if (check_symb($line[2])) {
                exit(23);
            }
            if (check_symb($line[3])) {
                exit(23);
            }
            break;
        case "MUL":
            if (count($line) != 4) {
                exit(23);
            }
            if (check_var($line[1])){
                exit(23);
            }
            if (check_symb($line[2])) {
                exit(23);
            }
            if (check_symb($line[3])) {
                exit(23);
            }
            break;
        case "IDIV":
            if (count($line) != 4) {
                exit(23);
            }
            if (check_var($line[1])){
                exit(23);
            }
            if (check_symb($line[2])) {
                exit(23);
            }
            if (check_symb($line[3])) {
                exit(23);
            }
            break;
        case "LT":
            if (count($line) != 4) {
                exit(23);
            }
            if (check_var($line[1])){
                exit(23);
            }
            if (check_symb($line[2])) {
                exit(23);
            }
            if (check_symb($line[3])) {
                exit(23);
            }
            break;
        case "GT":
            if (count($line) != 4) {
                exit(23);
            }
            if (check_var($line[1])){
                exit(23);
            }
            if (check_symb($line[2])) {
                exit(23);
            }
            if (check_symb($line[3])) {
                exit(23);
            }
            break;
        case "EQ":
            if (count($line) != 4) {
                exit(23);
            }
            if (check_var($line[1])){
                exit(23);
            }
            if (check_symb($line[2])) {
                exit(23);
            }
            if (check_symb($line[3])) {
                exit(23);
            }
            break;
        case "AND":
            if (count($line) != 4) {
                exit(23);
            }
            if (check_var($line[1])){
                exit(23);
            }
            if (check_symb($line[2])) {
                exit(23);
            }
            if (check_symb($line[3])) {
                exit(23);
            }
            break;
        case "OR":
            if (count($line) != 4) {
                exit(23);
            }
            if (check_var($line[1])){
                exit(23);
            }
            if (check_symb($line[2])) {
                exit(23);
            }
            if (check_symb($line[3])) {
                exit(23);
            }
            break;
        case "NOT":
            if (count($line) != 3) {
                exit(23);
            }
            if (check_var($line[1])){
                exit(23);
            }
            if (check_symb($line[2])) {
                exit(23);
            }
            break;
        case "INT2CHAR":
            if (count($line) != 3) {
                exit(23);
            }
            if (check_var($line[1])){
                exit(23);
            }
            if (check_symb($line[2])) {
                exit(23);
            }
            break;
        case "STRI2INT":
            if (count($line) != 4) {
                exit(23);
            }
            if (check_var($line[1])){
                exit(23);
            }
            if (check_symb($line[2])) {
                exit(23);
            }
            if (check_symb($line[3])) {
                exit(23);
            }
            break;
        case "READ":
            if (count($line) != 3) {
                exit(23);
            }
            if (check_var($line[1])){
                exit(23);
            }
            if (check_type($line[2])) {
                exit(23);
            }
            break;
        case "WRITE":
            if (count($line) != 2) {
                exit(23);
            }
            if (check_symb($line[1])) {
                exit(23);
            }
            break;
        case "CONCAT":
            if (count($line) != 4) {
                exit(23);
            }
            if (check_var($line[1])){
                exit(23);
            }
            if (check_symb($line[2])) {
                exit(23);
            }
            if (check_symb($line[3])) {
                exit(23);
            }
            break;
        case "STRLEN":
            if (count($line) != 3) {
                exit(23);
            }
            if (check_var($line[1])){
                exit(23);
            }
            if (check_symb($line[2])) {
                exit(23);
            }
            break;
        case "GETCHAR":
            if (count($line) != 4) {
                exit(23);
            }
            if (check_var($line[1])){
                exit(23);
            }
            if (check_symb($line[2])) {
                exit(23);
            }
            if (check_symb($line[3])) {
                exit(23);
            }
            break;
        case "SETCHAR":
            if (count($line) != 4) {
                exit(23);
            }
            if (check_var($line[1])){
                exit(23);
            }
            if (check_symb($line[2])) {
                exit(23);
            }
            if (check_symb($line[3])) {
                exit(23);
            }
            break;
        case "TYPE":
            if (count($line) != 3) {
                exit(23);
            }
            if (check_var($line[1])){
                exit(23);
            }
            if (check_symb($line[2])) {
                exit(23);
            }
            break;
        case "LABEL":
            if (count($line) != 2) {
                exit(23);
            }
            if (check_label($line[1])) {
                exit(23);
            }
            break;
        case "JUMP":
            if (count($line) != 2) {
                exit(23);
            }
            if (check_label($line[1])) {
                exit(23);
            }
            break;
        case "JUMPIFEQ":
            if (count($line) != 4) {
                exit(23);
            }
            if (check_label($line[1])) {
                exit(23);
            }
            if (check_symb($line[2])) {
                exit(23);
            }
            if (check_symb($line[3])) {
                exit(23);
            }
            break;
        case "JUMPIFNEQ":
            if (count($line) != 4) {
                exit(23);
            }
            if (check_label($line[1])) {
                exit(23);
            }
            if (check_symb($line[2])) {
                exit(23);
            }
            if (check_symb($line[3])) {
                exit(23);
            }
            break;
        case "EXIT":
            if (count($line) != 2) {
                exit(23);
            }
            if (check_symb($line[1])) {
                exit(23);
            }
            break;
        case "DPRINT":
            if (count($line) != 2) {
                exit(23);
            }
            break;
        case "BREAK":
            if (count($line) != 1) {
                exit(23);
            }
            break;
        default:
            exit(22);
    }
}

$xml = new XMLWriter();
$xml->openMemory();
$xml->startDocument('1.0', 'UTF-8');
$xml->setIndent(true);

$xml->startElement('program');
$xml->writeAttribute('language', 'IPPcode23');

function write_instruction($line, $xml, $id) {
    $xml->startElement('instruction');
    $xml->writeAttribute('order', $id);
    $xml->writeAttribute('opcode', $line[0]);
    for($i = 1; $i < count($line); $i++) {
        $xml->startElement('arg' . $i);
        if(str_starts_with($line[$i], 'GF@') || str_starts_with($line[$i], 'LF@') || str_starts_with($line[$i], 'TF@')) {
            $xml->writeAttribute('type', 'var');
        }
        else if(str_starts_with($line[$i], 'int@')) {
            $line[$i] = explode('@', $line[$i])[1];
            $xml->writeAttribute('type', 'int');
        }
        else if(str_starts_with($line[$i], 'bool@')) {
            $line[$i] = explode('@', $line[$i])[1];
            $xml->writeAttribute('type', 'bool');
        }
        else if(str_starts_with($line[$i], 'string@')) {
            $line[$i] = explode('@', $line[$i])[1];
            $xml->writeAttribute('type', 'string');
        }
        else if(str_starts_with($line[$i], 'nil@')) {
            $line[$i] = explode('@', $line[$i])[1];
            $xml->writeAttribute('type', 'nil');
        }
        else if(str_starts_with($line[$i], 'type@')) {
            $xml->writeAttribute('type', 'type');
        }
        else {
            $xml->writeAttribute('type', 'label');
        }
        $xml->text($line[$i]);
        $xml->endElement();
    }
    $xml->endElement();
}

$id = 1;
foreach($lines as $line) {
    if($line[0] == ".IPPCODE23") {
        continue;
    }
    write_instruction($line, $xml, $id);
    $id++;
}

$xml->endElement();
$xml->endDocument();
echo $xml->flush();

?>