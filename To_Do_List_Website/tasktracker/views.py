from functools import wraps
from operator import truediv

from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django import forms
from tasktracker.models import Task, TaskGroup
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json



#Deny logged-out users from executing views
def login_required_401(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            login_url = reverse("login_page")
            return redirect(f"{login_url}?next={request.path}")  #sends user back to view they were attempting after they login
        return view_func(request, *args, **kwargs)
    return _wrapped_view



# Root
def main(request):

    if request.user.is_authenticated:
        users_tasks = Task.objects.filter(user = request.user)       #filter all tasks in DB corresponding to the user
        users_groups = TaskGroup.objects.filter(user = request.user) #filter all taskgroups in DB corresponding to the user

        #Create list of tuples (group, tasks)
        group_task_pairs = []
        for group in users_groups:
            tasks_for_group = users_tasks.filter(group=group).order_by('completed', 'due_date') #order completed tasks at the bottom and then order by deadline
            group_task_pairs.append((group, tasks_for_group))

        context = {
            'group_task_pairs': group_task_pairs,
        }

        #If the user has no tasks send an empty group_task_pairs to trigger the banner prompting new users to get started
        if not users_tasks:
            context = {
                'group_task_pairs': [],
            }

    else:
        context = {
            'group_task_pairs': [],
        }

    return render(request, "main.html", context)



# Django form for creating and editing tasks
class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'urgency', 'due_date', 'group']
        widgets = {
            'due_date': forms.DateTimeInput(
                attrs={
                    'type': 'datetime-local',  #datetime picker
                    'class': 'form-control',
                }
            ),
        }

        group = forms.ChoiceField(required=True)

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['group'].queryset = TaskGroup.objects.filter(user= user)   #populate the dropdown with groups assigned to the user
            self.fields["group"].empty_label = None #removes a default dropdown choice since "General" should be the default



# Django form for creating and editing subtasks
class SubtaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'urgency', 'due_date']
        widgets = {
            'due_date': forms.DateTimeInput(
                attrs={
                    'type': 'datetime-local',  #datetime picker
                    'class': 'form-control',
                }
            ),
        }



# Django form for creating and editing task groups
class TaskGroupForm(forms.ModelForm):
    class Meta:
        model = TaskGroup
        fields = ['title', 'description']



# Create a new task
@login_required_401
def create_task(request):

    if request.method == "POST":

        task_form = TaskForm(request.POST, user= request.user) # create a form instance and populate it with data from the request

        #check whether submission is valid
        if task_form.is_valid():
            task = task_form.save(commit= False)  #save form data without commiting to DB
            task.user = request.user #attach the user to the task
            task.completed = False #all tasks should start uncompleted
            task.save() #commit form data and metadata (the user who created the task) to DB
            return redirect("home_page")

    else: #request is GET
        task_form = TaskForm(user= request.user) # create a blank form instance

    return render(request, "create_task.html", { "form" : task_form })



# Create a new task within a specified group (used for 'add task' buttons in group cards on main page)
@login_required_401
def create_task_in_group(request, task_group_id):

    group = get_object_or_404(TaskGroup, pk= task_group_id, user= request.user)

    if request.method == "POST":

        task_form = SubtaskForm(request.POST) # create a form instance and populate it with data from the request | Use subtask form because it is same as task form with no group dropdown

        #check whether submission is valid
        if task_form.is_valid():
            task = task_form.save(commit= False)  #save form data without commiting to DB
            task.user = request.user #attach the user to the task
            task.completed = False #all tasks should start uncompleted
            task.group = group
            task.save() #commit form data and metadata (the user who created the task) to DB
            return redirect("home_page")

    else: #request is GET
        task_form = SubtaskForm() # create a blank form instance | Use subtask form because it is same as task form with no group dropdown

    return render(request, "create_group_task.html", { "form" : task_form , "group" : group})



# Create a new subtask
@login_required_401
def create_subtask(request, parent_task_id):

    parent_task = get_object_or_404(Task, pk= parent_task_id)

    if parent_task.parent_task is not None:
        return JsonResponse({"success": False, "error": "Subtasks of subtasks are not allowed."}, status=400)

    #Deny users who do not own the parent task
    if not request.user == parent_task.user:
        return render(request, "403.html")

    if request.method == "POST":
        task_form = SubtaskForm(request.POST) # create a form instance and populate it with data from the request

        #check whether submission is valid
        if task_form.is_valid():
            task = task_form.save(commit= False)  #save form data without commiting to DB
            task.user = request.user #attach the user to the task
            task.completed = False #all tasks should start uncompleted
            task.parent_task = parent_task
            task.group = parent_task.group #subtasks inherit group from parents
            task.save() #commit form data and metadata (the user who created the task) to DB
            return redirect("home_page")


    else: #request is GET
        task_form = SubtaskForm() # create a blank form instance

    return render(request, "create_subtask.html", { "form" : task_form, "parent_task" : parent_task })



# Edit a task
@login_required_401
def edit_task(request, task_id):

    #Find the appropriate task
    task = get_object_or_404(Task, id=task_id, user=request.user)

    #Deny users who do not own the task
    if not request.user == task.user:
        return render(request, "403.html")

    if request.method == "POST":

        task_form = TaskForm(request.POST, instance=task, user=request.user)  # create a form instance and populate it with data from the request

        #check whether submission is valid
        if task_form.is_valid():
            task_form.save(commit=True) #save form data and commit to DB
            return redirect("home_page")

    else: #request is GET
        task_form = TaskForm(instance=task, user=request.user) # create a form populated with the Task's data

    return render(request, "edit_task.html", { "form" : task_form , "task" : task})



# Show a task's page
@login_required_401
def show_task(request, task_id):

    #Find the appropriate task
    task = get_object_or_404(Task, id=task_id, user=request.user)

    #Deny users who do not own the task
    if not request.user == task.user:
        return render(request, "403.html")

    #Find all subtasks
    subtasks = Task.objects.filter(parent_task = task).order_by('completed', 'due_date').values() #order completed tasks at the bottom and then order by deadline

    return render(request, "show_task.html", {"task": task, "subtasks": subtasks})



# Delete a task
@login_required_401
def delete_task(request, task_id):

    #Find the appropriate task
    task = get_object_or_404(Task, id=task_id, user=request.user)

    #Deny users who do not own the task
    if not request.user == task.user:
        return render(request, "403.html")

    #"are you sure" popup modal is set up in show_task.html

    if request.method == "POST":
        task.delete() #DB is set up to auto-cascade deletions to subtasks
        return redirect("home_page")

    return render(request, "403.html")  # fallback for GET requests for delete



#Toggle completion status of task
@login_required_401
def toggle_task(request, task_id):
    if request.method == "POST":
        task = get_object_or_404(Task, id=task_id, user=request.user)
        data = json.loads(request.body)
        task.completed = data.get("completed", False)
        task.save()

        # Only cascade if explicitly instructed
        cascade = data.get("cascade", False)
        if cascade:
            #cascade to subtasks
            Task.objects.filter(parent_task=task).update(completed=task.completed)

        return JsonResponse({"success": True, "completed": task.completed})
    return JsonResponse({"success": False}, status=400)



# Create a new task group
@login_required_401
def create_task_group(request):

    if request.method == "POST":

        group_form = TaskGroupForm(request.POST) # create a form instance and populate it with data from the request

        #check whether submission is valid
        if group_form.is_valid():
            group = group_form.save(commit= False)  #save form data without commiting to DB
            group.user = request.user #attach the user to the task group
            group.save() #commit form data and metadata (the user who created the group) to DB
            return redirect("home_page")

    else: #request is GET
        group_form = TaskGroupForm() # create a blank form instance

    return render(request, "create_task_group.html", { "form" : group_form })



# Show a task group's page
@login_required_401
def show_task_group(request, task_group_id):

    #Find the appropriate task group
    group = get_object_or_404(TaskGroup, id=task_group_id, user=request.user)

    #Find any tasks in this group
    tasks = Task.objects.filter(group = group, user=request.user).order_by('completed', 'due_date') #order completed tasks at the bottom and then order by deadline

    #Deny users who do not own the group
    if not request.user == group.user:
        return render(request, "403.html")


    return render(request, "show_task_group.html", {"group": group, "tasks": tasks})



# Edit a task group
@login_required_401
def edit_task_group(request, task_group_id):

    #Find the appropriate task group
    group = get_object_or_404(TaskGroup, id=task_group_id, user=request.user)

    #Deny users who do not own the group
    if not request.user == group.user:
        return render(request, "403.html")

    if request.method == "POST":

        group_form = TaskGroupForm(request.POST, instance=group)  # create a form instance and populate it with data from the request

        #check whether submission is valid
        if group_form.is_valid():
            group_form.save(commit=True) #save form data and commit to DB
            return redirect("home_page")

    else: #request is GET
        group_form = TaskGroupForm(instance=group) # create a form populated with the TaskGroup's data

    return render(request, "edit_task_group.html", { "form" : group_form , "group" : group})



# Delete a task group
@login_required_401
def delete_task_group(request, task_group_id):

    #Find the appropriate task group
    group = get_object_or_404(TaskGroup, id=task_group_id, user=request.user)

    #Deny users who do not own the group
    if not request.user == group.user:
        return render(request, "403.html")

    #"are you sure" popup modal is set up in show_task_group.html

    if request.method == "POST":
        group.delete() #DB is set up to auto-cascade deletions to tasks
        return redirect("home_page")

    return render(request, "403.html")  # fallback for GET requests for delete