unittest:
	python -m unittest -v neomnesis.server.task.test

createDocker:
	docker build .

startApplication:
	FLASK_APP=neomnesis/server/server_task.py
	${PY} -m flask run FLASK_APP=$(FLASK_APP)	

uninstall:
	rm -r ~/.neomnesis

