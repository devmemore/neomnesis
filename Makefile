test:
	python -m unittest neomnesis

createDocker:
	docker build . 
