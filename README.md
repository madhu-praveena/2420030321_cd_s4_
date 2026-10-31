# Interpreter vs Compiler Comparison Tool

An educational Compiler Design workbench that runs the same small C-like program through two independent execution paths and compares their outputs and measured processing costs.

- **Interpreter path:** source code → lexer → parser / AST → direct AST evaluation.
- **Compiler + VM path:** source code → lexer → parser / AST → bytecode translation → stack-based virtual machine.

The application is built with Python and Flask and provides a browser dashboard, built-in examples, batch comparison, and CSV export.

## Features

- Mini-language support for variables, integer arithmetic, relational and Boolean operators, `if` / `else`, `while`, blocks, and `print()`.
- A lexer and recursive-descent / precedence-climbing parser that produce a shared AST representation.
- Direct AST interpreter and a separate bytecode compiler + virtual machine.
- Phase measurements for lexical analysis, parsing, translation, and execution.
- Output and final-variable comparison to check correctness.
- VM bytecode listing, generated instruction count, and executed VM steps.
- Five built-in sample programs, batch execution page, and downloadable CSV report.
- No Python `eval()` or `exec()` is used to run user programs.

## Tech stack

| Layer | Technology |
|---|---|
| Backend | Python 3.9+ and Flask |
| Language processing | Custom lexer, parser, AST, interpreter, bytecode compiler, and VM |
| Frontend | HTML, CSS, Jinja templates |
| Benchmarking | Python `time.perf_counter()` |
| Export | Python `csv` module |

## Quick start

### 1. Clone the repository

```bash
git clone https://github.com/<your-username>/interpreter-vs-compiler-comparison-tool.git
cd interpreter-vs-compiler-comparison-tool
```

### 2. Create and activate a virtual environment

**macOS / Linux**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Windows PowerShell**

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Start the application

```bash
python app.py
```

Open <http://127.0.0.1:5000> in your browser. The batch comparison page is available at <http://127.0.0.1:5000/batch>.

> This is a local educational application. The Flask development server is configured for local use; do not expose it publicly with debug mode enabled. For deployment, configure a strong `SECRET_KEY`, turn debug mode off, and use a production WSGI server.

## Example program

```c
// Calculate a value and print it
x = 10;
y = 20;
result = x + y * 2;
print(result);
```

Expected output:

```text
50
```

Try the sample programs in [`samples/`](samples/), or select the built-in examples in the application.

## Supported mini-language

| Feature | Example |
|---|---|
| Assignment | `x = 5;` |
| Arithmetic | `total = x + y * 2;` |
| Relational operators | `x < 10`, `x == y`, `x >= y` |
| Boolean operators | `a && b`, `a || b`, `!a` |
| Conditional | `if (x > 5) { print(x); } else { print(0); }` |
| Loop | `while (x < 10) { x = x + 1; }` |
| Output | `print(total);` |
| Blocks | `{ x = 1; print(x); }` |

The language uses integer values. Division truncates toward zero. See [`docs/LANGUAGE.md`](docs/LANGUAGE.md) for grammar and semantics.

## Repository structure

```text
interpreter-vs-compiler-comparison-tool/
├── app.py                 # Flask application and routes
├── language.py            # Lexer, parser, AST, interpreter, compiler, and VM
├── benchmark.py           # Phase timing and comparison report
├── requirements.txt       # Python dependencies
├── templates/
│   ├── index.html         # Main interactive workbench
│   └── batch.html         # Batch comparison page
├── static/
│   └── style.css          # Frontend styles
├── samples/               # Ready-to-run mini-language programs
├── tests/                 # Automated tests
├── docs/                  # Architecture, language, and benchmark notes
├── presentation/          # Project presentation used for the demo
├── .gitignore
├── CONTRIBUTING.md
├── LICENSE
└── README.md
```

## How the system works

1. The user enters a program in the browser-based source editor.
2. The lexer converts characters into tokens such as identifiers, numbers, operators, and keywords.
3. The parser checks syntax and creates an Abstract Syntax Tree (AST).
4. The interpreter path evaluates the AST directly.
5. The compiler path translates the AST into stack-based bytecode, then the VM executes those instructions.
6. The benchmark module records phase timings and compares output and final variable values.
7. The dashboard presents correctness, timings, bytecode / instruction information, and an explanation of the measured run.

See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for component responsibilities and the two execution paths.

## Run tests

```bash
python -m unittest discover -s tests -v
```

## Understanding benchmark results

- The interpreter has no translation stage, so translation is reported as **Not applicable**.
- Lexer and parser timings are measured independently for each path; they are common preprocessing stages, not interpreter-only or compiler-only optimizations.
- The compiler path includes translation overhead before VM execution.
- Tiny programs can be dominated by Python overhead, machine load, and timer resolution. Do not conclude that one approach is always faster from one run.
- Repeat runs and compare averages or medians for more reliable observations. Instruction count is a structural metric, not elapsed time.

More detail: [`docs/BENCHMARKING.md`](docs/BENCHMARKING.md).

## Project presentation

The presentation used for the project demonstration is included at [`presentation/Project_Presentation.pptx`](presentation/Project_Presentation.pptx).

## Limitations and future work

This is a teaching mini-language, not a production compiler or a full implementation of C. Possible extensions include functions, arrays, strings, richer types, intermediate-code optimization, AST / VM animation, larger benchmark suites, and JSON / PDF report export.

## References

- Aho, Lam, Sethi, and Ullman, *Compilers: Principles, Techniques, and Tools*, 2nd ed., 2006.
- Cooper and Torczon, *Engineering a Compiler*, 2nd ed., 2011.
- Grune and Jacobs, *Parsing Techniques: A Practical Guide*, 2nd ed., 2008.
- [Python documentation](https://docs.python.org/3/)
- [Flask documentation](https://flask.palletsprojects.com/)
