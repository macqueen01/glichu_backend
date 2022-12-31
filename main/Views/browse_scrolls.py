from django.utils import timezone

from rest_framework.response import Response
from rest_framework import status, exceptions

from main.models import Scrolls, User
from main.serializer import *


def scrolls_with_given_id(request, id):

    try:
        if request.method == 'GET':
            scrolls = Scrolls.objects.filter(id__exact=id)
            assert (scrolls.exists() == True)

            serializer = ScrollsSerializer
            result = serializer(scrolls.get())
            return Response(result.data, status=status.HTTP_200_OK)
        return Response({'message': 'wrong method call'},
                        status=status.HTTP_405_METHOD_NOT_ALLOWED)
    except:
        return Response({'message': f'scrolls with id {id} does not exist'},
                        status=status.HTTP_404_NOT_FOUND)


def scrolls_with_given_tag(request, tag_id):

    try:
        if request.method != 'GET':
            return Response({'message': 'wrong method call'},
                            status=status.HTTP_405_METHOD_NOT_ALLOWED)

        if (scrolls := Tag.objects.get_scrolls(tag_id)):
            serializer = ScrollsSerializer
            result = serializer(scrolls, many=True)
            return Response(result.data, status=status.HTTP_200_OK)

        raise exceptions.NotFound(
            detail=f'scrolls with given tag no.{tag_id} not found', code='not_found')
    except:
        return Response({'message': f'scrolls with given tag no.{tag_id} not found'},
                        status=status.HTTP_404_NOT_FOUND)
