from .mock_framework import H1StepWithWebUI
from django.urls import path, include
from django.contrib.auth.models import User
from rest_framework import routers, serializers, viewsets
from django.shortcuts import render
from django.http import HttpResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response


class Api(H1StepWithWebUI):
    @api_view(['GET', 'POST'])
    def get_response(self, req, isPost):
        return "<br/><br/><center><H1>Hello Human-First AI World!</H1></center>"
#        if not isPost:
#            data = [ 1, 2, 3, 4, 5 ]
#            serializer = serializers.ModelSerializer(None, data)
#            return serializer.data
#        return "<br/><br/><center><H1>Hello Human-First AI World!</H1></center>"