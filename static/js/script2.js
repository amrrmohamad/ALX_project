document.getElementById('dark-mode-toggle').addEventListener('click', function() {
    // Toggle dark mode for the entire page
    document.body.classList.toggle('dark-mode');
    document.querySelector('header').classList.toggle('dark-mode');
    document.querySelector('footer').classList.toggle('dark-mode');
    document.querySelector('.container').classList.toggle('dark-mode');
    document.querySelectorAll('.repo').forEach(repo => repo.classList.toggle('dark-mode'));

    // Toggle dark mode for the GitHub calendar
    const calendar = document.querySelector('#github-calendar');
    if (calendar) {
        calendar.classList.toggle('dark-mode');
    }
});

