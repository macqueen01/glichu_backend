from django.utils import timezone

from rest_framework.response import Response
from rest_framework import status, exceptions
from rest_framework.pagination import PageNumberPagination
from main.BusinessLogics.recommendation_fetch import scrolls_recommendation_list_api_fetch
from main.Views.authentications import authenticate_then_user_or_unauthorized_error

from main.models import Scrolls, User, Recommendation
from main.serializer import *


def get_personalized_scrolls_feed(request):
    user = authenticate_then_user_or_unauthorized_error(request)
    page = 1

    if user is None:
        return Response({'message': 'user is invalid'}, status=status.HTTP_400_BAD_REQUEST)
    
    try: 
        page = request.data['page']
    except:
        page = 1

    # recommendation_list = scrolls_recommendation_list_api_fetch(user.id, page)

    if (request.method == 'GET'):

        # scrolls = Scrolls.objects.filter(id__in=recommendation_list).order_by('-created_at')

        followers = user.followers.all()
        followings = user.followings.all()

        follow_and_following_creator_list = [
            recommended_user.id for recommended_user in followers.union(followings)
        ]

        # This recommends user the scrolls of following's following

        followings_followers_creator_list = []
        followings_followings_creator_list = []

        for following in followings:
            for followings_following in following.followings.all():
                followings_followers_creator_list.append(followings_following.id)

        for recommended_user in followings_followers_creator_list:
            if recommended_user not in follow_and_following_creator_list:
                follow_and_following_creator_list.append(recommended_user)

        # append user himself
        follow_and_following_creator_list.append(user.id)

        # get reported scrolls by user
        reported_scrolls_list = [scrolls.id for scrolls in user.reported_scrolls.all()]


        scrolls = Scrolls.objects.filter(created_by__pk__in=follow_and_following_creator_list).exclude(id__in = reported_scrolls_list).order_by('-created_at')

        serializer = ScrollsSerializerGeneralUse

        paginator = PageNumberPagination()
        paginator.page_size = 10
        result_page = paginator.paginate_queryset(scrolls, request)
        serializer = serializer(result_page, many=True, context={'user': user})
        return paginator.get_paginated_response(serializer.data)
    
    return Response({'message': "wrong method call"}, 
        status = status.HTTP_405_METHOD_NOT_ALLOWED)



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

def get_all_scrolls(request):
    # returns all scrolls in the database 
    # this should be used only under debug flag

    if request.method != 'GET':
        return Response({'message': 'wrong method call'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED)
        
    scrolls = Scrolls.objects.all()
    serializer = ScrollsSerializer
    result = serializer(scrolls, many=True)
    return Response(result.data, status=status.HTTP_200_OK)

def get_random_scrolls(request):
    
    # returns one random scrolls from the database

    if request.method != 'GET':
        return Response({'message': 'wrong method call'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED)
    
    scrolls = Scrolls.objects.get_random_scrolls()

    if not scrolls:
        return Response({'message': 'no scrolls found', 'scrolls': '[]'},
            status=status.HTTP_200_OK)

    serializer = ScrollsSerializerGeneralUse
    result = serializer(scrolls)
    
    return Response(result.data, status=status.HTTP_200_OK)

def get_saved_scrolls_of_user(request, user_id):
    if (request.method != 'GET'):
        return Response({'message': 'wrong method call'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED)
    
    try:
        user = User.objects.get(id=user_id)

        
        if not user:
            return Response({'message': 'user not found'}, status=status.HTTP_404_NOT_FOUND)
        
        scrolls = Scrolls.objects.filter(saved_by = user.id).order_by('-created_at')
        paginator = PageNumberPagination()
        paginator.page_size = 1000
        result_page = paginator.paginate_queryset(scrolls, request)
        serializer = ScrollsSerializerGeneralUse(result_page, many=True, context={'user': user})
        return paginator.get_paginated_response(serializer.data)
    except:
        return Response({'message': 'argument missing'}, status=status.HTTP_400_BAD_REQUEST)


def get_scrolls_by_user(request, user_id):
    self = authenticate_then_user_or_unauthorized_error(request)

    if self is None:
        return Response({'message': 'user is invalid'}, status=status.HTTP_400_BAD_REQUEST)

    if (request.method != 'GET'):
        return Response({'message': 'wrong method call'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED)
    
    try:
        user = User.objects.get(id=user_id)

        
        if not user:
            return Response({'message': 'user not found'}, status=status.HTTP_404_NOT_FOUND)
        
        scrolls = Scrolls.objects.get_scrolls_by_user(user.id).order_by('-created_at')
        paginator = PageNumberPagination()
        paginator.page_size = 1000
        result_page = paginator.paginate_queryset(scrolls, request)
        serializer = ScrollsSerializerGeneralUse(result_page, many=True, context={'user': self})
        return paginator.get_paginated_response(serializer.data)
    except:
        return Response({'message': 'argument missing'}, status=status.HTTP_400_BAD_REQUEST)



# provides a functional view that returns two serialized scrolls for given page number
"""
def scrolls_with_given_page(request, page_number):

    try:
        if request.method != 'GET':
            return Response({'message': 'wrong method call'},
                            status=status.HTTP_405_METHOD_NOT_ALLOWED)

        if (scrolls := Scrolls.objects.get_scrolls(page_number)):
            serializer = ScrollsSerializer
            result = serializer(scrolls, many=True)
            return Response(result.data, status=status.HTTP_200_OK)

        raise exceptions.NotFound(
            detail=f'scrolls with given page no.{page_number} not found', code='not_found')
    except:
        return Response({'message': f'scrolls with given page no.{page_number} not found'},
                        status=status.HTTP_404_NOT_FOUND)
"""

# scrolls recommendation algorithm
def scrolls_from_recommendation(request):
    pass

def recommend(request):
    user = request.user
    recommendations = Recommendation.objects.filter(user=user).order_by('-score')
    recommended_posts = [recommendation.post for recommendation in recommendations]
    pass

def like_post(request):
    user = request.user
    post_id = request.POST['post_id']
    post = Scrolls.objects.get(id=post_id)
    UserInteraction.objects.create(user=user, post=post, interaction_type='like')
    pass

#@background(schedule=60*60*24)  # Run every day
def update_recommendations():
    # Get all users
    users = User.objects.all()

    # For each user, calculate recommendations
    for user in users:
        # Get user interactions
        interactions = UserInteraction.objects.filter(user=user)

        # Calculate recommendation scores for each post
        recommendation_scores = {}
        for interaction in interactions:
            post = interaction.post
            if post not in recommendation_scores:
                recommendation_scores[post] = 0
            if interaction.interaction_type == 'like':
                recommendation_scores[post] += 1
            elif interaction.interaction_type == 'dislike':
                recommendation_scores[post] -= 1

        # Create or update recommendations for the user
        for post, score in recommendation_scores.items():
            recommendation, created = Recommendation.objects.get_or_create(
                user=user, post=post)
            recommendation.score = score
            recommendation.save()



