from flask import Flask, redirect, url_for, render_template, session
from flask_oauthlib.client import OAuth

app = Flask(__name__)
app.secret_key = 'your_secret_key'

oauth = OAuth(app)

facebook = oauth.remote_app(
    'facebook',
    consumer_key='YOUR_FACEBOOK_APP_ID',
    consumer_secret='YOUR_FACEBOOK_APP_SECRET',
    request_token_params={'scope': 'email'},
    base_url='https://graph.facebook.com',
    request_token_url=None,
    access_token_url='/oauth/access_token',
    authorize_url='https://www.facebook.com/dialog/oauth'
)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    callback_url = url_for('facebook_authorized', _external=True)
    return facebook.authorize(callback=callback_url)

@app.route('/logout')
def logout():
    session.pop('facebook_token', None)
    return redirect(url_for('index'))

@app.route('/facebook-authorized')
def facebook_authorized():
    resp = facebook.authorized_response()
    if resp is None:
        return 'Access denied: reason={0} error={1}'.format(
            request.args['error_reason'],
            request.args['error_description']
        )
    session['facebook_token'] = (resp['access_token'], '')
    return redirect(url_for('admin'))

@facebook.tokengetter
def get_facebook_oauth_token():
    return session.get('facebook_token')

@app.route('/admin')
def admin():
    if 'facebook_token' in session:
        return render_template('admin.html')
    return redirect(url_for('login'))

@app.route('/messages/<page_id>')
def messages(page_id):
    if 'facebook_token' in session:
        graph_api_url = f"/{page_id}/feed?fields=message"
        resp = facebook.get(graph_api_url)
        if resp.status != 200:
            return f'Error accessing Facebook Graph API: {resp.data}'
        messages = resp.data['data']
        return render_template('messages.html', messages=messages)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run()
