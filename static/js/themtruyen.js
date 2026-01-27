document.addEventListener("DOMContentLoaded", () => {
  const dropdown = document.getElementById("genreDropdown");
  const selectedBox = document.getElementById("selectedGenres");

  if (!dropdown || !selectedBox) return;

  const form = dropdown.closest("form");
  const selected = new Map();

  // Toggle dropdown khi click box
  selectedBox.addEventListener("click", () => {
    dropdown.style.display =
      dropdown.style.display === "block" ? "none" : "block";
  });

  // Click chọn thể loại
  dropdown.querySelectorAll(".dropdown-item").forEach(item => {
    item.addEventListener("click", () => {
      const id = item.dataset.id;
      const name = item.dataset.name;

      if (selected.has(id)) return;

      selected.set(id, name);
      item.style.display = "none"; // ẩn item đã chọn

      // Tag hiển thị
      const tag = document.createElement("span");
      tag.className = "genre-tag";
      tag.textContent = name;


      // Input hidden gửi về Django
      const input = document.createElement("input");
      input.type = "hidden";
      input.name = "genres";
      input.value = id;
      input.dataset.id = id;

      tag.addEventListener("click", (e) => {
  e.stopPropagation();
  selected.delete(id);
  tag.remove();
  input.remove();
  item.style.display = "block";
});


      selectedBox.appendChild(tag);
      form.appendChild(input);
    });
  });

  // Click ngoài → đóng dropdown
  document.addEventListener("click", (e) => {
    if (!e.target.closest(".genre-select")) {
      dropdown.style.display = "none";
    }
  });
});
