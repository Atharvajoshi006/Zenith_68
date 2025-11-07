from django.contrib import admin
from .models import StudentProfile, OTPCode


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'student_type', 'created_at', 'last_login_at')
    search_fields = ('user__username', 'user__email', 'phone', 'student_type')
    list_filter = ('student_type', 'created_at')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'last_login_at')


@admin.register(OTPCode)
class OTPCodeAdmin(admin.ModelAdmin):
    list_display = ('user', 'code', 'is_used', 'created_at')
    search_fields = ('user__username', 'code')
    list_filter = ('is_used', 'created_at')
    ordering = ('-created_at',)

from .models import Course, Topic, Lesson, Enrollment, LessonProgress

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at')
    search_fields = ('title',)

@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ('title', 'course')
    list_filter = ('course',)
    search_fields = ('title', 'course__title')

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'topic', 'order')
    list_filter = ('topic__course', 'topic')
    search_fields = ('title', 'topic__title', 'topic__course__title')
    ordering = ('topic', 'order')

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'created_at')
    list_filter = ('course',)

@admin.register(LessonProgress)
class LessonProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'lesson', 'completed', 'completed_at')
    list_filter = ('completed', 'lesson__topic__course')
    search_fields = ('user__username', 'lesson__title')
from .models import QuizQuestion, QuizChoice, QuizAttempt, AttemptAnswer

class QuizChoiceInline(admin.TabularInline):
    model = QuizChoice
    extra = 1

@admin.register(QuizQuestion)
class QuizQuestionAdmin(admin.ModelAdmin):
    list_display = ('topic', 'difficulty', 'short')
    list_filter = ('difficulty', 'topic__course', 'topic')
    search_fields = ('text',)
    inlines = [QuizChoiceInline]

    def short(self, obj):
        return (obj.text[:70] + '…') if len(obj.text) > 70 else obj.text

@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ('user', 'score', 'total', 'source', 'created_at')
    list_filter = ('source', 'created_at')

@admin.register(AttemptAnswer)
class AttemptAnswerAdmin(admin.ModelAdmin):
    list_display = ('attempt', 'question', 'correct')
    list_filter = ('correct',)
from .models import AssistantThread, AssistantMessage

class AssistantMessageInline(admin.TabularInline):
    model = AssistantMessage
    extra = 0
    readonly_fields = ('role', 'content', 'created_at')

@admin.register(AssistantThread)
class AssistantThreadAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    inlines = [AssistantMessageInline]
from .models import StudyPlan, StudyTask

class StudyTaskInline(admin.TabularInline):
    model = StudyTask
    extra = 0

@admin.register(StudyPlan)
class StudyPlanAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'is_active', 'exam_date', 'days', 'daily_minutes', 'created_at')
    list_filter = ('is_active', 'exam_date', 'created_at')
    inlines = [StudyTaskInline]

@admin.register(StudyTask)
class StudyTaskAdmin(admin.ModelAdmin):
    list_display = ('plan', 'date', 'topic', 'minutes', 'is_break', 'done')
    list_filter = ('date', 'is_break', 'done')
from .models import Exam, Subject, SubjectWeightage, Resource

class SubjectInline(admin.TabularInline):
    model = Subject
    extra = 0

@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ('name', 'grade', 'slug')
    prepopulated_fields = {"slug": ("name",)}
    inlines = [SubjectInline]
    search_fields = ('name', 'grade')

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'exam')
    list_filter = ('exam',)
    search_fields = ('name', 'exam__name')

@admin.register(SubjectWeightage)
class SubjectWeightageAdmin(admin.ModelAdmin):
    list_display = ('subject', 'weight_percent', 'year')
    list_filter = ('subject__exam', 'year')
    search_fields = ('subject__name',)

@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ('title', 'kind', 'subject', 'year', 'source')
    list_filter = ('kind', 'subject__exam', 'subject', 'year')
    search_fields = ('title', 'subject__name', 'source')

