"""Defines URL paterns for promptly."""

from django.urls import path

from . import views

app_name = 'promptly'
urlpatterns = [
    # Home page
    path('', views.index, name='index'),
    # Page that shows all projects.
    path('projects/', views.projects, name='projects'),
    # Page for a single project.
    path('projects/<int:project_id>/', views.project, name='project'),
    # Page for adding a new project.
    path('new_project/', views.new_project, name='new_project'),
    # Page for editing a project.
    path('edit_project/<int:project_id>/', views.edit_project, name='edit_project'),
    # Page for deleting a project.
    path('delete_project/<int:project_id>/', views.delete_project, name='delete_project'),
    # Page for adding a new task.
    path('new_task/<int:project_id>/', views.new_task, name='new_task'),
    # Page for editing an task.
    path('edit_task/<int:task_id>/', views.edit_task, name='edit_task'),
    # Page for deleting an task.
    path('delete_task/<int:task_id>/', views.delete_task, name='delete_task'),
    # Page for generating an AI Suggestion.
    path('generate-ai/', views.generate_ai_suggestion, name='generate_ai'),
    # Page for all AI Suggestions.
    path('ai_suggestions/', views.ai_suggestions, name='ai_suggestions'),
    # Page for editing AI Suggestions.
    path('ai_suggestions/edit/<int:suggestion_id>/', views.edit_ai_suggestion, name='edit_ai_suggestion'),
    # Page for deleting AI Suggestions.
    path('ai_suggestions/delete/<int:suggestion_id>/', views.delete_ai_suggestion, name='delete_ai_suggestion'),
]