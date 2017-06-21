Requirements:
* Python 3.6

### Setting up a virtual environment

It is strongly recommended to use a virtual environment while developing contributions to this project. This following steps will serve as a guide for setting up a virtual environment, and assumes Python 3.6 is installed.

##### Install Virtualenv
To install virtualenv, simply execute the following command:
```
pip install virtualenv
```

After virtualenv has been successfully installed, we can now make a virtual environment for the project. It can be located anywhere on the system, but it is generally recommended to place it alongside the project code for ease of location.

###### Locating Python 3.6
First, we need to determine the location of our Python 3.6 installation. Execute the following command to determine the location of the python executable. (If the shell command `python` is already aliased to Python 3.6, you can skip this step)

```
which python3.6
```

If python 3.6 is properly installed, this will return a path to the executable.

###### Creating the environment
The following command will create a virtual environment:
```
virtualenv -p <path to python 3.6> <desired location of the virtual environment>
```

If the `python` alias points to python 3.6, then the `-p` argument is optional. Examples:

```
virtualenv -p /usr/bin/python3.6 ~/Projects/talentmap-env

virtualenv ~/Projects/talentmap-env
```

###### Activating the Environment
To activate the environment in your terminal, execute the following command:
```
source ~/Projects/talentmap-env/bin/activate
```

If successful, the terminal prompt change to denote the active environment. To deactivate the environment, use the command `deactivate`.

The virtual environment has now been created. For further convenience, one can use the autoenv tool to automatically activate the virtual environment, but its usage falls outside the scope of this document.

#### Environment Variables
To run the Django server, the following environment variables must be set:

* `DJANGO_SECRET_KEY` - This should be any valid secret string. See the [Django documentation](https://docs.djangoproject.com/en/1.11/ref/settings/#std:setting-SECRET_KEY) for more information.
* `DJANGO_DEBUG` - This should be set to `false` when in production, but will default to `true` if otherwise unset.

#### Installing Requirements
To install requirements, execute:

```
pip install -r requirements.txt
```

#### Initial Database Setup
Before running the server, the database must be initialized.

#### Setting the Environment Variables
Django accesses database information by looking at the following environment variables:

* `DATABASE_URL` - This should be set to a valid database connection string. For example `postgres://username:password@url.com:5432/data_base_name`

This can be set by using `EXPORT` in the terminal, or setting up a profile or autoenv to set these.

#### Migrations
Once the database environment variable has been set, it is now possible to migrate the schema of the database. To do so, execute the following command in the directory where Django's `manage.py` file is located.

```
python manage.py migrate
```

This will modify the database such that it is up to date with the current desired schema.

#### Running the Server
With a properly migrated database, it is possible to start the server and begin processing API requests.

To access the API locally, one can run:
```
python manage.py runserver
```

Viewing `localhost:8000` should serve you with Swagger documentation on the API.

For production, it is recommended to set up uwsgi settings, which fall outside of the scope of this document.
