from django.db import models


class Grade(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name = "Grade"
        verbose_name_plural = "Grades"

    def __str__(self):
        return str(self.name)


class Subject(models.Model):
    name = models.CharField(max_length=100)
    grade = models.ForeignKey(Grade, on_delete=models.CASCADE, related_name="subjects")

    class Meta:
        verbose_name = "Subject"
        verbose_name_plural = "Subjects"

    def __str__(self):
        return f"{self.name} (Grade: {self.grade})"


class Topic(models.Model):
    title = models.CharField(max_length=200)
    weight = models.FloatField(default=1)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="topics")

    class Meta:
        verbose_name = "Topic"
        verbose_name_plural = "Topics"

    def __str__(self):
        return f"{self.title} [{self.subject}]"


class Resource(models.Model):
    title = models.CharField(max_length=200)
    type = models.CharField(max_length=50)  # e.g., PDF, Video, Link
    url = models.URLField()
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name="resources")

    class Meta:
        verbose_name = "Resource"
        verbose_name_plural = "Resources"

    def __str__(self):
        return f"{self.title} ({self.type})"


class QuestionPaper(models.Model):
    year = models.IntegerField()
    pdf_url = models.URLField()
    solution_url = models.URLField(blank=True)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="papers")

    class Meta:
        verbose_name = "Question Paper"
        verbose_name_plural = "Question Papers"

    def __str__(self):
        return f"{self.subject} - {self.year}"
