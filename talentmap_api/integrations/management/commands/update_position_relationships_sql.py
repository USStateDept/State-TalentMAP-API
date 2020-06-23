import logging

from django.core.management.base import BaseCommand

from django.db import connection


class Command(BaseCommand):
    help = 'Runs SQL to update the position relationships'
    logger = logging.getLogger(__name__)

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            cursor.execute("update position_position set grade_id = position_grade.id from position_grade where position_grade.code = position_position._grade_code")
            cursor.execute("update position_position set skill_id = position_skill.id from position_skill where position_skill.code = position_position._skill_code;")
            cursor.execute("update position_position set post_id = organization_post.id from organization_post where organization_post._location_code = position_position._location_code;")
            cursor.execute("update position_position set organization_id = organization_organization.id from organization_organization where organization_organization.code = position_position._org_code;")
            cursor.execute("update position_position set bureau_id = organization_organization.id from organization_organization where organization_organization.code = position_position._bureau_code;")
            cursor.execute("update position_position set description_id = position_capsuledescription.id from position_capsuledescription where position_capsuledescription._pos_seq_num = position_position._seq_num;")
