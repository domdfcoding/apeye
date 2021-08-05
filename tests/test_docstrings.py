# stdlib
import doctest
import inspect
import shutil
from pathlib import PurePosixPath
from textwrap import indent

# 3rd party
import pytest
from domdf_python_tools.utils import redirect_output

# this package
import apeye.url

VERBOSE = 1

ret = 0


def relative_to(self, *other):
	# From Python 3.8, pathlib.py
	if not other:
		raise TypeError("need at least one argument")
	parts = self._parts
	drv = self._drv
	root = self._root
	if root:
		abs_parts = [drv, root] + parts[1:]
	else:
		abs_parts = parts
	to_drv, to_root, to_parts = self._parse_args(other)
	if to_root:
		to_abs_parts = [to_drv, to_root] + to_parts[1:]
	else:
		to_abs_parts = to_parts
	n = len(to_abs_parts)
	cf = self._flavour.casefold_parts
	if (root or drv) if n == 0 else cf(abs_parts[:n]) != cf(to_abs_parts):
		formatted = self._format_parsed_parts(to_drv, to_root, to_parts)
		raise ValueError(f"{str(self)!r} does not start with {str(formatted)!r}")
	return self._from_parsed_parts('', root if n == 1 else '', abs_parts[n:])


@pytest.mark.parametrize("module", [apeye.url])
def test_docstrings(module, monkeypatch):

	# Always use pre-Python 3.9 implementation
	monkeypatch.setattr(PurePosixPath, "relative_to", relative_to)

	# Check that we were actually given a module.
	if inspect.ismodule(module):
		print(f"Running doctest in {module!r}".center(shutil.get_terminal_size().columns, '='))
	else:
		raise TypeError(f"testmod: module required; {module!r}")

	with redirect_output(combine=True) as (stdout, stderr):

		# Find, parse, and run all tests in the given module.
		finder = doctest.DocTestFinder()
		runner = doctest.DocTestRunner(verbose=VERBOSE >= 2)

		for test in finder.find(module, module.__name__):
			runner.run(test)

		runner.summarize(verbose=bool(VERBOSE))

	# results = doctest.TestResults(runner.failures, runner.tries)
	print(indent(stdout.getvalue(), "  "))

	if runner.failures:
		pytest.fail(msg=f"{runner.failures} tests failed")
