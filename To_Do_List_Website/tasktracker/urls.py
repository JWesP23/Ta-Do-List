from django.urls import path
from . import views

urlpatterns = [
    path("show_task/<int:task_id>", views.show_task, name="show_task_page"),
    path("create_task/", views.create_task, name="create_task_page"),
    path("create_subtask/<int:parent_task_id>", views.create_subtask, name="create_subtask_page"),
    path("edit_task/<int:task_id>", views.edit_task, name="edit_task_page"),
    path("delete_task/<int:task_id>", views.delete_task, name="delete_task"),
    path("tasks/<int:task_id>/toggle/", views.toggle_task, name="toggle_task"),
    path("show_task_group/<int:task_group_id>", views.show_task_group, name="show_task_group_page"),
    path("create_task_group/", views.create_task_group, name="create_task_group_page"),
    path("edit_task_group/<int:task_group_id>", views.edit_task_group, name="edit_task_group_page"),
    path("delete_task_group/<int:task_group_id>", views.delete_task_group, name="delete_task_group"),
    path("create_task_in_group/<int:task_group_id>", views.create_task_in_group, name="create_task_in_group_page"),
]