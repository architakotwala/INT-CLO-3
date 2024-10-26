from flask import Flask, redirect, url_for, session
from flask_dance.contrib.github import make_github_blueprint, github
import os

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'  # Allow insecure HTTP for development

app = Flask(__name__)

# Set the secret key for session management and token security
app.secret_key = os.environ.get('SECRET_KEY', os.urandom(24))

# Set your GitHub OAuth credentials (use environment variables in production)
app.config['GITHUB_OAUTH_CLIENT_ID'] = os.environ.get('GITHUB_OAUTH_CLIENT_ID', 'Ov23liylvppNcTNjvbjr')
app.config['GITHUB_OAUTH_CLIENT_SECRET'] = os.environ.get('GITHUB_OAUTH_CLIENT_SECRET', 'ca28b111f4272524fbf8e0d1259215dd5fb92479')

# Enable OAuth integration with GitHub
github_blueprint = make_github_blueprint(
    client_id=app.config['GITHUB_OAUTH_CLIENT_ID'],
    client_secret=app.config['GITHUB_OAUTH_CLIENT_SECRET'],
)

# Register the GitHub blueprint with the app
app.register_blueprint(github_blueprint, url_prefix="/login")

# Route for the homepage
@app.route('/')
def index():
    if not github.authorized:
        return redirect(url_for('github.login'))
    account_info = github.get('/user')
    if account_info.ok:
        account_data = account_info.json()
        return f'You are logged in as {account_data["login"]}!'
    return 'Request failed!'

# Route to handle user logout
@app.route('/logout')
def logout():
    token = github_blueprint.token["access_token"]
    github_blueprint.session.delete(f'https://github.com/settings/connections/applications/{token}')
    del github_blueprint.token  # Clears the token
    return redirect(url_for('index'))

# Entry point to run the Flask app
if __name__ == '__main__':
    app.run(debug=True)

