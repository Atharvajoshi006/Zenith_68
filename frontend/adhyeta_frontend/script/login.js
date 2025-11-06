document.getElementById("loginForm").addEventListener("submit", (e) => {
  e.preventDefault();
  const username = document.getElementById("username").value.trim();

  if (username !== "") {
    // Redirect to selection page
    window.location.href = `select.html?user=${encodeURIComponent(username)}`;
  }
});
