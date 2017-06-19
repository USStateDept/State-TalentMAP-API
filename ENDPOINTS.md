### Endpoints

This is a simple list of endpoints as a temporary documentation placeholder until more interactive documentation can be provided.

| Endpoint | Data |
| -------- | ---- |
| `/api/v1/language/` | List of all available language instances |
| `/api/v1/language/proficiencies/` | List of all available language proficiency levels |
| `/api/v1/language/qualifications/` | List of all available language qualifications |
| `/api/v1/position/` | List all positions |

### Filters

Filters are specified via GET parameters. For instance, to limit the list of positions to only those requiring German, one would access:

`/api/v1/position/?language_requirements__language__name=German`

You can combine filters. To look for positions that require German with at least a spoken proficiency of 2+, you can use:

`/api/v1/position/?language_requirements__language__name=German&language_requirements__spoken_proficiency__at_least=2plus`

Note the use of `2plus` instead of `2+` - this is because `+` is a reserved delimiter in URLs.

To search for a position where multiple values are true (via logical AND) combine them into a single parameter. For example, positions that require both French and German:

`/api/v1/position/?language_requirements__language__name=German,French`

To search where either case is true (via logical OR), use the same parameter twice:

`/api/v1/position/?language_requirements__language__name=German&language_requirements__language__name=French`
