all: test

test:
	python3 -m unittest discover -p '*.py'
