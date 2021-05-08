from django.http.response import HttpResponse
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .mock_framework import H1StepWithRestUI


class Api(H1StepWithRestUI):
    @staticmethod
    @api_view(['GET','POST'])
    def users(req):
        return Response([1, 2, 3, 4, 5])