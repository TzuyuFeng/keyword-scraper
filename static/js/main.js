// 搜尋時顯示 loading 狀態
document.addEventListener("DOMContentLoaded", function () {
  const form = document.querySelector("form[action*='search']");
  if (form) {
    form.addEventListener("submit", function () {
      const btn = form.querySelector("button[type='submit']");
      if (btn) {
        btn.disabled = true;
        btn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>搜尋中，請稍候...';
      }
    });
  }
});
