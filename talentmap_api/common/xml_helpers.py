'''
This file contains helpers for loading data into the database from XML files
'''

import logging
import re
import csv
import datetime

from io import StringIO
import defusedxml.lxml as ET

from talentmap_api.common.common_helpers import ensure_date, xml_etree_to_dict  # pylint: disable=unused-import


class XMLloader():

    def __init__(self, model, instance_tag, tag_map, collision_behavior=None, collision_field=None, override_loading_method=None, logger=None):
        '''
        Instantiates the XMLloader

        Args:
            model (Class) - The model class used to create instances
            instance_tag (str) - The name of a tag which defines a new instance
            tag_map (dict) - A dictionary defining what XML tags map to which model fields
            collision_behavior (str) - What to do when a collision is detected (update or delete)
            collision_field (str) - The field to detect collisions on
            override_loading_method (Method) - This will override the normal behavior of the load function
        '''

        self.model = model
        self.instance_tag = instance_tag
        self.tag_map = tag_map
        self.collision_behavior = collision_behavior
        self.collision_field = collision_field
        self.override_loading_method = override_loading_method
        self.last_pagination_start_key = None
        if logger:
            self.logger = logger
        else:
            self.logger = logging.getLogger(__name__)

    def create_models_from_xml(self, xml, raw_string=False):
        '''
        Loads data from an XML file into a model, using a defined mapping of fields
        to XML tags.

        Args:
            xml (str) - The XML to load; either a filepath or string
            raw_string (bool) - True if xml is a string, false (default) if it is a filepath

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

        if raw_string:
            xml = StringIO(xml)

        xml_tree = ET.parse(xml, parser)

        # Get the root node
        root = xml_tree.getroot()

        # Get a set of all tags which match our instance tag
        instance_tags = root.findall(self.instance_tag, root.nsmap)

        # If we get nothing using namespace, try without
        if len(instance_tags) == 0:
            instance_tags = [element for element in list(root.iter()) if element.tag == self.instance_tag]

        # For every instance tag, create a new instance and populate it
        self.last_tag_collision_field = None  # Used when loading piecemeal
        self.last_pagination_start_key = None  # Used when loading SOAP integrations

        self.logger.info(f"XML Loader found {len(instance_tags)} items")
        processed = 0
        start_time = datetime.datetime.now()
        for tag in instance_tags:
            if processed > 0:
                tot_sec = (len(instance_tags) - processed) * ((datetime.datetime.now() - start_time).total_seconds() / processed)
                days = int(tot_sec / 86400)
                hours = int(tot_sec % 86400 / 3600)
                minutes = int(tot_sec % 86400 % 3600 / 60)
                seconds = int(tot_sec % 86400 % 3600 % 60)
                etr = f"{days} d {hours} h {minutes} min {seconds} s"
                pct = str(int(processed / len(instance_tags) * 100))
            else:
                etr = "Unknown"
                pct = "0"
            self.logger.info(f"Processing... ({pct})% Estimated Time Remaining: {etr}")
            # Update the last pagination start key
            last_pagination_key_item = tag.find("paginationStartKey", tag.nsmap)
            if last_pagination_key_item is not None:
                self.last_pagination_start_key = last_pagination_key_item.text

            # Try to parse and load this tag
            try:
                processed += 1
                # Call override method if it exists
                if self.override_loading_method:
                    self.override_loading_method(self, tag, new_instances, updated_instances)
                else:
                    self.default_xml_action(tag, new_instances, updated_instances)
            except Exception as e:
                self.logger.exception(e)

        # We want to call the save() logic on each new instance
        for instance in new_instances:
            instance.save()
        new_instances = [instance.id for instance in new_instances]

        # Create our instances
        return (new_instances, updated_instances)

    def default_xml_action(self, tag, new_instances, updated_instances):
        '''
        Returns the instance and a boolean indicating if the instance was "updated" or not
        '''
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
            self.last_tag_collision_field = getattr(instance, self.collision_field)
            collisions = type(instance).objects.filter(**q_kwargs)
            if collisions.count() > 1:
                logging.getLogger(__name__).warn(f"Looking for collision on {type(instance).__name__}, field {self.collision_field}, value {getattr(instance, self.collision_field)}; found {collisions.count()}. Skipping item.")
                return
            elif collisions.count() == 1:
                # We have exactly one collision, so handle it
                if self.collision_behavior == 'delete':
                    collisions.delete()
                    new_instances.append(instance)
                elif self.collision_behavior == 'update':
                    # Update our collided instance
                    update_dict = {k: v for k, v in instance.__dict__.items() if k in collisions.first().__dict__.keys()}
                    del update_dict["id"]
                    del update_dict["_state"]
                    collisions.update(**update_dict)
                    updated_instances.append(collisions.first().id)
                    return collisions.first(), True
                elif self.collision_behavior == 'skip':
                    # Skip this instance, because it already exists
                    return None, False
            else:
                new_instances.append(instance)
        else:
            # Append our instance
            new_instances.append(instance)

        return instance, False


class CSVloader():

    def __init__(self, model, tag_map, collision_behavior=None, collision_field=None):
        '''
        Instantiates the CSVloader

        Args:
            model (Class) - The model class used to create instances
            tag_map (dict) - A dictionary defining what CSV column headers map to which model fields
            collision_behavior (str) - What to do when a collision is detected (update or delete)
            collision_field (str) - The field to detect collisions on
        '''

        self.model = model
        self.tag_map = tag_map
        self.collision_behavior = collision_behavior
        self.collision_field = collision_field

    def create_models_from_csv(self, csv_filepath):
        '''
        Loads data from an CSV file into a model, using a defined mapping of fields
        to CSV column titles.

        Args:
            csv_filepath (str) - The filepath to the CSV file to load

        Returns:
            list: The list of new instance ids
            list: The list of updated instance ids
        '''

        # A list of instances to instantiate with a bulk create
        new_instances = []

        # A list of updated instance id's
        updated_instances = []

        # Parse the CSV
        with open(csv_filepath, 'r') as csv_file:
            for line in csv.DictReader(csv_file):
                instance = self.model()
                for key in line.keys():
                    # If we have a matching entry, and the map is not a callable,
                    # set the instance's property to that value
                    if not callable(self.tag_map[key]):
                        data = line[key]
                        if data and len(data.strip()) > 0:
                            setattr(instance, self.tag_map[key], data)
                    else:
                        # Tag map is a callable, so call it with instance + item
                        self.tag_map[key](instance, line[key])

                # Check for collisions
                if self.collision_field:
                    q_kwargs = {}
                    q_kwargs[self.collision_field] = getattr(instance, self.collision_field)
                    collisions = type(instance).objects.filter(**q_kwargs)
                    if collisions.count() > 1:
                        logging.getLogger(__name__).warn(f"Looking for collision on {type(instance).__name__}, field {self.collision_field}, value {getattr(instance, self.collision_field)}; found {collisions.count()}. Skipping item.")
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
                            # strip out any "null" values from the update dict; when we parse the CSVs we set nulls where empty
                            # and this sometimes will inadvertently overwrite data we want to keep
                            update_dict = {k: v for k, v in update_dict.items() if v is not None}
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

        # We want to call the save() logic on each new instance
        for instance in new_instances:
            instance.save()
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


def parse_date(field):
    '''
    Parses date fields into datetime
    '''
    def process_function(instance, item):
        setattr(instance, field, ensure_date(item.text))
    return process_function


def append_to_array(field):
    '''
    Appends the item to the array field
    '''
    def process_function(instance, item):
        getattr(instance, field).append(item.text)
    return process_function


def get_nested_tag(field, tag, many=False):
    '''
    Creates a function to grab a nested tag
    If the many parameter is set to True, it will concatenate them into a comma
    seperated list as a string
    '''

    def process_function(instance, item):
        if not many:
            setattr(instance, field, item.find(tag).text)
        else:
            data = [element.text for element in list(item.iter()) if element.tag == tag]
            setattr(instance, field, ",".join(data))
    return process_function


def set_foreign_key_by_filters(field, foreign_field, lookup="__iexact"):
    '''
    Creates a function which will search the model associated with the foreign key
    specified by the foreign field parameter, matching on tag contents. Use this when
    syncing reference data.
    '''

    def process_function(instance, item):
        if item is not None and item.text:
            foreign_model = type(instance)._meta.get_field(field).related_model
            search_parameter = {f"{foreign_field}{lookup}": item.text}
            setattr(instance, field, foreign_model.objects.filter(**search_parameter).first())

    return process_function
