from django.db import models
from django.contrib.auth.models import User


class StudentProfile(models.Model):
    """
    Extends the default Django User model with extra fields for students.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=32)
    student_type = models.CharField(max_length=64)
    created_at = models.DateTimeField(auto_now_add=True)
    last_login_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username}"

    class Meta:
        verbose_name = "Student Profile"
        verbose_name_plural = "Student Profiles"
        ordering = ['-created_at']


class OTPCode(models.Model):
    """
    Stores one-time passwords (OTP) for password reset / verification.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    def __str__(self):
        return f"OTP {self.code} for {self.user.username}"

    class Meta:
        verbose_name = "OTP Code"
        verbose_name_plural = "OTP Codes"
        ordering = ['-created_at']

# --- Learning models ---

class Course(models.Model):
    title = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Topic(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='topics')
    title = models.CharField(max_length=120)
    summary = models.TextField(blank=True)

    def __str__(self):
        return f"{self.course.title} → {self.title}"


class Lesson(models.Model):
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=160)
    content = models.TextField()  # HTML/Markdown allowed
    order = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.topic.title} → {self.order}. {self.title}"


class Enrollment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'course')

    def __str__(self):
        return f"{self.user.username} in {self.course.title}"


class LessonProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('user', 'lesson')

    def __str__(self):
        return f"{self.user.username} → {self.lesson} → {'✔' if self.completed else '…'}"
# --- Quiz models (adaptive) ---

class QuizQuestion(models.Model):
    DIFFICULTY = (
        ('easy', 'Easy'),
        ('med', 'Medium'),
        ('hard', 'Hard'),
    )
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY, default='easy')
    explanation = models.TextField(blank=True)

    def __str__(self):
        return f"[{self.topic.title}] {self.text[:50]}"


class QuizChoice(models.Model):
    question = models.ForeignKey(QuizQuestion, on_delete=models.CASCADE, related_name='choices')
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"{'✓' if self.is_correct else '•'} {self.text[:40]}"


class QuizAttempt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quiz_attempts')
    created_at = models.DateTimeField(auto_now_add=True)
    score = models.IntegerField(default=0)
    total = models.IntegerField(default=0)
    source = models.CharField(max_length=32, default='weekly')  # weekly/daily/custom

    def __str__(self):
        return f"{self.user.username} {self.score}/{self.total} @ {self.created_at:%Y-%m-%d}"


class AttemptAnswer(models.Model):
    attempt = models.ForeignKey(QuizAttempt, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(QuizQuestion, on_delete=models.CASCADE)
    chosen_choice = models.ForeignKey(QuizChoice, on_delete=models.SET_NULL, null=True)
    correct = models.BooleanField(default=False)
# --- AI Assistant models ---

class AssistantThread(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assistant_threads')
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Thread #{self.id} for {self.user.username}"


class AssistantMessage(models.Model):
    ROLE_CHOICES = (
        ('user', 'User'),
        ('assistant', 'Assistant'),
        ('system', 'System'),
    )
    thread = models.ForeignKey(AssistantThread, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=16, choices=ROLE_CHOICES)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
# --- Study Planner models ---

class StudyPlan(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='study_plans')
    title = models.CharField(max_length=160, default='Exam Study Plan')
    exam_date = models.DateField(null=True, blank=True)
    days = models.PositiveIntegerField(default=7)  # if exam_date not provided
    daily_minutes = models.PositiveIntegerField(default=180)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.title} ({self.user.username})"


class StudyTask(models.Model):
    plan = models.ForeignKey(StudyPlan, on_delete=models.CASCADE, related_name='tasks')
    date = models.DateField()
    topic = models.CharField(max_length=200)
    minutes = models.PositiveIntegerField(default=45)
    is_break = models.BooleanField(default=False)
    done = models.BooleanField(default=False)

    class Meta:
        ordering = ['date', 'id']

    def __str__(self):
        kind = 'Break' if self.is_break else 'Study'
        return f"{self.date} • {kind} • {self.topic} ({self.minutes}m)"
# --- Study Hub models (Exams, Subjects, Resources, Weightages) ---

class Exam(models.Model):
    name = models.CharField(max_length=120, unique=True)
    grade = models.CharField(max_length=40, blank=True)  # e.g., "Class 12", "UG", etc.
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.name} ({self.grade})" if self.grade else self.name


class Subject(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='subjects')
    name = models.CharField(max_length=120)

    class Meta:
        unique_together = ('exam', 'name')
        ordering = ['name']

    def __str__(self):
        return f"{self.exam.name} → {self.name}"


class SubjectWeightage(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='weightages')
    weight_percent = models.PositiveIntegerField()  # 0-100
    year = models.PositiveIntegerField(null=True, blank=True)  # optional (e.g., 2024 pattern)

    class Meta:
        ordering = ['-year', 'subject__name']

    def __str__(self):
        return f"{self.subject.name} {self.weight_percent}%"


class Resource(models.Model):
    KIND_CHOICES = (
        ('youtube', 'YouTube Lesson'),
        ('notes', 'Study Notes'),
        ('paper', 'Past Paper'),
    )
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='resources')
    kind = models.CharField(max_length=16, choices=KIND_CHOICES)
    title = models.CharField(max_length=200)
    url = models.URLField()
    source = models.CharField(max_length=120, blank=True)  # e.g., channel/site
    year = models.PositiveIntegerField(null=True, blank=True)  # for papers
    solution_url = models.URLField(blank=True)  # for papers with solutions

    class Meta:
        ordering = ['kind', '-year', 'title']

    def __str__(self):
        return f"[{self.get_kind_display()}] {self.title}"

