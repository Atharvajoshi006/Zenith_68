// login.js (paste-ready)
// Requires: <form id="loginForm"> and <input id="username">
// Optional: <input id="password">  (if present, will attempt backend login)

document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("loginForm");
  const usernameEl = document.getElementById("username");
  const passwordEl = document.getElementById("password"); // optional

  if (!form || !usernameEl) {
    console.warn("loginForm or username input not found.");
    return;
  }

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const username = (usernameEl.value || "").trim();
    const password = passwordEl ? passwordEl.value : "";

    if (!username) {
      alert("Please enter a username.");
      return;
    }

    // If a password field exists and has a value, try backend login
    if (passwordEl && password) {
      try {
        // api.js should be included before this file
        const res = await API.login(username, password);
        // success: store and redirect exactly like your current flow
        localStorage.setItem("user", res.user || username);
        window.location.href = `select.html?user=${encodeURIComponent(res.user || username)}`;
        return;
      } catch (err) {
        console.error(err);
        alert("Login failed. Check credentials or try without password (guest mode).");
        return;
      }
    }

    // Guest mode (no password field or left empty): keep your original behavior
    localStorage.setItem("user", username);
    window.location.href = `select.html?user=${encodeURIComponent(username)}`;
  });
});
