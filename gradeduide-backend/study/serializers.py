from rest_framework import serializers
from .models import Grade, Subject, Topic, Resource, QuestionPaper

class ResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resource
        fields = '__all__'

class TopicSerializer(serializers.ModelSerializer):
    resources = ResourceSerializer(many=True, read_only=True)
    class Meta:
        model = Topic
        fields = '__all__'

class SubjectSerializer(serializers.ModelSerializer):
    topics = TopicSerializer(many=True, read_only=True)
    class Meta:
        model = Subject
        fields = '__all__'

class GradeSerializer(serializers.ModelSerializer):
    subjects = SubjectSerializer(many=True, read_only=True)
    class Meta:
        model = Grade
        fields = '__all__'

class QuestionPaperSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionPaper
        fields = '__all__'
