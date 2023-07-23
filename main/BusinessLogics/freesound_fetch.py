from main.models import *

from mockingJae_back.settings import freesound_client

def freesound_search_background_sound(query, page=1):
    """
    Returns a list of sound objects from freesound.org
    :param query: search query
    :return: list of sound objects
    """

    search_result_page = freesound_client.text_search(
        query="", 
        fields='id,username,duration,images,previews,name,tags', 
        filter='duration:[1 TO *],ac_loop:True', 
        sort='downloads_desc', 
        page=page)

    results = search_result_page.results

    return results


def freesound_search_event_sound(query, page=1):
    """
    Returns a list of sound objects from freesound.org
    :param query: search query
    :return: list of sound objects
    """

    search_result_page = freesound_client.text_search(
        query="", 
        fields='id,username,duration,images,previews,name,tags', 
        filter='duration:[0 TO 1],ac_loop:False', 
        sort='downloads_desc', 
        page=page)

    results = search_result_page.results

    return results


def freesound_get_user(username):
    """
    Returns a user object from freesound.org
    :param username: username of the user
    :return: user object
    """
    return freesound_client.get_user(username)





