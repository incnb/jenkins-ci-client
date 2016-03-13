install:
	sudo pip install -r requirements.txt
	sudo cp ci.py /usr/local/bin/ci
	sudo chmod +x /usr/local/bin/ci
