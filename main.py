from flask import session, request, current_app, redirect, jsonify, url_for, render_template
from app import create_app
from app.blueprints.spotify_auth import get_access_token
import requests 
from app.services.rokolify_users_service import get_user_data


app = create_app()


@app.before_request 
def before_request_callback(): 
    # TODO: borrar, temporal
    # current_app.logger.info(request.endpoint)

    if request.endpoint not in ["spotify_auth.spotify_login", "spotify_auth.callback", "guest_bp.guest_gateway", "index"]:
        if not session.get("owner_email"):
            return render_template("session_expired.html")


@app.get("/")
def index():
    # Chequear que el token siga siendo valido, que el usuario siga logueado en spotify
    if session.get("owner_email"):
        return redirect(url_for("owner_bp.account_settings"))
    else:
        return redirect(url_for("spotify_auth.spotify_login"))


@app.get("/login")
def login():
    
    context = {
        "google_client_id": current_app.config["GOOGLE_CLIENT_ID"]
    }

    return render_template("login_templates/rokolify_login.html", **context)


@app.get("/token")
def token():
    return jsonify(get_access_token(get_full_data=True))


@app.get("/test")
def queue():

    # User data:
    owner_email = session.get("owner_email")
    user_data = get_user_data(owner_email)
    access_token = get_access_token(user_data)

    url = f"https://api.spotify.com/v1/me/player"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    response = requests.get(url, headers=headers)
   
    return jsonify(response.json())



if __name__ == "__main__":
    app.run( port=8888)
