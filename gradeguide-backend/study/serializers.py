from rest_framework import serializers
from .models import Grade, Subject, Topic, Resource, QuestionPaper


class GradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Grade
        fields = ['id', 'name']


class SubjectSerializer(serializers.ModelSerializer):
    # Nested grade info (read-only)
    grade = GradeSerializer(read_only=True)
    # Allows sending grade_id when creating/updating subjects
    grade_id = serializers.PrimaryKeyRelatedField(
        source='grade', queryset=Grade.objects.all(), write_only=True
    )

    class Meta:
        model = Subject
        fields = ['id', 'name', 'grade', 'grade_id']


class TopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topic
        fields = ['id', 'title', 'weight', 'subject']


class ResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resource
        fields = ['id', 'title', 'type', 'url', 'topic']


class QuestionPaperSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionPaper
        fields = ['id', 'year', 'pdf_url', 'solution_url', 'subject']
