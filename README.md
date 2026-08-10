# DarkSAST

**DarkSAST** is a lightweight, dependency-free **Python Static Application Security Testing (SAST)** scanner that uses Python's **Abstract Syntax Tree (AST)** to identify potentially dangerous coding patterns in `.py` files.

Unlike simple regex-based scanners, DarkSAST understands Python code structure and can distinguish actual function calls and assignments from comments and strings.

> ⚠️ DarkSAST is a lightweight security auditing utility and is not intended to replace professional SAST platforms or manual security testing.

---

## Features

DarkSAST currently detects:

* `eval()` usage
* `exec()` usage
* `os.system()` usage
* `pickle.loads()` deserialization
* `subprocess` functions using `shell=True`
* Hardcoded passwords
* Hardcoded API keys
* Hardcoded secrets
* Hardcoded tokens
* Python syntax errors

### Current detections

| Detection                     | Severity |
| ----------------------------- | -------- |
| `eval()`                      | High     |
| `exec()`                      | High     |
| `os.system()`                 | High     |
| `pickle.loads()`              | High     |
| `subprocess(..., shell=True)` | High     |
| Hardcoded password            | Medium   |
| Hardcoded API key             | Medium   |
| Hardcoded secret              | Medium   |
| Hardcoded token               | Medium   |

---

## Why AST Instead of Regex?

Many simple security scanners rely on regular expressions:

```python
if re.search(r"eval\s*\(", line):
    print("eval() detected")
```

While this is easy to implement, regex does not understand Python syntax.

For example:

```python
# eval(user_input)
```

or:

```python
print("eval(user_input)")
```

A regex scanner may incorrectly report these as vulnerabilities.

DarkSAST instead parses Python source code using Python's built-in `ast` module:

```python
tree = ast.parse(source)
```

It then walks the resulting syntax tree and analyzes actual Python constructs.

This allows DarkSAST to identify actual function calls such as:

```python
eval(user_input)
```

while ignoring:

```python
# eval(user_input)
```

and:

```python
print("eval(user_input)")
```

---

## Requirements

DarkSAST has no external dependencies.

You only need:

* Python 3.8+
* Standard Python library

Check your Python version:

```bash
python3 --version
```

---

## Installation

Clone the repository:

```bash
git clone https://github.com/YOUR_USERNAME/DarkSAST.git
```

Enter the directory:

```bash
cd DarkSAST
```

No `pip install` is required.

---

## Usage

Run DarkSAST:

```bash
python3 darksast.py
```

You will be prompted for the directory you want to scan:

```text
Target directory (default: current directory):
```

Enter the path:

```text
./test_repo
```

DarkSAST will recursively search for Python files and analyze them.

---

## Example

Running:

```bash
python3 darksast.py
```

Example output:

```text
    ____             __   _____ ___   __________
   / __ \____ ______/ /__/ ___//   | / ___/_  __/
  / / / / __ `/ ___/ // /\__ \/ /| | \__ \ / /
 / /_/ / /_/ / /  / ,<  ___/ / ___ |___/ // /
/_____/\__,_/_/  /_/|_|/____/_/  |_/____//_/

                DarkSAST-AST v1.0
      Lightweight Python AST Scanner

Target directory (default: current directory): ./test_repo

================================================================================
./test_repo/vuln_eval.py
================================================================================
[HIGH] Line 3: eval() usage

================================================================================
./test_repo/vuln_os_system.py
================================================================================
[HIGH] Line 5: os.system() usage

================================================================================
./test_repo/vuln_password.py
================================================================================
[MEDIUM] Line 1: Hardcoded credential in variable 'password'

================================================================================
SCAN SUMMARY
================================================================================
Files Scanned : 10
Findings      : 5
```

---

# Test Files

The repository includes intentionally vulnerable Python files under:

```text
test_repo/
```

These files are provided exclusively for testing DarkSAST's detection capabilities.

Example:

```python
import os

cmd = input("Command: ")
os.system(cmd)
```

DarkSAST should identify:

```text
[HIGH] Line 4: os.system() usage
```

---

## Included Vulnerable Examples

The test repository contains examples for:

```text
vuln_eval.py
vuln_exec.py
vuln_os_system.py
vuln_pickle.py
vuln_subprocess.py
vuln_password.py
vuln_api_key.py
vuln_token.py
mixed_vulns.py
```

There are also safe examples:

```text
safe_file.py
tricky_comments.py
```

These demonstrate that AST-based analysis can avoid some false positives caused by comments and strings.

---

# Detection Examples

## 1. eval()

Example:

```python
user_input = input("Expression: ")
result = eval(user_input)
```

Detection:

```text
[HIGH] eval() usage
```

---

## 2. exec()

Example:

```python
code = input("Python code: ")
exec(code)
```

Detection:

```text
[HIGH] exec() usage
```

---

## 3. os.system()

Example:

```python
import os

command = input("Command: ")
os.system(command)
```

Detection:

```text
[HIGH] os.system() usage
```

---

## 4. pickle.loads()

Example:

```python
import pickle

data = open("payload.bin", "rb").read()
obj = pickle.loads(data)
```

Detection:

```text
[HIGH] pickle.loads() deserialization
```

---

## 5. subprocess with shell=True

Example:

```python
import subprocess

command = input("Command: ")

subprocess.run(
    command,
    shell=True
)
```

Detection:

```text
[HIGH] subprocess.run() with shell=True
```

---

## 6. Hardcoded Credentials

Example:

```python
password = "Admin123!"
```

Detection:

```text
[MEDIUM] Hardcoded credential in variable 'password'
```

DarkSAST also checks common credential-related variable names such as:

```text
password
passwd
pwd
secret
apikey
api_key
token
```

---

# What DarkSAST Does Not Do

DarkSAST is intentionally simple.

It currently does **not** perform:

* Full data-flow analysis
* Taint analysis
* Control-flow analysis
* Interprocedural analysis
* Authentication analysis
* Business-logic analysis
* Dependency vulnerability scanning
* Package vulnerability detection
* Runtime analysis
* Dynamic application security testing (DAST)

For example, DarkSAST can identify:

```python
eval(user_input)
```

but it does not currently determine whether `user_input` originated from an HTTP request several functions earlier.

That type of analysis would require data-flow and/or taint analysis.

---

# AST vs Regex

A simplified comparison:

| Capability                   |        Regex |          AST |
| ---------------------------- | -----------: | -----------: |
| Understand Python syntax     |            ❌ |            ✅ |
| Detect actual function calls |           ⚠️ |            ✅ |
| Ignore comments              |            ❌ |            ✅ |
| Ignore strings               |            ❌ |            ✅ |
| Identify variables           |            ❌ |            ✅ |
| Identify assignments         |           ⚠️ |            ✅ |
| Track data flow              |            ❌ |            ❌ |
| Easy to implement            |            ✅ |            ✅ |
| External dependencies        | Not required | Not required |

AST is therefore a better foundation for Python source-code analysis than simple text matching.

---

# Project Structure

```text
DarkSAST/
│
├── darksast.py
│
├── test_repo/
│   ├── vuln_eval.py
│   ├── vuln_exec.py
│   ├── vuln_os_system.py
│   ├── vuln_pickle.py
│   ├── vuln_subprocess.py
│   ├── vuln_password.py
│   ├── vuln_api_key.py
│   ├── vuln_token.py
│   ├── mixed_vulns.py
│   ├── safe_file.py
│   └── tricky_comments.py
│
├── README.md
├── LICENSE
└── .gitignore
```

---

# Security Disclaimer

DarkSAST is intended for:

* Security research
* Secure coding education
* Authorized source-code auditing
* Local development
* SAST experimentation
* Security testing of applications you own or have permission to assess

Do not use this tool to analyze source code without appropriate authorization.

The findings produced by DarkSAST are **potential security issues** and should be manually reviewed before being considered confirmed vulnerabilities.

---

# Contributing

Contributions are welcome.

Some areas that could improve DarkSAST include:

* Additional AST security rules
* Better severity classification
* CWE mappings
* OWASP mappings
* Improved credential detection
* More Python vulnerability patterns
* Unit tests
* JSON output
* HTML reports
* Command-line arguments
* Configuration files

To contribute:

1. Fork the repository.
2. Create a feature branch.
3. Add your detection rule or improvement.
4. Add appropriate test cases.
5. Submit a pull request.

---

# Roadmap

Possible future improvements:

```text
[x] Regex-based prototype
[x] AST-based Python scanner
[x] Recursive directory scanning
[x] Severity classification
[x] Vulnerable test repository

[ ] CWE mapping
[ ] OWASP mapping
[ ] JSON output
[ ] HTML report
[ ] CLI arguments
[ ] Configurable rules
[ ] More AST security rules
[ ] Unit test suite
[ ] Data-flow analysis
[ ] Taint analysis
```

---

# License

This project is released under the MIT License.

See `LICENSE` for details.

---

## Author

Developed by **Syed Jan Muhammad Zaidi**.

DarkSAST is a lightweight security research project focused on experimenting with Python AST-based source-code security analysis.

---

## ⭐ Support

If you find DarkSAST useful, consider giving the repository a ⭐ on GitHub.
