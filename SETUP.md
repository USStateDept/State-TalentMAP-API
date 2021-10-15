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
docker-compose run app python manage.py create_demo_environment

docker-compose run mock_fsbid npm run migrate
docker-compose run mock_fsbid npm run seed
```

## Email Notifications
For local development, a fake SMTP server is included. The dashboard can be accessed on http://localhost:1080. Additional settings can be configured
in a .env file as such:
```
EMAIL_HOST_USER=xxxxxxxxxxxx # If you want to configure the SMTP server with a username
EMAIL_HOST_PASSWORD=xxxxxxxxxxxxxxxxxxxxxxxxxxxx # If you want to configure the SMTP server with a password
EMAIL_DEV_TO=xxxxxxxx@xxxxxx.com # If you want emails 'to' address to be overridden
```
This file is gitignored.