# Сервис авторизации

К концу спринта у вас должен получиться сервис авторизации 
с системой ролей, написанный на Flask с использованием gevent.

## Локальная разработка в docker

1. Создать .env файл на основе .env.template:
```console
$ make env
```
2. Сбилдить и запустить:
```console
$ make up
```
3. Остановить приложение:
```console
$ make down
```
4. Посмотреть логи:
```console
$ make logs
```
5. Создать суперпользователя:
```console
$ make superuser
```
6. Описание API
```
http://127.0.0.1:5000/apidocs/
```

## Тесты
1. Сбилдить и запустить тесты:
```console
$ make up-tests
```
2. Прогнать тесты еще раз:
```console
$ make run-tests
```
3. Остановить и удалить контейнеры:
```console
$ make down-tests
```

## Создание учетной записи через CLI
Для создания учетной записи 
1. Подключитесь к контейнеру с flask 
```console
$ docker exec -it auth_sprint_1_auth_flask_1 bash
```
2. Выполните команду:
```console
$ flask user create <user_name> <user@email> <password>
```

## Jaeger
Перейти в Jaeger UI
```
http://127.0.0.1:16686/
```

## Интеграция с другими сервисами через Protobuf
Для получения информации о пользователе 
сервис должен отправить access_token на auth/profile.
Пример запроса из сервиса async_api к сервису auth
```
https://github.com/pavlom10/Async_API_sprint_2/blob/7e46f0b4e0d80bafb234f08622e3e81201d10ec9/src/api/v1/film.py#L69
```