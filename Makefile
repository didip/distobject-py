.PHONY: test docker-test

test:
	pytest tests/

docker-test:
	docker compose up --build --abort-on-container-exit --exit-code-from distobject-py-test
