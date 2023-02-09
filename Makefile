ROOT := $(dir $(abspath $(firstword $(MAKEFILE_LIST))))
SRC := ${ROOT}thsl
TEST := ${ROOT}tests
.PHONY: black black-check usort usort-check format format-check mypy ruff ruff-fix fix test check

black:
	pdm run black ${SRC}

black-check:
	pdm run black --check --diff ${SRC}

usort:
	pdm run usort format ${SRC}

usort-check:
	pdm run usort check ${SRC}

format:
	pdm run ufmt format ${SRC}

format-check:
	pdm run ufmt check ${SRC}

mypy:
	pdm run mypy ${SRC}

ruff:
	pdm run ruff ${SRC}

ruff-fix:
	pdm run ruff ${SRC} --fix

fix: ruff-fix

test:
	pdm run pytest ${TEST}

check: ruff format-check mypy
