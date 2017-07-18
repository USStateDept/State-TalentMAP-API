### Management Commands

The following management commands are available. More detailed help can be found by using each commands provided `help` option.

##### Data Loading

* `load_xml <FILE> <MODE>` - Provided to load reference data into the database. XML files should be in the format as provided by the Department of State (These are not currently provided in the repository). Available modes are: "languages", "proficiencies", "grades"

* `load_all_data <FILEPATH>` - Loads all XML files from the given file path, using default DOS xml file names.

* `update_relationships` - Updates all relationships for models which have foreign keys. (This is useful if there was a partial data load)

* `create_user <USERNAME> <EMAIL> <PASSWORD>` - Creates a user
