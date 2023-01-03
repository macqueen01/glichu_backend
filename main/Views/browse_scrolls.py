from django.utils import timezone

from rest_framework.response import Response
from rest_framework import status, exceptions

from main.models import Scrolls, User, Recommendation
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



