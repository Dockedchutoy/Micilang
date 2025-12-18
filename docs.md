# Micilang Docs

UPOZORNĚNÍ: Dokumentace nemusí být zcela úplná a může mít zastaralé info.

## Příkazy

### Komentáře

Komentáře jsou víceřádkové a značí se takto: <code>// Komentář zde //</code>

Komentáře jsou v lexeru ignorovány, spolu s mezerami a novými řádky.

### Datatypy

Je pouze pár typů dat s rozdílnými úrovněmi funkcionality:

+ <code>num</code> - Number - Číslo, může, ale nemusí být desetinné. Čísla se při jakýchkoliv operacích převádí na desetinné.
+ <code>str</code> - String - Řetězec. Značí se stylem <code>"řetězec zde"</code>. Přemýšlím o podpoře českých uvozovek.
+ <code>bool</code> - Boolean - Buďto <code>false</code> nebo <code>true</code>.
+ <code>null</code> - Null - Prázdná hodnota.

### Statementy
 
Micilang má několik použitelných statementů:

+ <code>printl *value*;</code> - Na nový řádek vypíše na obrazovku *value*.
+ <code>var *name* = *value*;</code> - Vytvoří proměnnou *name*, která má *value*
+ <code>if *condition* {*thenBranch*}</code> - Provede kód obsažený v *thenBranch*, pokud *condition* vrátí true.
+ <code>else {*elseBranch*}</code> - Součást if statementu, pokud je *condition* false, provede *elseBranch*.
+ <code>while *condition* {*whileBlock*}</code> - opakovaně provádí *whileBlock*, dokud *condition* vrací true.
+ <code>func *name* *arguments\** {funcBlock}</code> - Vytvoří funkci zvanou *name* a argumenty *arguments*, který provádí po vyvolání kód v *funcBlock*.
+ <code>return *value*;</code> - Ukončí průběh dané funkce a vrátí hodnotu *value*.

### Funkce

Micilang má ještě základní knihovnu vestavěných funkcí. Zde je celý jejich seznam:

+ <code>inputl(*value*);</code> - Vrátí vstup od uživatele, který je přijímán na novém řádku. *value* se ukáže před vstupem, může být prázdný.
