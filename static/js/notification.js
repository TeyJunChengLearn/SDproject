function markAllAsRead() {
  fetch('/mark_all_read', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    }
  }).then(response => {
    if (response.ok) {
      location.reload(); // Refresh to reflect updated read states
    } else {
      console.error('Failed to mark all as read');
    }
  });
}

// Attach the function to the element when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  const markReadBtn = document.querySelector('.mark-read');
  if (markReadBtn) {
    markReadBtn.addEventListener('click', markAllAsRead);
  }
});
