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

$input = file_get_contents('php://stdin', 'r');
$lines = explode("\n", $input);
$lines = array_map('fce', $lines);
$lines = array_map('trim', $lines);
$lines = array_values(array_filter($lines));

$lines[0] = strtoupper($lines[0]);
if (strcmp($lines[0], ".IPPCODE23")) {
    exit(21);
}

var_dump($lines);


?>