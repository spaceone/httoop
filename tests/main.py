#!/usr/bin/env python

import sys
from os.path import abspath, dirname
from subprocess import STDOUT, Popen
from types import ModuleType


def importable(module):
	try:
		m = __import__(module, globals(), locals())
		return type(m) is ModuleType
	except ImportError:
		return False


def main():
	cmd = ["py.test", "-r", "fsxX", "--durations=1", "--ignore=tmp", '--color=yes', '--continue-on-collection-errors']

	if importable("pytest_cov"):
		cmd.append("--cov=httoop")
#		cmd.append("--no-cov-on-fail")
		cmd.append("--cov-report=html")

	cmd.append(dirname(abspath(__file__)))

	raise SystemExit(Popen(cmd, stdout=sys.stdout, stderr=STDOUT).wait())


if __name__ == "__main__":
	main()
