from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.core.management import call_command
from talentmap_api.integrations.models import SynchronizationJob

import logging
logger = logging.getLogger(__name__)


class DataSyncListView(APIView):

    permission_classes = (IsAuthenticatedOrReadOnly,)

    @classmethod
    def get_extra_actions(cls):
        return []

    def get(self, request, format=None, **url_arguments):
        '''
        Lists the data synchronization jobs available

        Returns list of data sync jobs, otherwise, 404
        '''
        job_list = SynchronizationJob.objects.all()
        str_jobs = []
        for job in job_list:
            j = {}
            j['id'] = job.id
            j['last_sync'] = job.last_synchronization
            j['delta_sync'] = job.delta_synchronization
            j['running'] = job.running
            j['talentmap_model'] = job.talentmap_model
            j['next_sync'] = job.next_synchronization
            j['priority'] = job.priority
            j['use_last_date_updated'] = job.use_last_date_updated
            str_jobs.append(j)

        count = job_list.count()
        resp = {
            "count": count,
            "data": str_jobs
        }

        return Response(data=resp)


class DataSyncActionView(APIView):

    permission_classes = (IsAuthenticatedOrReadOnly,)

    @classmethod
    def get_extra_actions(cls):
        return []

    # def get(self, request, format=None, **url_arguments):
    #     '''
    #     Indicates if the position is in the specified bid cycle

    #     Returns 204 if the position is in the cycle, otherwise, 404
    #     '''
    #     if get_object_or_404(BidCycle, id=url_arguments.get("pk")).positions.filter(id=url_arguments.get("pos_id")).count() > 0:
    #         return Response(status=status.HTTP_204_NO_CONTENT)
    #     else:
    #         return Response(status=status.HTTP_404_NOT_FOUND)

    def put(self, request, format=None, **url_arguments):
        '''
        Executes a data sync if the job is present, otherwise, 404
        '''
        sync_job = get_object_or_404(SynchronizationJob, id=url_arguments.get("pk"))
        tm_model = ""
        if sync_job:
            tm_model = sync_job.talentmap_model
        logger.info(f"User {self.request.user.id}:{self.request.user} running data sync for {tm_model}")
        call_command('synchronize_data', '--model', tm_model, '--test')
        # in_group_or_403(self.request.user, 'bidcycle_admin')
        # pid = url_arguments.get("pos_id")
        # bidcycle = get_object_or_404(BidCycle, id=url_arguments.get("pk"))
        # logger.info(f"User {self.request.user.id}:{self.request.user} adding position id {pid} to bidcycle {bidcycle}")
        # bidcycle.positions.add(get_object_or_404(Position, id=pid))

        return Response(data=tm_model)

    # def delete(self, request, format=None, **url_arguments):
    #     '''
    #     Removes the position from the bid cycle
    #     '''
    #     in_group_or_403(self.request.user, 'bidcycle_admin')
    #     bidcycle = get_object_or_404(BidCycle, id=url_arguments.get("pk"))
    #     position = get_object_or_404(bidcycle.positions.all(), id=url_arguments.get("pos_id"))
    #     logger.info(f"User {self.request.user.id}:{self.request.user} removing position id {position.id} from bidcycle {bidcycle}")
    #     bidcycle.positions.remove(position)
    #     return Response(status=status.HTTP_204_NO_CONTENT)