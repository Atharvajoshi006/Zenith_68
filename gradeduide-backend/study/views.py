from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Grade, Subject, Topic, QuestionPaper
from .serializers import GradeSerializer, SubjectSerializer, TopicSerializer, QuestionPaperSerializer
import random

class GradeViewSet(viewsets.ModelViewSet):
    queryset = Grade.objects.all()
    serializer_class = GradeSerializer

class SubjectViewSet(viewsets.ModelViewSet):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer

class TopicViewSet(viewsets.ModelViewSet):
    queryset = Topic.objects.all()
    serializer_class = TopicSerializer

class QuestionPaperViewSet(viewsets.ModelViewSet):
    queryset = QuestionPaper.objects.all()
    serializer_class = QuestionPaperSerializer

@api_view(['POST'])
def personalize_study_plan(request):
    subject_id = request.data.get('subjectId')
    weak_topics = request.data.get('weakTopics', [])
    hours = request.data.get('hoursAvailable', 5)

    topics = Topic.objects.filter(subject_id=subject_id)
    if not topics:
        return Response({'message': 'No topics found'}, status=404)

    total_weight = sum(t.weight for t in topics)
    plan = []

    for topic in topics:
        topic_hours = (topic.weight / total_weight) * hours
        if str(topic.id) in weak_topics:
            topic_hours *= 1.5
        plan.append({
            'topic': topic.title,
            'hours': round(topic_hours, 2),
            'reason': 'High weight or weak area' if topic_hours > 1 else 'Low priority'
        })

    random.shuffle(plan)
    return Response({'plan': plan})
