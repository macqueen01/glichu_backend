import os
import requests


def scrolls_recommendation_list_api_fetch(user_id, page):

    # fetches scrolls id list from recommendation server
    # feeds user id and page num to retrieve scrolls id list

    recommendation_url = os.environ.get('RECOMMENDATION_SERVER_URL')
    query_url = f'{recommendation_url}/{user_id}?pageno={page}'

    response = requests.get(query_url)
    scrolls_id_list = list(response.json().get('rec_list'))

    return scrolls_id_list




