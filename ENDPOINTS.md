### Endpoints

For a list of all available endpoints, see the Swagger documentation at the API root.

### Filters

Filters are specified via GET parameters. For instance, to limit the list of positions to only those requiring German, one would access:

`/api/v1/position/?languages__language__name=German`

You can combine filters. To look for positions that require German with at least a spoken proficiency of 2+, you can use:

`/api/v1/position/?languages__language__name=German&languages__spoken_proficiency__at_least=2plus`

Note the use of `2plus` instead of `2+` - this is because `+` is a reserved delimiter in URLs.

To search for a position where multiple values are true (via logical AND) combine them into a single parameter. For example, positions that require both French and German:

`/api/v1/position/?languages__language__name=German,French`

To search where either case is true (via logical OR), use the `in` lookup:

`/api/v1/position/?languages__language__name__in=German,French`
