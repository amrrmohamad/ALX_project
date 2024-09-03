async function loadGitHubStats() {
    const username = document.getElementById('username').value.trim();
    const resultDiv = document.getElementById('result');
    resultDiv.innerHTML = '';

    if (username) {
        try {
            const response = await fetch(`/github-stats/${username}`);
            if (response.ok) {
                const data = await response.json();
                // html file to show data in page
                resultDiv.innerHTML = `
                    <div>
                        <img src="${data.avatar_url}" alt="${data.username}'s avatar" class="avatar">
                        <h2 stylesheet="font-family: 'Arial', sans-serif;">Username: ${data.username}</h2>
                        <p>Public Repositories: <strong>${data.public_repos}</strong></p>
                        <p>Followers: ${data.followers}</p>
                        <p>Following: ${data.following}</p>
                        <p>Created Date: ${new Date(data.created_at).toLocaleDateString()}</p>
                        <h3>Repositories:</h3>
                        ${data.repos.map(repo => `
                            <div class="repo">
                                <a href="${repo.html_url}" target="_blank">${repo.name}</a>
                                <p>Stars: ${repo.stars}</p>
                                <p>Forks: ${repo.forks}</p>
                            </div>
                        `).join('')}
                    </div>
                `;
                // show the calendar
                new GitHubCalendar("#github-calendar", username);

            } else {
                // print error at console to discover the error
                console.error('Server returned an error:', response.status, response.statusText);
                resultDiv.innerHTML = '<p>Could not fetch repositories or find the user</p>';
            }
        } catch (error) {
            // same to discover error at console
            console.error('Server returned an error:', response.status, response.statusText);
            resultDiv.innerHTML = '<p> Error fetching the data</p>';
        }
    } else {
        resultDiv.innerHTML = '<p>Please enter a username</p>';
    }
}
