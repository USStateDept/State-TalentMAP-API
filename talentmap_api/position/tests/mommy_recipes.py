from model_mommy import mommy
from model_mommy.recipe import Recipe, seq, foreign_key
from rest_framework import status

from talentmap_api.position.models import Position, Grade, Skill

grade = Recipe(
    Grade,
    code=seq("")
)

skill = Recipe(
    Skill,
    code=seq("")
)

position = Recipe(
    Position,
    grade=foreign_key('grade'),
    skill=foreign_key('skill')
)
