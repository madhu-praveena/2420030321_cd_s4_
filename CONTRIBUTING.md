# Contributing

Contributions that improve correctness, documentation, accessibility, or test coverage are welcome.

1. Fork the repository and create a focused feature branch.
2. Create and activate a virtual environment.
3. Install dependencies with `python -m pip install -r requirements.txt`.
4. Make a focused change and add or update tests.
5. Run `python -m unittest discover -s tests -v`.
6. Open a pull request describing the change and how it was tested.

Please keep the mini-language behavior documented and avoid using Python `eval()` or `exec()` to execute user-supplied source code.
