all:
	pyinstaller --onefile --hidden-import=urllib2 ci.py

bootstrap:
	pip install -r requirements.txt

lint:
	flake8 *.py

install:
	cp dist/ci /usr/local/bin/ci
