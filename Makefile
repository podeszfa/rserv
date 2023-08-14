.PHONY: all install clean installer

EXE=
SEP=:
venv=./venv/bin
ifneq (,$(findstring Windows,$(OS)))
    EXE=.exe
	SEP=;
	venv=./venv/Scripts
endif

all: rserv$(EXE)

./venv:
	@if [ ! -d ./venv ]; then \
	  echo Installing venv; \
	  python -m venv venv && $(MAKE) install || rm -fR ./venv; \
	fi

rserv$(EXE): ./venv rserv.py
	LC_ALL=C $(venv)/pyinstaller --distpath . -y --clean --onefile --add-data "LICENSE$(SEP)." --python-option "W ignore" --hidden-import rpy2 rserv.py

rserv-installer.exe: rserv.exe
	makensis installer.nsi

installer: rserv-installer.exe

requirements.txt:
	$(venv)/pipreqs --force

clean:
	@rm -fR build dist __pycache__ rserv$(EXE) rserv.spec venv

install: ./venv
	$(venv)/python -m pip install pipreqs
	$(venv)/python -m pip install pyinstaller
	$(MAKE) requirements.txt
	$(venv)/python -m pip install -r requirements.txt


