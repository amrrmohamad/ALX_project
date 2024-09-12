async function loadGitHubStats() {
    const username = document.getElementById('username').value.trim();
    const resultDiv = document.getElementById('result');
    const loadingSpinner = document.getElementById('loading-spinner');
    resultDiv.innerHTML = '';
    loadingSpinner.style.display = 'block';  // Show loading spinner

    if (username) {
        try {
            const response = await fetch(`/github-stats/${username}`);
            if (response.ok) {
                const data = await response.json();
                loadingSpinner.style.display = 'none';  // Hide loading spinner

                // html file to show data in page
                resultDiv.innerHTML = `
                    <div>
                        <img src="${data.avatar_url}" alt="${data.username}'s avatar" class="avatar">
                        <div class="left-section">
                            <h2 stylesheet="font-family: 'Arial', sans-serif;">Username: ${data.username}</h2>
                            <p>Public Repositories: <strong>${data.public_repos}</strong></p>
                            <p>Followers: ${data.followers}</p>
                            <p>Following: ${data.following}</p>
                            <p>Created Date: ${new Date(data.created_at).toLocaleDateString()}</p>
                        </div>
                        <hr>
                        <div id="readme-section" class="readme-section">
                            <p>Loading README...</p>
                        </div>
                        <hr>
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
                loadingSpinner.style.display = 'none';  // Hide loading spinner
                // print error at console to discover the error
                console.error('Server returned an error:', response.status, response.statusText);
                resultDiv.innerHTML = '<p>Could not fetch repositories or find the user</p>';
            }
            //Fetch README.md from the user's profile repository
            const readmeResponse = await fetch(`/get_user_readme/${username}`);
            if (readmeResponse.ok) {
                    const readmeData = await readmeResponse.json();
                    const readmeSection = document.getElementById('readme-section');
                    readmeSection.innerHTML = `
                        <h3>README.md</h3>
                        <pre>${readmeData.content}</pre>
                    `;
            } else {
                const readmeSection = document.getElementById('readme-section');
                readmeSection.innerHTML = `<p>README.md not found for this user.</p>`;
            }
        } catch (error) {
            loadingSpinner.style.display = 'none';  // Hide loading spinner
            // same to discover error at console
            console.error('Server returned an error:', response.status, response.statusText);
            resultDiv.innerHTML = '<p> Error fetching the data</p>';
        }
    } else {
        loadingSpinner.style.display = 'none';  // Hide loading spinner
        resultDiv.innerHTML = '<p>Please enter a username</p>';
    }
}
