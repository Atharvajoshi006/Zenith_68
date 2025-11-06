from django.db import models

class Grade(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name

class Subject(models.Model):
    grade = models.ForeignKey(Grade, related_name='subjects', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    def __str__(self):
        return f"{self.name} ({self.grade})"

class Topic(models.Model):
    subject = models.ForeignKey(Subject, related_name='topics', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    weight = models.FloatField(default=0)
    def __str__(self):
        return f"{self.title} - {self.subject}"

class Resource(models.Model):
    topic = models.ForeignKey(Topic, related_name='resources', on_delete=models.CASCADE)
    type = models.CharField(max_length=50)
    title = models.CharField(max_length=200)
    url = models.URLField()
    def __str__(self):
        return self.title

class QuestionPaper(models.Model):
    subject = models.ForeignKey(Subject, related_name='papers', on_delete=models.CASCADE)
    year = models.IntegerField()
    pdf_url = models.URLField()
    solution_url = models.URLField(blank=True, null=True)
    def __str__(self):
        return f"{self.subject.name} - {self.year}"
