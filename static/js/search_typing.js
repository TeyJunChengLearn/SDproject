fetch('/search_typing', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({ input: searchInput })  // 'searchInput' is your user's text
})
.then(response => response.json())
.then(data => {
  console.log(data.suggestions);
})
.catch(error => console.error('Error:', error));
