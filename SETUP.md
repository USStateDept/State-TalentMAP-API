# Setup

## Oracle
Before building the container, perform the following:

1. Create an account on the Oracle Container Registry - https://container-registry.oracle.com/
2. `docker login container-registry.oracle.com`

## Database
Ensure you have built and run the app:
```
docker-compose build
docker-compose up
```

Then run the following from your terminal inside the project dir...
```
docker-compose run app python manage.py migrate
docker-compose run app python manage.py create_base_permissions
docker-compose run app python manage.py create_demo_environment

docker-compose run mock_fsbid npm run migrate
docker-compose run mock_fsbid npm run seed
```
