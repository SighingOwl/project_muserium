from rest_framework import serializers
from .models import DetailInfo, Review, Question, Answer, Comment

class DetailInfoSerializer(serializers.ModelSerializer):
    # Detail info serializer

    class Meta:
        model = DetailInfo
        fields = '__all__'

class ReviewSerializer(serializers.ModelSerializer):
    # Review serializer

    class Meta:
        model = Review
        fields = '__all__'

class QuestionSerializer(serializers.ModelSerializer):
    # Question serializer

    class Meta:
        model = Question
        fields = '__all__'

class QuestionListSerializer(serializers.ModelSerializer):
    # Question list serializer

    class Meta:
        model = Question
        fields = ['id', 'title', 'author', 'created_at', 'view_count', 'answered_at', 'is_secret']

class AnswerSerializer(serializers.ModelSerializer):
    # Answer serializer

    class Meta:
        model = Answer
        fields = '__all__'

class CommentSerializer(serializers.ModelSerializer):
    # Comment serializer

    class Meta:
        model = Comment
        fields = '__all__'