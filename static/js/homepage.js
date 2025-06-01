document.addEventListener("DOMContentLoaded", () => {
    const searchInput = document.getElementById("searchInput");

    searchInput.addEventListener("keydown", function(event) {
        // If user presses Enter key
        if (event.key === "Enter") {
            event.preventDefault();
            const query = searchInput.value.trim();
            if (query !== "") {
                window.location.href = `/search?q=${encodeURIComponent(query)}`;
            }
        }
    });

    // Optional: show placeholder suggestion box on focus
    searchInput.addEventListener("focus", function () {
        // Optionally show prefill UI or suggestion list here
    });
});
