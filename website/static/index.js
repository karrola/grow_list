function deleteList(listId) {
  fetch("/delete-list", {
    method: "POST",
    body: JSON.stringify({ listId: listId }),
  }).then((_res) => {
    window.location.href = "/home";
  });
}

function deleteTask(taskId) {
fetch("/delete-task", {
  method: "POST",
  body: JSON.stringify({ taskId: taskId }),
}).then((_res) => {
  window.location.reload();
});
}