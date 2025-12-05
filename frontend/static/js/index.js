const select = document.getElementById('theme-select');
const body = document.body;

const saved = localStorage.getItem('theme') || 'dark';
body.className = saved + '-theme';
select.value = saved;

select.addEventListener('change', function () {
    const theme = this.value;
    body.className = theme + '-theme';
    localStorage.setItem('theme', theme);
});