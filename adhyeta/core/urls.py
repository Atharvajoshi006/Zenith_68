from django.urls import path
from . import views

urlpatterns = [
    # Frontend
    path('', views.index, name='index'),

    # Authentication APIs
    path('api/signup', views.api_signup, name='api_signup'),
    path('api/login', views.api_login, name='api_login'),
    path('api/logout', views.api_logout, name='api_logout'),
    path('api/me', views.api_me, name='api_me'),

    # Password Reset (OTP-based)
    path('api/forgot-password', views.api_forgot_password, name='api_forgot_password'),
    path('api/verify-otp', views.api_verify_otp, name='api_verify_otp'),
    path('api/reset-password', views.api_reset_password, name='api_reset_password'),
    ]    # Learning APIs
urlpatterns += [
    path('api/courses', views.api_courses, name='api_courses'),
    path('api/topics', views.api_topics, name='api_topics'),            # ?course_id=ID
    path('api/lessons', views.api_lessons, name='api_lessons'),         # ?topic_id=ID
    path('api/mark-lesson', views.api_mark_lesson, name='api_mark_lesson'),
    path('api/my-progress', views.api_my_progress, name='api_my_progress'),
    path('api/seed-demo', views.api_seed_demo, name='api_seed_demo'),   # demo data creator


]
# Weekly progress API
urlpatterns += [
    path('api/progress-weekly', views.api_progress_weekly, name='api_progress_weekly'),
]
# Quiz APIs
urlpatterns += [
    path('api/quiz/generate', views.api_quiz_generate, name='api_quiz_generate'),
    path('api/quiz/submit', views.api_quiz_submit, name='api_quiz_submit'),
    path('api/quiz/history', views.api_quiz_history, name='api_quiz_history'),
    path('api/quiz/seed', views.api_quiz_seed, name='api_quiz_seed'),  # demo seed
]
# AI Assistant APIs
urlpatterns += [
    path('api/ai/start', views.api_ai_start, name='api_ai_start'),
    path('api/ai/message', views.api_ai_message, name='api_ai_message'),
]
urlpatterns += [
    path("api/login", views.api_login, name="api_login"),
]
