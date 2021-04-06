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

## Email Notifications
For local development, create an account with SparkPost to configure SMTP. Copy your account details into a .env file at the root of this project, formatted as such:
```
EMAIL_HOST=smtp.sparkpostmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=SMTP_Injection
EMAIL_HOST_PASSWORD=xxxxxxxxxxxxxxxxxxxxxxxxxxxx
EMAIL_FROM_ADDRESS=xxxxxxxx@xxxxxxx.com
EMAIL_USE_TLS=true
EMAIL_IS_DEV=true # Use for local development
EMAIL_DEV_TO=xxxxxxxx@xxxxxx.com # Use your own email address. All email notifications will get sent to this address instead of the ones defined in the user's profile
```
Do not commit this file to Github. .gitignore is already configured to ignore this file.