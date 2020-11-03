#!/usr/bin/make -f

dist:
	python3 setup.py sdist bdist_wheel

pushreleasetest:
	python3 -m twine upload --repository testpypi dist/*

pushrelease:
	python3 -m twine upload dist/*

clean:
	$(RM) -r dist
