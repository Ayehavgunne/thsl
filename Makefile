OSFLAG :=
ifeq ($(OS),Windows_NT)
	OSFLAG += -D WIN32
	ifeq ($(PROCESSOR_ARCHITECTURE),AMD64)
		OSFLAG += -D AMD64
	endif
	ifeq ($(PROCESSOR_ARCHITECTURE),x86)
		OSFLAG += -D IA32
	endif
else
	UNAME_S := $(shell uname -s)
	ifeq ($(UNAME_S),Linux)
		OSFLAG += -D LINUX
	endif
	ifeq ($(UNAME_S),Darwin)
		OSFLAG += -D OSX
	endif
		UNAME_P := $(shell uname -p)
	ifeq ($(UNAME_P),x86_64)
		OSFLAG += -D AMD64
	endif
		ifneq ($(filter %86,$(UNAME_P)),)
	OSFLAG += -D IA32
		endif
	ifneq ($(filter arm%,$(UNAME_P)),)
		OSFLAG += -D ARM
	endif
endif

EXPECTED_PYTHON_VERSION := 3
PYTHON_VERSION := $(shell python3 --version | cut -d" " -f2 | cut -d"." -f1)
SITE_PACKAGES := $(shell pip show pip | grep '^Location' | cut -f2 -d':')
ROOT := $(dir $(abspath $(firstword $(MAKEFILE_LIST))))
BIN_PATH := ${ROOT}.env/bin
PYTHON_PATH := ${BIN_PATH}/python
ACTIVATE_PATH := ${BIN_PATH}/activate
PIP_PATH := ${BIN_PATH}/pip
SRC := ${ROOT}thsl
TEST := ${ROOT}tests
.PHONY: check-python black isort mypy lint test check setup format env

all: setup

$(SITE_PACKAGES): requirements.txt
	${PIP_PATH} install -r requirements.txt

setup: $(SITE_PACKAGES)

black: setup
	. ${ACTIVATE_PATH} && ${BIN_PATH}/black ${SRC}

isort: setup
	. ${ACTIVATE_PATH} && ${BIN_PATH}/isort --profile black ${SRC}

format: setup isort black

mypy: setup
	@ECHO ${OSFLAG}
	. ${ACTIVATE_PATH} && ${BIN_PATH}/mypy ${SRC}

lint: setup
	. ${ACTIVATE_PATH} && ${BIN_PATH}/pylint ${SRC}

test: setup
	@ECHO ${ROOT}
	. ${ACTIVATE_PATH} && PYTHONPATH=${ROOT} ${BIN_PATH}/pytest ${TEST}

check: mypy lint

env: check-python
	python3 -m venv .env
	. ${ACTIVATE_PATH} && ${PIP_PATH} install -U pip setuptools wheel

check-python:
ifneq ($(PYTHON_VERSION), $(EXPECTED_PYTHON_VERSION))
	$(error Expected Python $(EXPECTED_PYTHON_VERSION). Found $(PYTHON_VERSION))
endif
