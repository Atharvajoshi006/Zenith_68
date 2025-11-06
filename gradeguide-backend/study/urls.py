# study/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    GradeViewSet,
    SubjectViewSet,
    TopicViewSet,
    ResourceViewSet,
    QuestionPaperViewSet,
    personalize_study_plan,
    login_view,
)

# Router for automatic CRUD routes
router = DefaultRouter()
router.register(r'grades', GradeViewSet, basename='grade')
router.register(r'subjects', SubjectViewSet, basename='subject')
router.register(r'topics', TopicViewSet, basename='topic')
router.register(r'resources', ResourceViewSet, basename='resource')
router.register(r'papers', QuestionPaperViewSet, basename='paper')

# Final URL patterns combining router routes and custom endpoints
urlpatterns = [
    path('', include(router.urls)),                         # Auto routes: /api/grades/, /api/subjects/, etc.
    path('personalize/', personalize_study_plan, name='personalize-study-plan'),  # POST endpoint
    path('login/', login_view, name='login'),               # POST endpoint for login
]
