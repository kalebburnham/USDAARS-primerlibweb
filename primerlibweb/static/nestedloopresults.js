function toggle_pcr_condition_display(id) {
    element = document.getElementById(id);
    if (element.style.display == 'none') {
        element.style.display = 'block';
    } else {
        element.style.display = 'none';
    }
}