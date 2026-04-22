/* ===============================
   AUTH MODAL SCRIPT (FINAL AJAX)
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

  if (openBtn) openBtn.addEventListener("click", () => openAuth("login"));
  if (closeBtn) closeBtn.addEventListener("click", closeAuth);

  overlay.addEventListener("click", (e) => {
    if (e.target === overlay) closeAuth();
  });

  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && overlay.classList.contains("show")) closeAuth();
  });

  /* ===============================
     Switch Login / Register
     =============================== */
  document.querySelectorAll("[data-switch]").forEach((el) => {
    el.addEventListener("click", () => switchAuth(el.dataset.switch));
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

  /* ==========================================================
     XỬ LÝ ĐĂNG NHẬP/ĐĂNG KÝ BẰNG AJAX (GIỮ MODAL KHI SAI)
     ========================================================== */
  const handleAuthSubmit = async (form, successMsg) => {
    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      const formData = new FormData(form);
      const btn = form.querySelector(".auth-btn");
      const originalText = btn.textContent;

      // Hiệu ứng chờ
      btn.textContent = "Đang xử lý...";
      btn.disabled = true;

      try {
        const response = await fetch(form.action, {
          method: "POST",
          body: formData,
          headers: { "X-Requested-With": "XMLHttpRequest" }
        });

        const data = await response.json();

        if (data.success) {
          // Thành công: Reload trang hoặc chuyển hướng
          window.location.reload();
        } else {
          // Thất bại: Ở lại Modal và báo lỗi
          alert(data.message || "Có lỗi xảy ra, vui lòng thử lại!");
          btn.textContent = originalText;
          btn.disabled = false;
        }
      } catch (error) {
        console.error("Auth Error:", error);
        btn.textContent = originalText;
        btn.disabled = false;
      }
    });
  };

  if (loginForm) handleAuthSubmit(loginForm, "Đăng nhập thành công!");
  if (registerForm) handleAuthSubmit(registerForm, "Đăng ký thành công!");

  if (window.AUTH_OPEN) openAuth(window.AUTH_MODE || "login");
});