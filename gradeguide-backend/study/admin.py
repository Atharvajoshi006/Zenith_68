from django.contrib import admin
from .models import Grade, Subject, Topic, Resource, QuestionPaper


class SubjectInline(admin.TabularInline):
    model = Subject
    extra = 0


class TopicInline(admin.TabularInline):
    model = Topic
    extra = 0


class ResourceInline(admin.TabularInline):
    model = Resource
    extra = 0


class QuestionPaperInline(admin.TabularInline):
    model = QuestionPaper
    extra = 0


@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)
    inlines = [SubjectInline]


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "grade")
    list_filter = ("grade",)
    search_fields = ("name",)
    inlines = [TopicInline, QuestionPaperInline]


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "weight", "subject")
    list_filter = ("subject",)
    search_fields = ("title",)


@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "type", "topic")
    list_filter = ("type", "topic")
    search_fields = ("title", "url")


@admin.register(QuestionPaper)
class QuestionPaperAdmin(admin.ModelAdmin):
    list_display = ("id", "year", "subject")
    list_filter = ("year", "subject")
    search_fields = ("year",)
