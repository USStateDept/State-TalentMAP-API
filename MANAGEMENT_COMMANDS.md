### Management Commands

The following management commands are available. More detailed help can be found by using each commands provided `help` option.

##### Data Loading

* `load_xml <FILE> <MODE>` - Provided to load reference data into the database. XML files should be in the format as provided by the Department of State (these are not currently provided in the repository). Available modes are: "languages", "proficiencies", "grades".

* `load_all_data <FILEPATH>` - Loads all XML files from the given file path, using default Department of State XML file names.

* `update_relationships` - Updates all relationships for models which have foreign keys (this is useful if there was a partial data load).

* `create_user <USERNAME> <EMAIL> <PASSWORD> <FIRST_NAME> <LAST_NAME>` - Creates a user
* `create_user <USERNAME> <EMAIL> <PASSWORD> <FIRST_NAME> <LAST_NAME> --settoken <TOKEN>` - Creates a user and sets their initial authentication token to the provided value.
* `create_seeded_users` - Creates testing users based on design personas, and assigns random skills and grades from available positions.

* `create_classifications` - Creates all position classifications, called by `load_all_data`.
* `create_base_permissions` - Creates app-wide baseline permissions and groups.
* `create_demo_environment` - Creates all seeded users and a bidcycle with all positions.
