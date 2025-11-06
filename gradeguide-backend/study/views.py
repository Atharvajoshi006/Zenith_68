# study/views.py

from django.contrib.auth import authenticate, login
from django.views.decorators.csrf import csrf_exempt

from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Grade, Subject, Topic, Resource, QuestionPaper
from .serializers import (
    GradeSerializer, SubjectSerializer, TopicSerializer,
    ResourceSerializer, QuestionPaperSerializer
)


class GradeViewSet(viewsets.ModelViewSet):
    queryset = Grade.objects.all()
    serializer_class = GradeSerializer


class SubjectViewSet(viewsets.ModelViewSet):
    serializer_class = SubjectSerializer

    def get_queryset(self):
        qs = Subject.objects.all()
        grade_id = self.request.query_params.get('grade')
        if grade_id:
            qs = qs.filter(grade_id=grade_id)
        return qs


class TopicViewSet(viewsets.ModelViewSet):
    serializer_class = TopicSerializer

    def get_queryset(self):
        qs = Topic.objects.all()
        subject_id = self.request.query_params.get('subject')
        if subject_id:
            qs = qs.filter(subject_id=subject_id)
        return qs


class ResourceViewSet(viewsets.ModelViewSet):
    serializer_class = ResourceSerializer

    def get_queryset(self):
        qs = Resource.objects.all()
        topic_id = self.request.query_params.get('topic')
        if topic_id:
            qs = qs.filter(topic_id=topic_id)
        return qs


class QuestionPaperViewSet(viewsets.ModelViewSet):
    serializer_class = QuestionPaperSerializer

    def get_queryset(self):
        qs = QuestionPaper.objects.all()
        subject_id = self.request.query_params.get('subject')
        if subject_id:
            qs = qs.filter(subject_id=subject_id)
        return qs


@csrf_exempt  # dev convenience so fetch() POST works without CSRF token
@api_view(['POST'])
def personalize_study_plan(request):
    """
    Request JSON:
    {
      "subject_id": 3,
      "hours": 12,
      "weak_topics": [5, 7]
    }
    """
    try:
        hours = float(request.data.get('hours', 10))
    except Exception:
        return Response({'detail': 'hours must be a number'}, status=400)

    subject_id = request.data.get('subject_id')
    if not subject_id:
        return Response({'detail': 'subject_id is required'}, status=400)

    weak_topics = set(map(str, request.data.get('weak_topics', [])))

    topics = Topic.objects.filter(subject_id=subject_id)
    total_weight = sum((t.weight or 1) for t in topics) or 1

    plan = []
    for t in topics:
        topic_hours = (float(t.weight or 1) / total_weight) * hours
        if str(t.id) in weak_topics:
            topic_hours *= 1.5
        plan.append({
            'topic': t.title,
            'hours': round(topic_hours, 2),
            'reason': 'High weight or weak area' if str(t.id) in weak_topics else 'Proportional weight'
        })

    # simple shuffle so the list looks less monotonous
    import random
    random.shuffle(plan)
    return Response({'plan': plan})


@csrf_exempt  # dev convenience so fetch() POST works without CSRF token
@api_view(['POST'])
def login_view(request):
    """
    Demo session login. Use with fetch(..., credentials: 'include') on the frontend.
    Request JSON: { "username": "user", "password": "pass" }
    """
    username = request.data.get('username', '')
    password = request.data.get('password', '')

    user = authenticate(request, username=username, password=password)
    if user:
        login(request, user)
        return Response({'ok': True, 'user': username})

    return Response(
        {'ok': False, 'detail': 'Invalid credentials'},
        status=status.HTTP_400_BAD_REQUEST
    )
