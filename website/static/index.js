function deleteList(listId) {
    fetch("/delete-list", {
      method: "POST",
      body: JSON.stringify({ listId: listId }),
    }).then((_res) => {
      window.location.href = "/home";
    });
  }