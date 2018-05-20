.PHONY: env help use
.DEFAULT: use
ENV=""
use:
	@echo "clean                         Cleans the project"
	@echo "env                           Generate virutal env"
	@echo "run                           Run local server"
	@echo "unittest                      Run the unittests"
	@echo "integrationTests              Run integration tests in docker"
	@echo "tests                         Run all tests"
	@echo "help                          alias for use"
	@echo "startServerApplication        Run the server"
	@echo "startClientApplication        Run the command line client"

help: use
	
env:
ifeq ($(ENV), "")
	$(error Usage: make <command> ENV=(local|dev|prod))
endif
	bash scripts/create_venv.sh ${ENV}

unittest: env_local
	./env_local/bin/python neomnesis/task/test/test_task.py

test: env_local
	./env_local/bin/tox

createDocker:
	docker build .

startServerApplication:
ifeq ($(ENV), "")
	$(error Usage: make <command> ENV=(local|dev|prod))
endif
	bash ./scripts/start_application.sh ${ENV}

startClientApplication:
ifeq ($(ENV), "")
	$(error Usage: make <command> ENV=(local|dev|prod))
endif
	bash ./scripts/start_cmd_line_client_application.sh ${ENV}

uninstall:
	rm -r ~/.neomnesis

runLocal:
ifeq ($(ENV), "")
	$(error Usage: make <command> ENV=(local|dev|prod))
endif
	bash scripts/start_application.sh local


runDocker:
ifeq ($(ENV), "")
	$(error Usage: make <command> ENV=(local|dev|prod))
endif
	bash  
