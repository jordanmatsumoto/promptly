from django.db import models
from django.contrib.auth.models import User

class Project(models.Model):
    """A project the user is working on."""

    text = models.CharField(max_length=200)
    date_added = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.text
    
class Task(models.Model):
    """Something specific tracked about a project."""

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks')
    text = models.TextField()
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'tasks'

    def __str__(self):
        return f"{self.text[:50]}..."

class AISuggestion(models.Model):
    """AI-generated suggestions for a project."""
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='ai_suggestions', null=True, blank=True)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='ai_suggestions', null=True, blank=True)
    text = models.TextField()
    date_added = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.text[:50]}..."