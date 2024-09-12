document.getElementById('dark-mode-toggle').addEventListener('click', function() {
     // Toggle dark mode for the entire page
    document.body.classList.toggle('dark-mode');
    document.querySelector('header').classList.toggle('dark-mode');
    document.querySelectorAll('.nav-links li a').forEach(link => link.classList.toggle('dark-mode'));
    document.querySelectorAll('.button-header').forEach(button => button.classList.toggle('dark-mode'));
    document.querySelector('.search-bar input').classList.toggle('dark-mode');
    document.querySelector('.search-button').classList.toggle('dark-mode');

    // Toggle dark mode for the GitHub calendar
    const calendar = document.querySelector('#github-calendar');
    if (calendar) {
        calendar.classList.toggle('dark-mode');
    }
});
