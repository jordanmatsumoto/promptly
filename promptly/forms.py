from django import forms

from .models import Project, Task, AISuggestion

class ProjectForm(forms.ModelForm):
    """Form for creating or editing a Project."""

    class Meta:
        model = Project
        fields = ['text']
        labels = {'text': ''}

class TaskForm(forms.ModelForm):
    """Form for creating or editing a Task."""

    class Meta:
        model = Task
        fields = ['text']
        labels = {'text': ''}
        widgets = {
            'text': forms.Textarea(attrs={'cols': 80})
        }

class AISuggestionForm(forms.ModelForm):
    """Form for editing an AI-generated suggestion."""

    class Meta:
        model = AISuggestion
        fields = ['text']
        labels = {'text': ''}
        widgets = {
            'text': forms.Textarea(attrs={'cols': 80, 'rows': 4})
        }