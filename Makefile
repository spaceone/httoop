#!/usr/bin/make -f

.PHONY: dist pushrelease pushreleasetest clean lint lint-fix format

dist:
	python3 setup.py sdist bdist_wheel

pushreleasetest:
	python3 -m twine upload --repository testpypi dist/*

pushrelease:
	python3 -m twine upload dist/*

clean:
	$(RM) -r dist

lint:
	-prek run -a

lint-fix:
	-prek run -a --hook-stage manual ruff-fix

format:
	-prek run -a --hook-stage manual ruff-format

ty:
	-prek run -a --hook-stage manual ty

mypy:
	-prek run -a --hook-stage manual mypy
