const yearNav = document.querySelector('.year-nav');
const yearPicker = yearNav.querySelector('select');

yearNav.classList.add('year-nav--enhanced');

const updateNavHeight = () => {
  yearNav.closest('main').style.setProperty(
    '--year-nav-height', `${yearNav.getBoundingClientRect().height}px`
  );
};
updateNavHeight();
new ResizeObserver(updateNavHeight).observe(yearNav);

yearPicker.addEventListener('change', () => {
  if (yearPicker.value) {
    // Native fragment navigation preserves existing URLs and browser history.
    window.location.hash = yearPicker.value;
  }
});

const syncYearPicker = () => {
  yearPicker.value = window.location.hash;
  if (yearPicker.selectedIndex < 0) yearPicker.value = '';
};
window.addEventListener('hashchange', syncYearPicker);
syncYearPicker();
