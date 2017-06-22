'''
This file contains helpers for loading data into the database from XML files
'''

import defusedxml.lxml as ET


class XMLloader():

    def __init__(self, model, instance_tag, tag_map):
        '''
        Instantiates the XMLloader

        Args:
            model (Class) - The model class used to create instances
            instance_tag (str) - The name of a tag which defines a new instance
            tag_map (dict) - A dictionary defining what XML tags map to which model fields
        '''

        self.model = model
        self.instance_tag = instance_tag
        self.tag_map = tag_map

    def create_models_from_xml(self, xml_filepath):
        '''
        Loads data from an XML file into a model, using a defined mapping of fields
        to XML tags.

        Args:
            xml_filepath (str) - The filepath to the XML file to load

        Returns:
            int: The number of instances created from the XML file
        '''

        # A list of instances to instantiate with a bulk create
        instances = []

        # Parse the XML tree
        xml_tree = ET.parse(xml_filepath)

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
                        setattr(instance, self.tag_map[key], item.text)
                    else:
                        # Tag map is a callable, so call it with instance + item
                        self.tag_map[key](instance, item)

            # Append our instance
            instances.append(instance)

        # Create our instances
        self.model.objects.bulk_create(instances)

        return len(instances)
