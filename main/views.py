from rest_framework.decorators import api_view, renderer_classes
from rest_framework.renderers import JSONRenderer, TemplateHTMLRenderer

from main.Views import browse_scrolls, post_scrolls

@api_view(['GET'])
def scrolls_browse(request):
    scrolls_id = request.query_params['id']
    return browse_scrolls.scrolls_with_given_id(request, scrolls_id)

@api_view(['POST'])
def video_upload(request):
    return post_scrolls.upload_video(request)

@api_view(['POST'])
def scrollify_video(request):
    return post_scrolls.scrollify_video(request)

@api_view(['POST'])
def scrolls_upload(request):
    return post_scrolls.upload_scrolls(request)

    

