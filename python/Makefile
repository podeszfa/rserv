.PHONY: all install clean

all: rserv.exe

rserv.exe: requirements.txt rserv.py
	pyinstaller --distpath . -y --clean --onefile --hidden-import rpy2 rserv.py

requirements.txt:
	pipreqs --force

clean:
	@rm -fR build dist __pycache__ requirements.txt rserv.exe rserv.spec

install:
	python -m pip install pipreqs
	python -m pip install pyinstaller
