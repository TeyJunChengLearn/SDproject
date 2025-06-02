function clearSearch() {
  const input = document.getElementById("searchInput");
  input.value = "";
  input.focus(); // puts cursor back for retyping
}

document.addEventListener("DOMContentLoaded", function () {
  const input = document.getElementById("searchInput");

  input.addEventListener("keydown", function (e) {
    if (e.key === "Enter") {
      const query = input.value.trim();
      if (query !== "") {
        // Redirect to the search route with new query
        window.location.href = `/search?q=${encodeURIComponent(query)}`;
      }
    }
  });
});
