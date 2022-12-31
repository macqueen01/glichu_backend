from rest_framework.decorators import api_view

from main.Views import browse_scrolls

@api_view(['GET'])
def scrolls_browse(request):
    scrolls_id = request.query_params['id']
    return browse_scrolls.scrolls_with_given_id(request, scrolls_id)
    
