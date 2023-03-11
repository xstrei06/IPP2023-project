## Implementační dokumentace k 1. úloze do IPP 2022/2023  
### Jméno a příjmení: Jaroslav Streit  
### Login: xstrei06

## Implementace skriptu parse.php

Skript se skládá z jediného souboru ``parse.php``.

### Zpracování argumentů příkazové řádky

Ke zpracování programových argumentů slouží třída ``parse_args``. Při vytvoření objektu této třídy dojde ke kontrole počtu argumentů a v případě výskytu argumentu [--help] dojde k vypsání nápovědy metodou ``write_help`` a ukončení programu.

### Lexikální a syntaktická analýza

O lexikální a syntaktickou analýzu se starají třídy ``parse_input`` a ``parse_instruction``. Při vytvoření objektu třídy ``parse_input`` dochazí k načtení vstupního kódu ze standardního vstupu. Následně je vstup osekán od komentářů a prázdných řádků a přebytečných bílých znaků, je zkontrolována hlavička, celý vstup je rozdělen podle instrukcí do pole ``$lines`` a nakonec jednotlivé řádky v poli ``$lines`` jsou rozděleny na jméno a parametry jednotlivých instrukcí. Samotné instrukce kontroluje třída ``parse_instruction``, jejíž hlavní částí je přepínač podle názvu instrukce. V přepínači následně dochází ke kontrole počtu parametrů instrukce a kontrole typů a hodnot jednotlivých parametrů pomocí metod ``check_symb``, ``check_var``, ``check_label`` a ``check_type``. Kontroly parametrů v těchto metodách jsou implementovány pomocí regulárních výrazů. Cyklem přes všechny řádky v poli ``$lines`` je vytvořen objekt třídy ``parse_instruction`` pro každou intrukci vstupního programu a následně je objekt uložen do pole ``$instructions``, se kterým se pracuje dále při generování XML.

### Generování XML

Generování XML reprezentace vstupního programu má na starost třída write_xml. Třída využívá knihovnu XMLWriter. Třída přijíma jako parametr pole s instrukcemi ``$instructions``, přes které iteruje při konstruování objektu. Pro každou instrukci je vytvořen nový XML element a pomocí metody ``write_arg`` jsou vytvořeny elementy pro každý parametr instrukce. Metoda ``end_xml`` nakonec ukončí XML dokument a vytiskne vzniklé XML na standardní výstup.

### Rozšíření

Skript jsem implementoval v rámci OOP rozšíření NVP.
Ze tříd ``parse_args``, ``parse_input`` a ``write_xml`` je za celou dobu běhu programu vytvořen pouze jediný objekt, jedná se tedy o návrhový vzor **Jedináček** (Singleton). Veškerá funkcionalita těchto tříd se provede již při zavolání konstruktoru, metody jsou tedy privátní a nelze je využít mimo zkonstruování objektu. Atributy třídy parse_input ``$lines`` a ``$input`` jsou veřejné, protože je s nimi dále nutné pracovat. Načtení vstupu, jeho zpracování a vygenerování XML se provede jednorázově, proto mi Jedináček dával největší smysl. Ze třídy ``parse_instruction`` je vytvořen objekt pro každou instrukci vstupního programu a následně se podle těchto objektů generuje XML reprezentace IPPcode23 programu. Metody třídy ``parse_instruction`` jsou též privátní, protože vše potřebné proběhne při samotném zkonstruování objektu instrukce. Atributy této třídy jsou veřejné, protože je nutné s nimi pracovat při generování XML.

### Testování

K testování skriptu jsem využil [studentské testy](https://gist.github.com/sproott/d534b327752a5bb2d41139b9f9e005fa) společně s testy poskytnutými v VUT IS.
