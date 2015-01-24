import os
import logging

from os import path
from dropbox.client import DropboxOAuth2Flow
from flask import (Flask, request, url_for, redirect, jsonify, json, session,
                   render_template)

APP_SECRET_KEY = os.environ.get('APP_SECRET_KEY', 'testing')
DROPBOX_KEY = os.environ.get('DROPBOX_KEY')
DROPBOX_SECRET = os.environ.get('DROPBOX_SECRET')

if APP_SECRET_KEY == 'testing':
    logging.warning('Using weak app secret, set APP_SECRET_KEY.')

app = Flask(__name__)
app.secret_key = APP_SECRET_KEY

def url(path):
    base = request.url_root
    if base.find('localhost') == -1:
        base = base.replace("http://", "https://")
    return base + path

def get_dropbox_auth_flow(web_app_session):
    redirect_uri = url('auth-finish')
    return DropboxOAuth2Flow(DROPBOX_KEY, DROPBOX_SECRET, redirect_uri,
                                     session, "dropbox-auth-csrf-token")

@app.route("/auth-start", methods=['GET'])
def authorize_start():
    authorize_url = get_dropbox_auth_flow(session).start()
    return redirect(authorize_url, 302)

# URL handler for /dropbox-auth-finish
@app.route("/auth-finish", methods=['GET'])
def dropbox_auth_finish():
    try:
        access_token, user_id, url_state = \
            get_dropbox_auth_flow(session).finish(request.args)
        return render_template('auth_complete.html')
    except DropboxOAuth2Flow.BadRequestException, e:
        http_status(400)
    except DropboxOAuth2Flow.BadStateException, e:
        # Start the auth flow again.
        return redirect("/auth-start")
    except DropboxOAuth2Flow.CsrfException, e:
        http_status(403)
    except DropboxOAuth2Flow.NotApprovedException, e:
        return jsonify(message = ":(")
    except DropboxOAuth2Flow.ProviderException, e:
        logging.log("Auth error: %s" % (e,))
        return render_template('auth_error.html'), 403

@app.route("/debug")
def debug():
    return "%r" % request

def err(msg):
    return jsonify(status= {
        'success': False,
        'message': msg
    })

# Stolen from wowhack/plautocompleter
@app.after_request
def add_header(response):

    # These headers should be enough to disable caching across browsers
    # according to http://stackoverflow.com/a/2068407/98057
    response.headers['Pragma'] = 'no-cache' # HTTP 1.0
    response.headers['Expires'] = '0' # Proxies
    # HTTP 1.1
    response.cache_control.no_cache = True
    response.cache_control.no_store = True
    response.cache_control.must_revalidate = True
    response.cache_control.proxy_revalidate = True

    # Cross domain requests
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Max-Age'] = '0'

    return response

@app.errorhandler(500)
def internal_error(error):
    return err("Unexpected error '{}'".format(error.message))

if __name__ == "__main__":
    app.run()
