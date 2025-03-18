from rest_framework import serializers

from reviews.models import Review, User


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Review
        fields = ('id', 'title', 'text', 'author', 'score', 'pub_date')
        read_only_fields = ('title',)


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('__all__')
