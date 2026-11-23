.PHONY: install test validate build

install:
	python -m pip install -r requirements-dev.txt

test:
	pytest

validate:
	sam validate --lint

build:
	sam build
