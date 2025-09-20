from django.db import models
from django.contrib.auth.models import User

URGENCY_LEVELS = [
    (1, "Very Low"),
    (2, "Low"),
    (3, "Medium"),
    (4, "High"),
    (5, "Critical"),
]

class TaskGroup(models.Model):
    title = models.CharField(max_length=100, unique=False)              #The Group's title
    description = models.TextField(blank=True, null=True)              #a description the group
    user = models.ForeignKey(User, on_delete=models.CASCADE)           #the owner of the group

    def __str__(self):
        return self.title


class Task(models.Model):
    user = models.ForeignKey(                                           #the owner of the task
        User,
        on_delete=models.CASCADE,
        related_name="tasks"
    )
    group = models.ForeignKey(                                          #the group the task is in
        TaskGroup,
        on_delete=models.CASCADE,
        related_name="tasks",
        null=True,
        blank=True
    )
    title = models.CharField(max_length=255)                            #the owner of the group
    description = models.TextField(blank=True, null=True)               #a description of the task
    completed = models.BooleanField(default=False)                      #tracks whether the task has been completed
    urgency = models.IntegerField(choices=URGENCY_LEVELS, default=3)    #importance of the task on a scale of 5
    due_date = models.DateTimeField(null=True, blank=True)              #the deadline to complete the task by
    parent_task = models.ForeignKey(                                    #connects subtasks to tasks
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="subtasks"
    )

    def __str__(self):
        return f"{self.title} (Urgency {self.urgency})"

