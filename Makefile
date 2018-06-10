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
	./env_local/bin/python -m unittest neomnesis/task/test/test_task.py
	./env_local/bin/python -m unittest neomnesis/common/data_type/test/test_data_type.py

test: env_local
	./env_local/bin/tox

testSync: env_local
	./env_local/bin/python -m unittest neomnesis/sync/test/test_mkarchive.py

devCmdLineClient:
ifeq ($(ENV), "")
	$(error Usage: make <command> ENV=(local|dev|prod))
endif
	mkfifo /tmp/pipe
	bash ./scripts/start_cmd_line_client_application.sh ${ENV} < /tmp/pipe
	echo "create note" > cmdlineclient
	echo "edit_all" > cmdlineclient


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

startLocalApplication:
	nohup bash ./scripts/start_application.sh local > server_logs.log 2>&1 &
	bash ./scripts/start_cmd_line_client_application.sh local

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
