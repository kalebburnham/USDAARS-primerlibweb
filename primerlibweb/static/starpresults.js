function toggleGroupDisplay(tablesId, toggleButtonId) {
    var group = document.getElementById(tablesId);
    var toggleButton = document.getElementById(toggleButtonId);
    console.log(group);
    if (group.style.display == 'none') {
        group.style.display = 'block';
    } else {
        group.style.display = 'none';
    }

    if (toggleButton.value === '-') {
        toggleButton.value = '+';
    } else {
        toggleButton.value = '-';
    }
}