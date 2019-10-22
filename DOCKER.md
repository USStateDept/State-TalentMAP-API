# Using docker and docker-compose for local development

```sh
docker-compose build
docker-compose run app python manage.py migrate
docker-compose up
```

A server will now be running at `http://localhost:8000`.

You will need to `docker-compose build` whenever `requirements.txt` changes since the dependencies are installed in the docker image (see `Dockerfile`).

Note that in `docker-compose.yml`, `app` is the name of the service for the Django application, and `db` is the name of the database service. You can run any command within those service containers using `docker-compose run <SERVICE NAME> <COMMAND>`.

For example:

- `docker-compose run app py.test` will run the test suite.
- `docker-compose run db bash` will get you a shell in the `db` container.

Use `docker-compose -f docker-compose.yml -f docker-compose.local-fsbid.yml up` to run mock-fsbid container from local code.