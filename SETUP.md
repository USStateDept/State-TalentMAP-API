# Setup

## Database
Run the following from your terminal inside the project dir...
*If you have never run the `migrate` command, you can skip to that step.*
```
docker-compose run app bash
psql -U talentmap-user -h db talentmap
DROP SCHEMA public CASCADE;
CREATE SCHEMA public;
\q
exit
docker-compose run app python manage.py migrate
docker-compose run app python manage.py schedule_synchronization_job --set-defaults
docker-compose run app python manage.py synchronize_data --test
docker-compose run app python manage.py load_all_data talentmap_api/data/test_data/real/
docker-compose run app python manage.py create_demo_environment
```