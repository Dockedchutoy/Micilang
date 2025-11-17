# Micilang Docs

## Příkazy

### Komentáře

Jednořádkový kometář: <code>// Komentář</code>

Takové komntáře pokračují až do konce řádku

Víceřádkový komentář: <code>/// Víceřádkový
                                Komentář ///</code>

Takové kometáře pokračují, dokud se znova neobjeví lomítka. Mohou se dávat mezi přikazy, ale ehhhhh moc bych na to nesázel.

Komentáře jsou interpreterem zcela ignorovány.

### Datatypy

Je pouze pár typů dát s rozdílnými úrovněmi funkcionality:

+ <code>int</code> - Integer - Prosté celé číslo. neznačí se ničím
+ <code>str</code> - String - Text. Značí se ". Ne apostrofy. Hmmm co kdybyh použil české apostrofy to by bylo vtipne
+ <code>bool</code> - Boolean - Buďto <code>false</code> (0) nebo <code>true</code> (1).
+ <code>null</code> - Null - Prázdná hodnota. V mat. a text. operacích ignorováno.

Ještě chyby spojené obecně s datatypy:

+ <code>TypeError</code>: Invalid operation between incompatible types

### Funkce
 
Zde je výběr Micilang funkcí a statementů:

+ <code>write(*output*)</code> - Vypíše na obrazovku *output*
+ <code>var *x* = *value*</code> - Vytvoří proměnnou *x*, která má *value*
+ <code></code>

Následující funkce nejsou součástí specifikace Micilangu. Nejsou tedy nedílnou součástí jazyku, a spíš jsou věci pro testování:

+ <code>shell(*value*)</code> - Provede *value* jako program v Pythonu.