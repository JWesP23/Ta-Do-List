from django.contrib import admin
from .models import Task, TaskGroup

@admin.register(TaskGroup)
class TaskGroupAdmin(admin.ModelAdmin):
    list_display = ("title", "description",)
    search_fields = ("title",)

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "group", "urgency", "due_date", "completed")
    list_filter = ("completed", "urgency", "due_date", "group")
    search_fields = ("title", "description")
    ordering = ("due_date",)