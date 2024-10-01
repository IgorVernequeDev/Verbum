function toggleUserMenu() {
    const buttonsUser = document.getElementById('userInterface');
    if (buttonsUser.style.display !== 'none') {
        buttonsUser.style.display = 'none';
    } else {
        buttonsUser.style.display = 'block';
    }
}