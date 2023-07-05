'''
This file contains helpers for loading data into the database from XML files
'''

import logging
import csv


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
        with open(csv_filepath, 'r', encoding='utf-8-sig') as csv_file:
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
