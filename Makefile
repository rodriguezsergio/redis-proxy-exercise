test:
	docker-compose build && docker-compose up

run:
	docker-compose build && docker-compose up redis segment