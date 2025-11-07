# core/admin.py
from django.contrib import admin
from .models import (
    # Accounts / profile / otp
    StudentProfile, OTPCode,
    # Learning
    Course, Topic, Lesson, Enrollment, LessonProgress,
    # Quiz
    QuizQuestion, QuizChoice, QuizAttempt, AttemptAnswer,
    # Assistant
    AssistantThread, AssistantMessage,
    # Planner
    StudyPlan, StudyTask,
    # Study Hub
    Exam, Subject, SubjectWeightage, Resource,
)

# =========================
# Accounts / Profile / OTP
# =========================

@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "phone", "student_type", "created_at", "last_login_at")
    search_fields = ("user__username", "user__email", "phone", "student_type")
    list_filter = ("student_type", "created_at")
    ordering = ("-created_at",)
    readonly_fields = ("created_at", "last_login_at")


@admin.register(OTPCode)
class OTPCodeAdmin(admin.ModelAdmin):
    list_display = ("user", "code", "is_used", "created_at")
    search_fields = ("user__username", "user__email", "code")
    list_filter = ("is_used", "created_at")
    ordering = ("-created_at",)


# ===============
# Learning models
# ===============

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("title", "created_at")
    search_fields = ("title",)
    ordering = ("title",)
    date_hierarchy = "created_at"


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ("title", "course")
    list_filter = ("course",)
    search_fields = ("title", "course__title")
    ordering = ("course__title", "title")


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ("title", "topic", "order")
    list_filter = ("topic__course", "topic")
    search_fields = ("title", "topic__title", "topic__course__title")
    ordering = ("topic__course__title", "topic__title", "order")


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ("user", "course", "created_at")
    list_filter = ("course",)
    search_fields = ("user__username", "user__email", "course__title")
    date_hierarchy = "created_at"
    ordering = ("-created_at",)


@admin.register(LessonProgress)
class LessonProgressAdmin(admin.ModelAdmin):
    list_display = ("user", "lesson", "completed", "completed_at")
    list_filter = ("completed", "lesson__topic__course")
    search_fields = ("user__username", "user__email", "lesson__title", "lesson__topic__title")
    date_hierarchy = "completed_at"


# ===========
# Quiz models
# ===========

class QuizChoiceInline(admin.TabularInline):
    model = QuizChoice
    extra = 1


@admin.register(QuizQuestion)
class QuizQuestionAdmin(admin.ModelAdmin):
    list_display = ("topic", "difficulty", "short_text")
    list_filter = ("difficulty", "topic__course", "topic")
    search_fields = ("text", "topic__title", "topic__course__title")
    inlines = [QuizChoiceInline]
    ordering = ("topic__course__title", "topic__title", "id")

    @admin.display(description="Question")
    def short_text(self, obj):
        return (obj.text[:70] + "…") if len(obj.text) > 70 else obj.text


@admin.register(QuizChoice)
class QuizChoiceAdmin(admin.ModelAdmin):
    """
    Must exist (and include search_fields) so AttemptAnswerAdmin.autocomplete_fields
    can reference the QuizChoice model without admin.E039.
    """
    list_display = ("id", "question", "text", "is_correct")
    list_filter = ("is_correct", "question__topic", "question__topic__course")
    search_fields = (
        "text",
        "question__text",
        "question__topic__title",
        "question__topic__course__title",
    )
    autocomplete_fields = ("question",)
    ordering = ("question__topic__course__title", "question__topic__title", "id")


@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ("user", "score", "total", "source", "created_at")
    list_filter = ("source", "created_at")
    search_fields = ("user__username", "user__email", "source")
    date_hierarchy = "created_at"
    ordering = ("-created_at",)


@admin.register(AttemptAnswer)
class AttemptAnswerAdmin(admin.ModelAdmin):
    list_display = ("attempt", "question", "chosen_choice", "correct")
    list_filter = ("correct", "attempt__created_at", "question__topic", "question__topic__course")
    search_fields = (
        "attempt__user__username",
        "attempt__user__email",
        "question__text",
        "chosen_choice__text",
    )
    # Every FK here must point to a model with a registered ModelAdmin that has search_fields.
    autocomplete_fields = ("attempt", "question", "chosen_choice")
    ordering = ("-attempt__created_at",)


# =================
# Assistant (chat)
# =================

class AssistantMessageInline(admin.TabularInline):
    model = AssistantMessage
    extra = 0
    readonly_fields = ("role", "content", "created_at")
    can_delete = False


@admin.register(AssistantThread)
class AssistantThreadAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "is_active", "created_at")
    list_filter = ("is_active", "created_at")
    search_fields = ("user__username", "user__email")
    autocomplete_fields = ("user",)
    inlines = [AssistantMessageInline]
    date_hierarchy = "created_at"
    ordering = ("-created_at",)


@admin.register(AssistantMessage)
class AssistantMessageAdmin(admin.ModelAdmin):
    list_display = ("id", "thread", "role", "short_content", "created_at")
    list_filter = ("role", "created_at")
    search_fields = ("content", "thread__title", "thread__user__username", "thread__user__email")
    autocomplete_fields = ("thread",)
    date_hierarchy = "created_at"
    ordering = ("-created_at",)

    def short_content(self, obj):
        return (obj.content[:80] + "…") if len(obj.content) > 80 else obj.content


# ==================
# Study Planner data
# ==================

class StudyTaskInline(admin.TabularInline):
    model = StudyTask
    extra = 0


@admin.register(StudyPlan)
class StudyPlanAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "is_active", "exam_date", "days", "daily_minutes", "created_at")
    list_filter = ("is_active", "exam_date", "created_at")
    search_fields = ("title", "user__username", "user__email")
    autocomplete_fields = ("user",)
    inlines = [StudyTaskInline]
    date_hierarchy = "created_at"
    ordering = ("-created_at",)


@admin.register(StudyTask)
class StudyTaskAdmin(admin.ModelAdmin):
    list_display = ("plan", "date", "topic", "minutes", "is_break", "done")
    list_filter = ("date", "is_break", "done")
    search_fields = ("plan__title", "plan__user__username", "plan__user__email", "topic")
    autocomplete_fields = ("plan",)
    date_hierarchy = "date"
    ordering = ("date", "id")


# ==========================================
# Study Hub (Exams, Subjects, Weight, Links)
# ==========================================

class SubjectInline(admin.TabularInline):
    model = Subject
    extra = 0


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ("name", "grade", "slug")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [SubjectInline]
    search_fields = ("name", "grade")
    ordering = ("name",)


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ("name", "exam")
    list_filter = ("exam",)
    search_fields = ("name", "exam__name")
    ordering = ("exam__name", "name")


@admin.register(SubjectWeightage)
class SubjectWeightageAdmin(admin.ModelAdmin):
    list_display = ("subject", "weight_percent", "year")
    list_filter = ("subject__exam", "year")
    search_fields = ("subject__name", "subject__exam__name")
    autocomplete_fields = ("subject",)
    ordering = ("-year", "subject__name")


@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ("title", "kind", "subject", "year", "source")
    list_filter = ("kind", "subject__exam", "subject", "year")
    search_fields = ("title", "subject__name", "source")
    autocomplete_fields = ("subject",)
    ordering = ("kind", "-year", "title")
