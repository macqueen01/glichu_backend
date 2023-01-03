from .UserModel import User
from .ScrollsModel import Scrolls, Tag

from django.db import models

# We replace Scrolls to 'post' and Tag to 'hashtag' in the models to avoid some confusions.
# We would like to treat post as a scroll.

class UserInteractionManager(models.Manager):
    def likes(self):
        return self.filter(interaction_type=self.model.LIKE)

    def dislikes(self):
        return self.filter(interaction_type=self.model.DISLIKE)

    def ratings(self):
        return self.exclude(interaction_type=self.model.NEUTRAL)

class UserInteraction(models.Model):
    LIKE = 'L'
    DISLIKE = 'D'
    NEUTRAL = 'N'
    INTERACTION_TYPE_CHOICES = [
        (LIKE, 'Like'),
        (DISLIKE, 'Dislike'),
        (NEUTRAL, 'Neutral'),
    ]
    interaction_type = models.CharField(max_length=1, choices=INTERACTION_TYPE_CHOICES)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    scrolls = models.ForeignKey(Scrolls, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserInteractionManager()


class TagInteractionManager(models.Manager):
    def likes(self):
        return self.filter(interaction_type=self.model.LIKE)

    def dislikes(self):
        return self.filter(interaction_type=self.model.DISLIKE)

    def ratings(self):
        return self.exclude(interaction_type=self.model.NEUTRAL)

class TagInteraction(models.Model):
    LIKE = 'L'
    DISLIKE = 'D'
    NEUTRAL = 'N'
    INTERACTION_TYPE_CHOICES = [
        (LIKE, 'Like'),
        (DISLIKE, 'Dislike'),
        (NEUTRAL, 'Neutral'),
    ]
    interaction_type = models.CharField(max_length=1, choices=INTERACTION_TYPE_CHOICES)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = TagInteractionManager()


class RecommendationManager(models.Manager):
    def create_recommendation(self, user, scrolls, tag, score):
        recommendation = self.create(
            user=user, scrolls=scrolls, tag=tag, score=score)
        return recommendation

    def update_recommendations(user):
        # Generate recommendations
        recommendations = generate_recommendations(user)

        # Create or update Recommendation objects
        for recommendation in recommendations:
            recommendation, created = Recommendation.objects.get_or_create(
                user=user, scrolls=recommendation.scrolls)
            recommendation.score = recommendation.score
            recommendation.save()


class Recommendation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    scrolls = models.ForeignKey(Scrolls, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE, null=True)
    score = models.FloatField()

    objects = RecommendationManager()

def pearson_correlation_tags(user1, user2):
    # Get user interactions
    interactions1 = TagInteraction.objects.filter(user=user1)
    interactions2 = TagInteraction.objects.filter(user=user2)

    # Calculate common interactions
    hashtag_ids1 = {interaction.tag.id for interaction in interactions1}
    hashtag_ids2 = {interaction.tag.id for interaction in interactions2}
    common_hashtag_ids = hashtag_ids1 & hashtag_ids2
    common_interactions1 = [i for i in interactions1 if i.tag.id in common_hashtag_ids]
    common_interactions2 = [i for i in interactions2 if i.tag.id in common_hashtag_ids]
    n = len(common_hashtag_ids)

    # Return 0 if there are no common interactions
    if n == 0:
        return 0

    # Calculate the sum of the ratings for the common interactions
    sum1_likes = sum(
        1 for interaction in common_interactions1 if interaction.interaction_type == TagInteraction.LIKE)
    sum1_dislikes = sum(
        1 for interaction in common_interactions1 if interaction.interaction_type == TagInteraction.DISLIKE)
    sum2_likes = sum(
        1 for interaction in common_interactions2 if interaction.interaction_type == TagInteraction.LIKE)
    sum2_dislikes = sum(
        1 for interaction in common_interactions2 if interaction.interaction_type == TagInteraction.DISLIKE)

    # Calculate the Pearson correlation coefficient
    numerator = sum1_likes * sum2_likes + sum1_dislikes * sum2_dislikes
    denominator = (sum1_likes + sum1_dislikes) * (sum2_likes + sum2_dislikes)
    if denominator == 0:
        return 0
    else:
        return numerator / denominator


def pearson_correlation(user1, user2):
    # Get user interactions
    interactions1 = UserInteraction.objects.filter(user=user1)
    interactions2 = UserInteraction.objects.filter(user=user2)

    # Map interactions to post IDs
    post_ids1 = set(interaction.scrolls.id for interaction in interactions1)
    post_ids2 = set(interaction.scrolls.id for interaction in interactions2)

    # Calculate intersection of post IDs
    common_post_ids = post_ids1 & post_ids2
    common_interactions1 = [
        i for i in interactions1 if i.scrolls.id in common_post_ids]
    common_interactions2 = [
        i for i in interactions2 if i.scrolls.id in common_post_ids]
    n = len(common_post_ids)

    # Return 0 if there are no common interactions
    if n == 0:
        return 0

    # Calculate the sum of the ratings for the common interactions
    # Calculate sum of likes and dislikes for common interactions
    sum1_likes = sum(
        1 for interaction in common_interactions1 if interaction.interaction_type == UserInteraction.LIKE)
    sum1_dislikes = sum(
        1 for interaction in common_interactions1 if interaction.interaction_type == UserInteraction.DISLIKE)
    sum2_likes = sum(
        1 for interaction in common_interactions2 if interaction.interaction_type == UserInteraction.LIKE)
    sum2_dislikes = sum(
        1 for interaction in common_interactions2 if interaction.interaction_type == UserInteraction.DISLIKE)

    # Calculate the Pearson correlation coefficient
    numerator = sum1_likes * sum2_likes + sum1_dislikes * sum2_dislikes
    denominator = (sum1_likes + sum1_dislikes) * (sum2_likes + sum2_dislikes)
    if denominator == 0:
        return 0
    else:
        return numerator / denominator


def generate_recommendations(user, num_recommendations=10):
    # Calculate Pearson correlation coefficient between user and all other users
    user_interactions = UserInteraction.objects.filter(user=user).exclude(interaction_type=UserInteraction.NEUTRAL)
    user_interactions_other_users = user_interactions.exclude(user=user)
    user_correlations = {
        interaction.user: pearson_correlation(user_interactions, interaction.user.userinteraction_set.all())
        for interaction in user_interactions_other_users
    }
    top_correlated_users = sorted(user_correlations, key=user_correlations.get, reverse=True)[:num_recommendations]

    # Calculate Pearson correlation coefficient between user and all tags
    user_tag_interactions = TagInteraction.objects.filter(user=user).exclude(interaction_type=TagInteraction.NEUTRAL)
    user_tag_interactions_other_tags = user_tag_interactions.exclude(tag__in=user_tag_interactions)
    tag_correlations = {
        interaction.tag: pearson_correlation_tags(user_tag_interactions, interaction.tag.taginteraction_set.all())
        for interaction in user_tag_interactions_other_tags
    }
    top_correlated_tags = sorted(tag_correlations, key=tag_correlations.get, reverse=True)[:num_recommendations]

    # Get recommended scrolls from top correlated users and tags
    recommended_scrolls = Scrolls.objects.filter(author__in=top_correlated_users).prefetch_related('created_by')
    recommended_scrolls = recommended_scrolls.filter(tags__in=top_correlated_tags).prefetch_related('tags')

    # Exclude scrolls that the user has already interacted with
    recommended_scrolls = recommended_scrolls.exclude(userinteraction__user=user)

    # Return top N recommended scrolls
    return recommended_scrolls[:num_recommendations]