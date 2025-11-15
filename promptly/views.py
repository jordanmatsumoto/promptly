from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import Http404, JsonResponse

from .models import Project, Task, AISuggestion
from .forms import ProjectForm, TaskForm, AISuggestionForm
from .llama_utils import generate_suggestion

def index(request):
    """Show home page with quick stats, works for both logged-in and anonymous users."""
    if request.user.is_authenticated:
        user_projects = Project.objects.filter(owner=request.user)
        project_count = user_projects.count()
        task_count = Task.objects.filter(project__owner=request.user).count()
        ai_suggestions_count = AISuggestion.objects.filter(owner=request.user).count()
    else:
        # Defaults for users without accounts.
        project_count = task_count = ai_suggestions_count = 0

    context = {
        'project_count': project_count,
        'task_count': task_count,
        'ai_suggestions_count': ai_suggestions_count,
    }
    return render(request, 'promptly/index.html', context)

@login_required
def projects(request):
    """Show all projects."""
    projects = Project.objects.filter(owner=request.user).order_by('date_added')
    context = {'projects': projects}
    return render(request, 'promptly/projects.html', context)

@login_required
def project(request, project_id):
    """Show a single project and all its tasks."""
    project = Project.objects.get(id=project_id)
    # Make sure the project belongs to the current user.
    if project.owner != request.user:
        raise Http404

    tasks = project.tasks.order_by('-date_added')
    context = {'project': project, 'tasks': tasks}
    return render(request, 'promptly/project.html', context)

@login_required
def new_project(request):
    """Add a new project."""
    if request.method != 'POST':
        # No data submitted, create a blank form.
        form = ProjectForm()
    else:
        # POST data submitted, process data.
        form = ProjectForm(data=request.POST)
        if form.is_valid():
            new_project = form.save(commit=False)
            new_project.owner = request.user
            new_project.save()
            return redirect('promptly:projects')
        
    # Display a blank or invalid form.
    context = {'form': form}
    return render(request, 'promptly/new_project.html', context)

@login_required
def edit_project(request, project_id):
    """Edit a project."""
    project = get_object_or_404(Project, id=project_id)
    if project.owner != request.user:
        raise Http404

    if request.method != 'POST':
        form = ProjectForm(instance=project)
    else:
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            return redirect('promptly:project', project_id=project.id)

    context = {'project': project, 'form': form}
    return render(request, 'promptly/edit_project.html', context)

@login_required
def delete_project(request, project_id):
    """Delete a project."""
    project = Project.objects.get(id=project_id)
    if project.owner != request.user:
        raise Http404
    project.delete()
    return JsonResponse({}, status=204)

@login_required
def new_task(request, project_id):
    """Add a new task for a particular project."""
    project = Project.objects.get(id=project_id)
    if project.owner != request.user:
        raise Http404
    
    if request.method != 'POST':
        # No data submitted; create a blank form.
        form = TaskForm()
    else:
        # POST data submitted; process data.
        form = TaskForm(data=request.POST)
        if form.is_valid():
            new_task = form.save(commit=False)
            new_task.project = project
            new_task.save()
            return redirect('promptly:project', project_id=project_id)

    # Display a blank or invalid form.
    context = {'project': project, 'form': form}
    return render(request, 'promptly/new_task.html', context)

@login_required    
def edit_task(request, task_id):
    """Edit an existing task."""
    task = Task.objects.get(id=task_id)
    project = task.project
    if project.owner != request.user:
        raise Http404

    if request.method != 'POST':
        # Initial request; pre-fill form with the current task.
        form = TaskForm(instance=task)
    else:
        # POST data submitted; process data.
        form = TaskForm(instance=task, data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('promptly:project', project_id=project.id)

    context = {'task': task, 'project': project, 'form': form}
    return render(request, 'promptly/edit_task.html', context)

@login_required
def delete_task(request, task_id):
    """Delete an existing task."""
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method."}, status=400)

    task = get_object_or_404(Task, id=task_id)

    if task.project.owner != request.user:
        return JsonResponse({"error": "Not authorized."}, status=403)

    task.delete()
    return JsonResponse({}, status=204)

@login_required
def generate_ai_suggestion(request):
    """Generate an AI suggestion for a project."""
    if request.method == "POST":
        prompt = request.POST.get("prompt", "").strip()
        project_id = request.POST.get("project_id")

        if not prompt:
            return JsonResponse({"error": "Prompt is empty."}, status=400)

        # Fetch the project if provided
        project = None
        if project_id:
            try:
                project = Project.objects.get(id=project_id, owner=request.user)
            except project.DoesNotExist:
                return JsonResponse({"error": "project not found."}, status=404)

        # Generate AI suggestion
        suggestion_text = generate_suggestion(prompt)

        # Save AI suggestion to database
        ai_suggestion = AISuggestion.objects.create(
            project=project,
            text=suggestion_text,
            owner=request.user
        )

        return JsonResponse({"suggestion": suggestion_text})

    return JsonResponse({"error": "Invalid request method."}, status=400)

@login_required
def ai_suggestions(request):
    """Show all AI Suggestions."""
    query = request.GET.get('q', '')
    project_id = request.GET.get('project', '')

    # All projects for the dropdown
    projects = Project.objects.filter(owner=request.user)

    suggestions = AISuggestion.objects.filter(owner=request.user).select_related('project', 'task')

    # Apply search filter
    if query:
        suggestions = suggestions.filter(text__icontains=query)
    
    # Apply project filter
    if project_id:
        suggestions = suggestions.filter(project_id=project_id)

    suggestions = suggestions.order_by('-date_added')
    return render(request, 'promptly/ai_suggestions.html', {
        'suggestions': suggestions,
        'query': query,
        'projects': projects,
        'selected_project': project_id
    })

@login_required
def edit_ai_suggestion(request, suggestion_id):
    """Edit an AI Suggestion."""
    suggestion = get_object_or_404(AISuggestion, id=suggestion_id, owner=request.user)
    if request.method == 'POST':
        form = AISuggestionForm(request.POST, instance=suggestion)
        if form.is_valid():
            form.save()
            return redirect('promptly:ai_suggestions')
    else:
        form = AISuggestionForm(instance=suggestion)
    return render(request, 'promptly/edit_ai_suggestion.html', {'form': form, 'suggestion': suggestion})

@login_required
def delete_ai_suggestion(request, suggestion_id):
    """Delete an AI Suggestion."""
    if request.method == "POST":
        suggestion = get_object_or_404(AISuggestion, id=suggestion_id, owner=request.user)
        suggestion.delete()
        return JsonResponse({}, status=204)
    return JsonResponse({'error': 'Invalid request'}, status=400)