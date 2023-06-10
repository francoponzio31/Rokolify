from flask import session, request, current_app, redirect, jsonify, url_for, render_template
from app import create_app
from app.blueprints.spotify_auth import get_access_token
import requests 
from app.services.rokolify_users_service import get_user_data
from app.validators import login_required


app = create_app()

@app.get("/")
def index():
    # Se chequea que el usuario este logueado
    if session.get("owner_email"):
        return redirect(url_for("owner_bp.account_settings"))
    else:
        return redirect(url_for("login"))


@app.get("/login")
def login():
    return render_template("login_templates/rokolify_login.html")


@app.get("/logout")
@login_required
def logout():
    session.clear()
    return redirect(url_for("login"))


#? De aca para abajo endpoints de testing
@app.get("/token")
def token():
    return jsonify(get_access_token(get_full_data=True))


# @app.get("/test")
# def queue():

#     # User data:
#     owner_email = session.get("owner_email")
#     user_data = get_user_data(owner_email)
#     spotify_access_token = get_access_token(user_data)

#     url = f"https://api.spotify.com/v1/me/player"

#     headers = {
#         "Authorization": f"Bearer {spotify_access_token}",
#         "Content-Type": "application/json"
#     }

#     response = requests.get(url, headers=headers)
   
#     return jsonify(response.json())



if __name__ == "__main__":
    app.run(port=8888)
