from model_mommy.recipe import Recipe, seq, foreign_key

from talentmap_api.language.models import Language, Proficiency, Qualification

language = Recipe(
    Language,
    code=seq("")
)

proficiency = Recipe(
    Proficiency,
    code=seq("")
)

qualification = Recipe(
    Qualification,
    language=foreign_key('language'),
    written_proficiency=foreign_key('proficiency'),
    spoken_proficiency=foreign_key('proficiency')
)
