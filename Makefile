all: init test

init:
	pip install -r requirements.txt

test:
	python tests/test_util.py
	python tests/test_common.py

.PHONY: all init test
