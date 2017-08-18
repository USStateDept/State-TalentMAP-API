'''
This file contains helpers for loading data into the database from XML files
'''

from django.forms.models import model_to_dict
from django.db.models.constants import LOOKUP_SEP
from django.db.models import Q

import defusedxml.lxml as ET
import difflib
import logging
import re


class XMLloader():

    def __init__(self, model, instance_tag, tag_map, collision_behavior=None, collision_field=None):
        '''
        Instantiates the XMLloader

        Args:
            model (Class) - The model class used to create instances
            instance_tag (str) - The name of a tag which defines a new instance
            tag_map (dict) - A dictionary defining what XML tags map to which model fields
            collision_behavior (str) - What to do when a collision is detected (update or delete)
            collision_field (str) - The field to detect collisions on
        '''

        self.model = model
        self.instance_tag = instance_tag
        self.tag_map = tag_map
        self.collision_behavior = collision_behavior
        self.collision_field = collision_field

    def create_models_from_xml(self, xml_filepath):
        '''
        Loads data from an XML file into a model, using a defined mapping of fields
        to XML tags.

        Args:
            xml_filepath (str) - The filepath to the XML file to load

        Returns:
            list: The list of new instance ids
            list: The list of updated instance ids
        '''

        # A list of instances to instantiate with a bulk create
        new_instances = []

        # A list of updated instance id's
        updated_instances = []

        # Parse the XML tree
        parser = ET._etree.XMLParser(recover=True)
        xml_tree = ET.parse(xml_filepath, parser)

        # Get the root node
        root = xml_tree.getroot()

        # Get a set of all tags which match our instance tag
        instance_tags = root.findall(self.instance_tag, root.nsmap)

        # For every instance tag, create a new instance and populate it
        for tag in instance_tags:
            instance = self.model()
            for key in self.tag_map.keys():
                # Find a matching entry for the tag from the tag map
                item = tag.find(key, tag.nsmap)
                if item is not None:
                    # If we have a matching entry, and the map is not a callable,
                    # set the instance's property to that value
                    if not callable(self.tag_map[key]):
                        data = item.text
                        if data and len(data.strip()) > 0:
                            setattr(instance, self.tag_map[key], data)
                    else:
                        # Tag map is a callable, so call it with instance + item
                        self.tag_map[key](instance, item)

            # Check for collisions
            if self.collision_field:
                q_kwargs = {}
                q_kwargs[self.collision_field] = getattr(instance, self.collision_field)
                collisions = type(instance).objects.filter(**q_kwargs)
                if collisions.count() > 1:
                    logging.getLogger('console').warn(f"Looking for collision on {type(instance).__name__}, field {self.collision_field}, value {getattr(instance, self.collision_field)}; found {collisions.count()}. Skipping item.")
                    continue
                elif collisions.count() == 1:
                    # We have exactly one collision, so handle it
                    if self.collision_behavior == 'delete':
                        collisions.delete()
                        new_instances.append(instance)
                    elif self.collision_behavior == 'update':
                        # Update our collided instance
                        update_dict = dict(instance.__dict__)
                        del update_dict["id"]
                        del update_dict["_state"]
                        collisions.update(**update_dict)
                        updated_instances.append(collisions.first().id)
                        continue
                    elif self.collision_behavior == 'skip':
                        # Skip this instance, because it already exists
                        continue
                else:
                    new_instances.append(instance)
            else:
                # Append our instance
                new_instances.append(instance)

        new_instances = self.model.objects.bulk_create(new_instances)
        new_instances = [instance.id for instance in new_instances]

        # Create our instances
        return (new_instances, updated_instances)


def strip_extra_spaces(field):
    '''
    Creates a function for processing a specific field by removing duplicated and
    trailing spaces during XML loading
    '''
    def process_function(instance, item):
        setattr(instance, field, re.sub(' +', ' ', item.text).strip())
    return process_function


def parse_boolean(field, true_values_override=None):
    '''
    Creates a function for processing booleans from a string
    '''
    def process_function(instance, item):
        true_values = ["1", "True", "true", "Y", "T"]
        if true_values_override:
            true_values = true_values_override
        value = False
        if item.text in true_values:
            value = True
        setattr(instance, field, value)
    return process_function


def canonize_country(field):
    '''
    Ensures all location country tags have the same formatting. This is a temporary solution
    until a full location list can be obtained
    '''
    def process_function(instance, item):
        canon = {
            "afghanistan": "Afghanistan",
            "albania": "Albania",
            "algeria": "Algeria",
            "angola": "Angola",
            "argentina": "Argentina",
            "australia": "Australia",
            "austria": "Austria",
            "azerbaijan": "Azerbaijan",
            "belgium": "Belgium",
            "botswana": "Botswana",
            "brazil": "Brazil",
            "burkina faso": "Burkina Faso",
            "burundi": "Burundi",
            "cambodia": "Cambodia",
            "cameroon": "Cameroon",
            "chad": "Chad",
            "china": "China",
            "colombia": "Colombia",
            "congo": "Congo",
            "congo, democratic republic": "Congo, Democratic Republic",
            "costa rica": "Costa Rica",
            "cote d'ivoire": "Cote D'Ivoire",
            "croatia": "Croatia",
            "cyprus": "Cyprus",
            "denmark": "Denmark",
            "djibouti": "Djibouti",
            "ecuador": "Ecuador",
            "egypt": "Egypt",
            "el salvador": "El Salvador",
            "eritrea": "Eritrea",
            "ethiopia": "Ethiopia",
            "france": "France",
            "gabon": "Gabon",
            "germany": "Germany",
            "guatemala": "Guatemala",
            "guinea": "Guinea",
            "haiti": "Haiti",
            "honduras": "Honduras",
            "india": "India",
            "indonesia": "Indonesia",
            "iraq": "Iraq",
            "italy": "Italy",
            "jordan": "Jordan",
            "kenya": "Kenya",
            "korea, republic of": "Korea, Republic Of",
            "lebanon": "Lebanon",
            "lesotho": "Lesotho",
            "liberia": "Liberia",
            "lithuania": "Lithuania",
            "macedonia": "Macedonia",
            "madagascar": "Madagascar",
            "malawi": "Malawi",
            "mali": "Mali",
            "mauritania": "Mauritania",
            "mexico": "Mexico",
            "micronesia, federated states o": "Micronesia, Federated States Of",
            "mongolia": "Mongolia",
            "montenegro": "Montenegro",
            "mozambique": "Mozambique",
            "netherlands": "Netherlands",
            "netherlands antilles": "Netherlands Antilles",
            "nicaragua": "Nicaragua",
            "nigeria": "Nigeria",
            "norway": "Norway",
            "pakistan": "Pakistan",
            "panama": "Panama",
            "papua new guinea": "Papua New Guinea",
            "paraguay": "Paraguay",
            "peru": "Peru",
            "portugal": "Portugal",
            "russia": "Russia",
            "saudi arabia": "Saudi Arabia",
            "serbia and montenegro": "Serbia And Montenegro",
            "sierra leone": "Sierra Leone",
            "singapore": "Singapore",
            "south sudan": "South Sudan",
            "sudan": "Sudan",
            "switzerland": "Switzerland",
            "tajikistan": "Tajikistan",
            "tanzania, united republic of": "Tanzania, United Republic Of",
            "thailand": "Thailand",
            "trinidad and tobago": "Trinidad And Tobago",
            "tunisia": "Tunisia",
            "turkey": "Turkey",
            "turkmenistan": "Turkmenistan",
            "uganda": "Uganda",
            "ukraine": "Ukraine",
            "united arab emirates": "United Arab Emirates",
            "venezuela": "Venezuela",
            "vietnam": "Vietnam",
            "zimbabwe": "Zimbabwe",
        }

        # The only time a location's country is blank is if it is domestic
        country = "United States of America"

        if item.text:
            candidates = difflib.get_close_matches(item.text.lower(), canon.keys())
            if len(candidates) > 1:
                logging.getLogger('console').warn(f"While canonizing country {item.text} got {len(candidates)} canidates: {'; '.join(candidates)}")
            country = canon[candidates[0]]

        logging.getLogger('console').info(f"Canonizing: {item.text} -> {country}")
        setattr(instance, field, country)

    return process_function
