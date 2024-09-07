from flask import Flask, jsonify, request
from flask import render_template, url_for, session, redirect
from werkzeug.security import generate_password_hash, check_password_hash
import requests
import sqlite3
import os
import base64
from database import init_db

app = Flask(__name__)

#################################################################
# remeber before run programming you should run database.py first
# to create data base => try this way if something happen
#################################################################

# calling function data base to create it
init_db()


# The path of main page
@app.route('/')
def home():
    if 'username' in session:
        return render_template('index.html')
    else:
        return redirect(url_for('login'))


# The path of log in page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # get form data
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        # connect to data base
        with sqlite3.connect('users.db') as data:
            cursor = data.cursor()
            cursor.execute(
                'SELECT * FROM users WHERE username = ?', (username,)
                )
            user = cursor.fetchone()
            email = cursor.fetchone()

            # return the main page if user name exist
            if user and check_password_hash(user[2], password):
                session['username'] = username
                return redirect(url_for('home'))
            else:
                return "Check user name or password"

    return render_template('login.html')


# The path of sign up page
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])

        # connect to data base
        with sqlite3.connect('users.db') as data:
            cursor = data.cursor()

            try:
                cursor.execute("""
                    INSERT INTO users 
                    (username, password, email)
                    VALUES (?, ?, ?)
                    """,(username, password, email))
                data.commit()
                return redirect(url_for('home'))
            except sqlite3.IntegrityError:
                return "user name or email is already exist"

    return render_template('signup.html')


@app.route('/get_readme/<username>/<repo>', methods=['GET'])
def get_user_readme(username, repo):
    """Fetch the README.md file from a GitHub repository"""
    repo_url = f"https://api.github.com/repos/{username}/{repo}/readme"
    headers = {'Accept': 'application/vnd.github.v3+json'}
    response = requests.get(repo_url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        content = base64.b64decode(data['content']).decode('utf-8')
        return jsonify({'content': content})
    else:
        return jsonify({'error': 'README not found'}), 404


#The path of GitHub stats
@app.route('/github-stats/<username>', methods=['GET'])
def get_github_stats(username):
    user_url = f'https://api.github.com/users/{username}'
    repos_url = f'https://api.github.com/users/{username}/repos'

    user_response = requests.get(user_url)
    repos_response = requests.get(repos_url)

    try:
        # Send requests to the GitHub API with a timeout
        user_response = requests.get(user_url, timeout=5)
        repos_response = requests.get(repos_url, timeout=5)
        var1 = user_response.status_code
        var2 = user_response.status_code

        if var1 == 200 and var2 == 200:
            user_data = user_response.json()
            repos_data = repos_response.json()

            # make a stats dictionary
            stats = {
                'username': user_data['login'],
                'avatar_url': user_data['avatar_url'],  # url for image profile
                'public_repos': user_data['public_repos'],
                'followers': user_data['followers'],
                'following': user_data['following'],
                'created_at': user_data['created_at'],
                'repos': []
            }

            for repo in repos_data:
                repo_info = {
                    'name': repo['name'],
                    'stars': repo['stargazers_count'],
                    'forks': repo['forks_count'],
                    'html_url': repo['html_url']
                }
                stats['repos'].append(repo_info)

            return jsonify(stats)
        else:
            return jsonify(
                {'Error': 'User not found or unable to fetch repos'}), 404

    # return request exceptions, such as timeout or connection errors
    except requests.exceptions.RequestException as error_e:
        return jsonify({'error': f'Error fetching data: {error_e}'}), 500


# The log out function
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))


# to make password not appear in data base
app.secret_key = 'your_secret_key'

if __name__ == '__main__':
    app.run(debug=True, port=5000)


