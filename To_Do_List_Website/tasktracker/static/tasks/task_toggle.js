document.addEventListener("DOMContentLoaded", () => {

    function getCSRFToken() {
        const name = "csrftoken";
        let cookieValue = null;
        if (document.cookie && document.cookie !== "") {
            const cookies = document.cookie.split(";");
            for (let cookie of cookies) {
                cookie = cookie.trim();
                if (cookie.startsWith(name + "=")) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    const csrftoken = getCSRFToken();

    function updateStrikethrough(checkbox) {
        const listItem = checkbox.closest("li.list-group-item");
        const title = listItem?.querySelector(".task-title");
        if (title) {
            title.classList.toggle("text-decoration-line-through", checkbox.checked);
        }
    }

    function updateParentFromSubtasks(parentId) {
        const parent = document.querySelector(`.task-checkbox[data-task-id='${parentId}']`);
        const subtasks = document.querySelectorAll(`.task-checkbox[data-parent-id='${parentId}']`);
        const allChecked = Array.from(subtasks).every(cb => cb.checked);
        parent.checked = allChecked;
        updateStrikethrough(parent);

        // Persist parent in DB
        fetch(window.toggleTaskUrlTemplate.replace("{id}", parentId), {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrftoken
            },
            body: JSON.stringify({ completed: allChecked })
        });
    }

    function toggleSubtasks(parentId, completed) {
        const subtasks = document.querySelectorAll(`.task-checkbox[data-parent-id='${parentId}']`);
        subtasks.forEach(cb => {
            cb.checked = completed;
            updateStrikethrough(cb);

            // Persist each subtask
            fetch(window.toggleTaskUrlTemplate.replace("{id}", cb.dataset.taskId), {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": csrftoken
                },
                body: JSON.stringify({ completed: completed })
            });
        });
    }

    document.querySelectorAll(".task-checkbox").forEach(checkbox => {
        updateStrikethrough(checkbox);

        checkbox.addEventListener("change", () => {
            const taskId = checkbox.dataset.taskId;
            const parentId = checkbox.dataset.parentId;
            const completed = checkbox.checked;

            if (!parentId) {
                // Parent changed → cascade subtasks
                toggleSubtasks(taskId, completed);

                fetch(window.toggleTaskUrlTemplate.replace("{id}", taskId), {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "X-CSRFToken": csrftoken
                    },
                    body: JSON.stringify({ completed: completed, cascade: true })
                });
            } else {
                // Subtask changed → update parent visually only
                fetch(window.toggleTaskUrlTemplate.replace("{id}", taskId), {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "X-CSRFToken": csrftoken
                    },
                    body: JSON.stringify({ completed: completed })
                }).then(() => {
                    updateParentFromSubtasks(parentId);
                });
            }

            updateStrikethrough(checkbox);
        });
    });
});