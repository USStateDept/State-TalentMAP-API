import datetime
import logging
import os

from dateutil.relativedelta import relativedelta
import defusedxml.lxml as ET

from django.db import models
from django.apps import apps
from django.utils import timezone

from talentmap_api.integrations.synchronization_helpers import get_synchronization_information, get_soap_client
from talentmap_api.common.xml_helpers import XMLloader
from talentmap_api.common.common_helpers import ensure_date


class SynchronizationJob(models.Model):
    '''
    Represents a synchronization job, consisting of a database model, WSDL commands,
    and timing.

    Synchronization jobs are evaluated by the synchronize_data command, which should
    be called by the deployment environment's scheduling software (e.g. cron)
    '''

    # Some useful time constants, in seconds
    TIME_YEAR = 31536000
    TIME_WEEK = 604800
    TIME_DAY = 86400
    TIME_HOUR = 3600
    TIME_MINUTE = 60
    TIME_SECOND = 1

    last_synchronization = models.DateTimeField(default="1975-01-01T00:00:00Z", help_text="The last time this model was synchronized")
    next_synchronization = models.DateTimeField(null=True, help_text="The next synchronization event")
    delta_synchronization = models.IntegerField(default=TIME_DAY, help_text="The time, in seconds, between synchronizations")
    running = models.BooleanField(default=False, help_text="Whether the synchronization job is currently running")

    talentmap_model = models.TextField(unique=True, help_text="The talentmap model as a string; e.g. position.Position")

    @staticmethod
    def get_scheduled():
        '''
        Returns all SynchronizationJob who should be run (any job whose last sync + delta is in the past)
        '''
        return SynchronizationJob.objects.filter(next_synchronization__lte=datetime.datetime.utcnow(), running=False)

    def synchronize(self, soap_function="IPMSDataWebService", test=False):
        '''
        Runs the SynchronizationJob

        Args:
            soap_function (str) - The function to call on the SOAP client
            test (bool) - Indicates if we should use the testing method of the SOAP client
        '''
        start = datetime.datetime.utcnow()
        self.running = True
        self.save()
        try:
            logger = logging.getLogger('synchronization')
            logger.info(self)

            logger.info("Getting SOAP client")

            client = get_soap_client(soap_function=soap_function, test=test)

            logger.info(f"Using function {soap_function}")

            # This will search for any environment variables called DJANGO_SOAP_HEADER_xxxx, and parse it as a Header/Value pair
            soap_headers = {}
            env_soap_headers = [os.environ[key] for key in os.environ.keys() if key[:18] == "DJANGO_SOAP_HEADER"]
            for header in env_soap_headers:  # pragma: no cover
                split = header.split("=")
                soap_headers[split[0]] = split[1]
                logger.info(f"Setting SOAP header\t\t{split[0]}: {split[1]}")

            synchronization_tasks = get_synchronization_information(self.talentmap_model)
            for task in synchronization_tasks:
                logger.info(f"Running task {task.__name__}")
                soap_arguments, instance_tag, tag_map, collision_field, post_load_function, override_loading_method = task()
                model = apps.get_model(self.talentmap_model)

                logger.info("Intializing XML loader")

                loader = XMLloader(model, instance_tag, tag_map, 'update', collision_field, override_loading_method)

                logger.info("Loader initialized, pulling XML data")

                '''
                The XML data from DOS SOAP comes back in batches, we need to use the last 'collision_field'
                as the PaginationStartKey of the next request, and continue until we get no more results
                '''
                new_ids = []
                updated_ids = []
                last_collision_field = None
                soap_function_name = soap_function
                while True:
                    if last_collision_field:
                        # Set the pagination start key to our last collision field; which should be the remote data's primary key
                        soap_arguments['PaginationStartKey'] = last_collision_field
                        logger.info(f"Requesting page from primary key: {last_collision_field}")
                    else:
                        logger.info(f"Requesting first page")

                    # Get the data
                    response_xml = ET.tostring(getattr(client, soap_function_name)(**soap_arguments, _soapheaders=soap_headers), encoding="unicode")

                    newer_ids, updateder_ids, last_collision_field = loader.create_models_from_xml(response_xml, raw_string=True)

                    # If there are no new or updated ids on this page, we've reached the end
                    if len(newer_ids) == 0 and len(updateder_ids) == 0:
                        break

                    logger.info(f"Got: {len(newer_ids)} new, {len(updateder_ids)} updated this page")

                    # Append our newer and updated-er ids to our total list
                    new_ids = new_ids + newer_ids
                    updated_ids = updated_ids + updateder_ids

            logger.info("Data pull complete")

            # Run the post load function, if it exists
            if callable(post_load_function):
                logger.info(f"Calling post-load function for model {model}")
                post_load_function(model, new_ids, updated_ids)

            logger.info("Synchronization complete")
            d = relativedelta(start, datetime.datetime.utcnow())
            logger.info(f"Synchronization Report\n\tModel: {self.talentmap_model}\n\tNew: {len(new_ids)}\n\tUpdated: {len(updated_ids)}\n\tElapsed time: {d.days} d {d.minutes} min {d.seconds} s\t\t")

            # Successful, set the last synchronization
            self.last_synchronization = timezone.now()
        except:  # pragma: no cover
            raise
        finally:
            self.running = False
            self.save()

    def save(self, *args, **kwargs):
        self.next_synchronization = ensure_date(self.last_synchronization) + relativedelta(seconds=self.delta_synchronization)
        super(SynchronizationJob, self).save(*args, **kwargs)

    def __str__(self):
        d = relativedelta(seconds=self.delta_synchronization)
        status_string = f"Last@{self.last_synchronization} Next@+{self.next_synchronization} ∆[{d.years}y {d.months}mo {d.days}d {d.minutes}min {d.seconds}s]"
        if self.running:
            status_string = "IN PROGRESS"
        return f"SynchronizationJob - {self.talentmap_model}: {status_string}"

    class Meta:
        managed = True
        ordering = ["talentmap_model"]
