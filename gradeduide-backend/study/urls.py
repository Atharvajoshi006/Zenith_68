from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import GradeViewSet, SubjectViewSet, TopicViewSet, QuestionPaperViewSet, personalize_study_plan

router = DefaultRouter()
router.register(r'grades', GradeViewSet)
router.register(r'subjects', SubjectViewSet)
router.register(r'topics', TopicViewSet)
router.register(r'papers', QuestionPaperViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('personalize/', personalize_study_plan),
]
