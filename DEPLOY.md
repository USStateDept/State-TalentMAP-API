## Deploying a new build

After installing a new set of code, perform the following actions

### Update dependencies

Execute `pip install -r requirements.txt` to install any new dependencies. This requires internet access; if that is unavailable, you will need to install the new dependencies from a tar or zip file

### Perform migrations

Execute `python manage.py migrate` to perform database migrations

### (Optional) Clear Database

If you are in a development or testing environment, you may wish to empty your database. To do this, execute `python manage.py flush`

### Create base permissions

Create base permissions using `python manage.py create_base_permissions`

### Restart HTTPD

If you are deployed via Apache, restart the HTTPD service
