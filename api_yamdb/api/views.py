from django.shortcuts import get_object_or_404
from rest_framework import viewsets, permissions

from permissions import IsOwnerOrReadOnly
from reviews.models import Review
from api.serializers import ReviewSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def get_title(self):
        return get_object_or_404(Review, pk=self.kwargs['title_id'])

    def get_queryset(self):
        return self.get_title().reviews.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, title=self.get_title())
