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
    """
    It's a function to route for main page of website 
    """
    if 'username' in session:
        return render_template('index.html')
    else:
        return redirect(url_for('login'))


# The path of log in page
@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Login function page using POST method:
        connect to data base and check of user
        or password is correct or not:
            if  True => redirect home page
                False => show error massage
    """
    if request.method == 'POST':
        # get form data
        username = request.form['username']
        password = request.form['password']

        if not username or not password:
            return jsonify({'error':'Please enter username and password'}), 400

        # connect to data base
        with sqlite3.connect('users.db') as conn:
            cursor = conn.cursor()
            cursor.execute(
                'SELECT * FROM users WHERE username = ?', (username,)
                )
            user = cursor.fetchone()

            # return the main page if user name exist
            if user:
                stored_password = user[2]
                if check_password_hash(stored_password, password):
                    session['username'] = username
                    return redirect(url_for('home'))
                else:
                    print("Password is incorrect")
                    return jsonify({"error": "Check user name or password"}), 400
            else:
                print("User name is incorrect")
                return jsonify({"error": "Check user name or password"}), 400

    return render_template('login.html')


# The path of sign up page
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """
    Sign up function using method GET and POST:
        connect to data base:
            insert user, email and password
            check if user is exist or not
    """
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        if not username or not email or not password:
            return jsonify({'error': 'Please enter username, email and password'}), 400
        
        hashed_password = generate_password_hash(password)

        # connect to data base
        try:
            with sqlite3.connect('users.db') as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO users 
                    (username, password, email)
                    VALUES (?, ?, ?)
                    """,(username, hashed_password, email))
                conn.commit()
                return redirect(url_for('home'))
        except sqlite3.IntegrityError:
            print("User name or email is already exist")
            return jsonify({"error": "user name or email is already exist"}), 400

    return render_template('signup.html')


@app.route('/get_readme/<username>/<repo>', methods=['GET'])
def get_user_readme(username, repo):
    """Fetch the README.md file from a GitHub repository"""
    repo_url = f"https://api.github.com/repos/{username}/{repo}/readme"
    headers = {'Accept': 'application/vnd.github.v3+json'}
    response = requests.get(repo_url, headers=headers)

    if response.status_code == 200:
        content = base64.b64decode(response.json()['content']).decode('utf-8')
        return jsonify({'content': content})
    else:
        return jsonify({'error': 'README not found'}), 404


#The path of GitHub stats
@app.route('/github-stats/<username>', methods=['GET'])
def get_github_stats(username):
    """
    Fetch data from GitHub website:
        get username, stars, forks, number of repo
        following, followers, avatar and activity
        store all of this in json file
            user_data, repos_data
    """
    user_url = f'https://api.github.com/users/{username}'
    repos_url = f'https://api.github.com/users/{username}/repos'

    try:
        # Send requests to the GitHub API with a timeout
        user_response = requests.get(user_url, timeout=5)
        repos_response = requests.get(repos_url, timeout=5)

        if  user_response.status_code == 200 and  repos_response.status_code == 200:
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
            return jsonify({'Error': 'User not found or unable to fetch repos'}), 404

    # return request exceptions, such as timeout or connection errors
    except requests.exceptions.RequestException as error_e:
        return jsonify({'error': f'Error fetching data: {error_e}'}), 500


# The log out function
@app.route('/logout')
def logout():
    """ 
    log out function 
        remove username from session
    """
    session.pop('username', None)
    return redirect(url_for('login'))

# to make password not appear in data base
app.secret_key = os.getenv('SECRET_KEY', os.urandom(24))

if __name__ == '__main__':
    app.run(debug=True, port=5000)


