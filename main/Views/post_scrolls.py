from django.utils import timezone

from rest_framework.response import Response
from rest_framework import status, exceptions

from main.models import Scrolls, User
from main.serializer import *


def upload_scrolls_from_images():
    pass