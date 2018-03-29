.PHONY: env help use
.DEFAULT: use
ENV=""
use:
	@echo "clean                   Cleans the project"
	@echo "env                     Generate virutal env"
	@echo "run                     Run local server"
	@echo "unittest                Run the unittests"
	@echo "integrationTests        Run integration tests in docker"
	@echo "tests                   Run all tests"
	@echo "help                    alias for use"
	@echo "startApplication        Run the server"

help: use
	
env:
ifeq ($(ENV), "")
	$(error Usage: make <command> ENV=(local|dev|prod))
endif
	bash ./scripts/create_venv.sh ${ENV}

unittest: env_local
	./env_local/bin/python neomnesis/task/test/test_task.py

createDocker:
	docker build .

startApplication:
	bash ./scripts/start_application.sh ${ENV}

uninstall:
	rm -r ~/.neomnesis

run:
	bash scripts/start_application.sh local
