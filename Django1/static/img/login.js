/* ===============================
   AUTH MODAL SCRIPT (FIXED)
   =============================== */

document.addEventListener("DOMContentLoaded", () => {
  const overlay = document.getElementById("authOverlay");
  const openBtn = document.getElementById("openAuth");
  const closeBtn = document.getElementById("closeAuth");

  const loginForm = document.getElementById("loginForm");
  const registerForm = document.getElementById("registerForm");

  const title = document.getElementById("authTitle");
  const desc = document.getElementById("authDesc");

  /* ===============================
     Open / Close modal
     =============================== */

  function openAuth(mode = "login") {
    overlay.classList.remove("hide");
    overlay.classList.add("show");
    document.body.style.overflow = "hidden";
    switchAuth(mode);
  }

  function closeAuth() {
    overlay.classList.remove("show");
    overlay.classList.add("hide");
    document.body.style.overflow = "";

    setTimeout(() => {
      overlay.classList.remove("hide");
    }, 200);
  }

  if (openBtn) {
    openBtn.addEventListener("click", () => openAuth("login"));
  }

  if (closeBtn) {
    closeBtn.addEventListener("click", closeAuth);
  }

  overlay.addEventListener("click", (e) => {
    if (e.target === overlay) closeAuth();
  });

  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && overlay.classList.contains("show")) {
      closeAuth();
    }
  });

  /* ===============================
     Switch Login / Register
     =============================== */

  document.querySelectorAll("[data-switch]").forEach((el) => {
    el.addEventListener("click", () => {
      switchAuth(el.dataset.switch);
    });
  });

  function switchAuth(type) {
    if (type === "register") {
      loginForm.classList.remove("active");
      registerForm.classList.add("active");

      title.textContent = "Đăng ký";
      desc.textContent = "Tạo tài khoản mới";
    } else {
      registerForm.classList.remove("active");
      loginForm.classList.add("active");

      title.textContent = "Đăng nhập";
      desc.textContent = "Chào mừng bạn quay lại";
    }
  }

  /* ===============================
     Toggle password visibility
     =============================== */

  document.querySelectorAll(".toggle-password").forEach((icon) => {
    icon.addEventListener("click", () => {
      const input = icon.previousElementSibling;
      if (!input) return;

      const isPassword = input.type === "password";
      input.type = isPassword ? "text" : "password";
      icon.textContent = isPassword ? "🙈" : "👁";
    });
  });

  /* ===============================
     Auto open modal (backend signal)
     =============================== */

  if (window.AUTH_OPEN) {
    openAuth(window.AUTH_MODE || "login");
  }
});
