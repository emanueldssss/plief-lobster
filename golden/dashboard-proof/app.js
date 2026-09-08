const open = document.querySelector('#open'); const dialog = document.querySelector('#details'); const close = document.querySelector('#close');
open.addEventListener('click', () => dialog.showModal());
close.addEventListener('click', () => { dialog.close(); open.focus(); });
document.querySelector('#state').textContent = 'Ready'; document.querySelector('#motion-status').textContent = new URLSearchParams(location.search).has('fallback') ? 'Fallback motion path' : 'Native motion path';
fetch('/api/ok').catch(() => {});

