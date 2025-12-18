PY3 = python3
PIP3 = pip3
PYPY3 = pypy3

default: install

clean:
	rm -f dist/*
	rm -rf build/*

pypy3: clean
	$(PYPY3) -m build
	$(PYPY3) -m pip install .	

install: clean pkg
	$(PY3) -m pip install .

pkg: clean
	$(PY3) -m build

uninstall: clean
	$(PIP3) uninstall srtfu
	
upload: clean pkg	
	twine upload dist/*

upgrade:
	$(PIP3) install --upgrade srtfu

debian: 
	$(PIP3) install --upgrade srtfu --break-system-packages


