# Quoting matrix: pwsh7 → pwsh7 / pwsh5 / cmd / python / bash / dotnet

Scope: variable-value transmission across runtime boundary. Payload live in
PowerShell variable (single-quote literal), passed as arg to helper, helper
echo back `[arg]`. Cell `ok` mean byte-identical return. This isolate
transmission layer, not keystroke parsing.

Runtimes: `pwsh` 7.6.5 (child), `powershell` 5.1, `cmd`, `python`,
`C:/Program Files/Git/bin/bash.exe`, `dotnet` 11 (`echoarg.dll`, build once
from C# source below).

## Helpers (exact sources)

`echo-arg.ps1`: `param([string]$a)` then `'[' + $a + ']'`.
`echo-arg.bat`: `@echo off` newline `echo [%1]` (raw `%1`, no tilde-strip).
`echo-arg.py`: `import sys` newline `print('[' + sys.argv[1] + ']')`.
`echo-arg.sh`: `printf '[%s]' "$1"`.
C# (`echoarg.csproj` net11.0 + `Program.cs`):
`System.Console.Write("[" + args[0] + "]");` via `GetCommandLineArgs`-style
`args[0]` (first user arg; dll run as `dotnet echoarg.dll <payload>`).

Probe: for each payload × runtime, run helper with payload variable,
grab stdout, compare case-sensitive against `[payload]`.

## Results

| payload                 | ps7 | ps5 | cmd                                                                                               | py  | bash         | dotnet |
| ----------------------- | --- | --- | ------------------------------------------------------------------------------------------------- | --- | ------------ | ------ |
| `plain`                 | ok  | ok  | ok                                                                                                | ok  | ok           | ok     |
| `it's`                  | ok  | ok  | ok                                                                                                | ok  | DIFF `[its]` | ok     |
| `say "hi"`              | ok  | ok  | DIFF `["say "hi""]`                                                                               | ok  | ok           | ok     |
| `C:\Users\x`            | ok  | ok  | ok                                                                                                | ok  | ok           | ok     |
| `C:\\Users\\x`          | ok  | ok  | ok                                                                                                | ok  | ok           | ok     |
| `C:/Users/x`            | ok  | ok  | ok                                                                                                | ok  | ok           | ok     |
| `"C:\path with spaces"` | ok  | ok  | ok                                                                                                | ok  | ok           | ok     |
| `a?b=c`                 | ok  | ok  | DIFF `[a?b]`                                                                                      | ok  | ok           | ok     |
| `$HOME`                 | ok  | ok  | ok                                                                                                | ok  | ok           | ok     |
| `a,b;c\|d&e`            | ok  | ok  | DIFF `'C:' is not recognized as an internal or external command, operable program or batch file.` | ok  | ok           | ok     |
| `100%`                  | ok  | ok  | ok                                                                                                | ok  | ok           | ok     |
| `trailing\`             | ok  | ok  | ok                                                                                                | ok  | ok           | ok     |

## Findings

- ps5 block script by default (`UnauthorizedAccess`); probe add `-ExecutionPolicy Bypass` fix um.
- bash eat single quote (`it's` → `[its]`); all other payload survive bash fine.
- cmd keep inner double quote, add outer ones too (`["say "hi""]`).
- cmd treat `=` as arg splitter (`a?b=c` → `[a?b]`).
- cmd metachar `;||&` split/pipe even with caller quote (`/c` strip quote); payload run as command, bad.
- Backslash transmit clean everywhere, even doubled and trailing kind.
- `$HOME`, `100%`, `a?b=c` (outside cmd) transmit literal everywhere, no trouble.