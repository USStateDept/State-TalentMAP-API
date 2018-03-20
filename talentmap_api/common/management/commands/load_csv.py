from django.core.management.base import BaseCommand

import logging

from talentmap_api.common.xml_helpers import CSVloader
from talentmap_api.glossary.models import GlossaryEntry


class Command(BaseCommand):
    help = 'Loads a CSV into a supported model'
    logger = logging.getLogger(__name__)

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

        self.modes = {
            'glossary': mode_glossary_entry,
        }

    def add_arguments(self, parser):
        parser.add_argument('file', nargs=1, type=str, help="The CSV file to load")
        parser.add_argument('type', nargs=1, type=str, choices=self.modes.keys(), help="The type of data in the CSV")
        parser.add_argument('--delete', dest='delete', action='store_true', help='Delete collisions')
        parser.add_argument('--update', dest='update', action='store_true', help='Update collisions')
        parser.add_argument('--skippost', dest='skip_post', action='store_true', help='Skip post load functions')

    def handle(self, *args, **options):
        model, tag_map, collision_field, post_load_function = self.modes[options['type'][0]]()

        # Set / update the collision behavior
        collision_behavior = None
        if options['delete']:
            collision_behavior = "delete"
        elif options['update']:
            collision_behavior = "update"
        else:
            collision_behavior = "skip"

        loader = CSVloader(model, tag_map, collision_behavior, collision_field)
        new_ids, updated_ids = loader.create_models_from_csv(options['file'][0])

        # Run the post load function, if it exists
        if callable(post_load_function) and not options['skip_post']:
            post_load_function(new_ids, updated_ids)

        self.logger.info(f"CSV Load Report\n\tNew: {len(new_ids)}\n\tUpdated: {len(updated_ids)}\t\t")


def mode_glossary_entry():
    model = GlossaryEntry
    collision_field = "title"
    tag_map = {
        "title": "title",
        "definition": "definition",
        "link": "link",
    }

    return (model, tag_map, collision_field, None)
