document.querySelectorAll('[data-vol]').forEach(btn => {
  btn.onclick = () => {
    const id = btn.dataset.vol;
    document.getElementById(id).scrollIntoView({
      behavior: 'smooth',
      block: 'start'
    });
  };
});
