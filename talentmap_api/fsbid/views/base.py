from rest_framework.views import APIView


class BaseView(APIView):
    @classmethod
    def get_extra_actions(cls):
        return []
