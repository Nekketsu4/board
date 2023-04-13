from rest_framework import serializers

from main.models import Bboard, Comment


class BboardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bboard
        fields = ('id', 'title', 'content', 'price', 'created_at')


class BboardsDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bboard
        fields = ('id', 'title', 'content', 'price', 'created_at',
                  'contacts', 'image')


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ('bboard', 'author', 'content', 'created_at')
