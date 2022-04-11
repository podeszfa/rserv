.PHONY: all install clean installer

EXE=
SEP=:
ifneq (,$(findstring Windows,$(OS)))
    EXE=.exe
	SEP=;
endif

all: rserv$(EXE)

rserv$(EXE): requirements.txt rserv.py
	pyinstaller --distpath . -y --clean --onefile --add-data "LICENSE$(SEP)." --python-option "W ignore" --hidden-import rpy2 rserv.py

rserv-installer.exe: rserv.exe
	makensis installer.nsi

installer: rserv-installer.exe

requirements.txt:
	pipreqs --force

clean:
	@rm -fR build dist __pycache__ requirements.txt rserv$(EXE) rserv.spec

install:
	python -m pip install pipreqs
	python -m pip install pyinstaller
