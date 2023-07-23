from rest_framework.response import Response
from rest_framework import status, exceptions

from main.Serializers.SoundSerializer import SoundSerializerForSearchView
from main.models import *


def get_freesound_sounds(request, page = 1, query = ''):

    try:
        is_background = int(request.query_params['is-background'])
    except:
        return Response({'message': 'argument missing'}, status=status.HTTP_400_BAD_REQUEST)


    sounds = []
    processed_sounds = []

    if is_background:
        sounds = freesound_search_background_sound(query, page)
    else:
        sounds = freesound_search_event_sound(query, page)

    for sound in sounds:
        new_sound = Sound.objects.create_from_freesound(sound, is_background, loopable=is_background)
        serialized_sound = SoundSerializerForSearchView(new_sound).data
        processed_sounds.append(serialized_sound)

    return Response({'results':processed_sounds}, status=status.HTTP_200_OK)




