.PHONY: all install clean

EXE=
ifneq (,$(findstring Windows,$(OS)))
    EXE=.exe
endif

all: rserv$(EXE)

rserv$(EXE): requirements.txt rserv.py
	pyinstaller --distpath . -y --clean --onefile --python-option "W ignore" --hidden-import rpy2 rserv.py

requirements.txt:
	pipreqs --force

clean:
	@rm -fR build dist __pycache__ requirements.txt rserv$(EXE) rserv.spec

install:
	python -m pip install pipreqs
	python -m pip install pyinstaller
