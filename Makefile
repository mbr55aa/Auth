env:
	cp config/.env.template config/.env

up:
	docker-compose up --build -d

down:
	docker-compose down --remove-orphans

superuser:
	docker-compose exec auth_flask flask user create admin admin@localhost 123

logs:
	docker-compose logs

up-tests:
	docker-compose -f ./tests/functional/docker-compose.yml up --build -d
	docker-compose -f ./tests/functional/docker-compose.yml exec auth_flask flask user create admin admin@localhost 123
	docker-compose -f ./tests/functional/docker-compose.yml exec auth_flask pytest .

run-tests:
	docker-compose -f ./tests/functional/docker-compose.yml exec auth_flask pytest .

down-tests:
	docker-compose -f ./tests/functional/docker-compose.yml down --remove-orphans

logs-tests:
	docker-compose -f ./tests/functional/docker-compose.yml logs

