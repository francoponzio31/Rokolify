from flask import Blueprint, request, redirect, url_for, session, current_app, jsonify
import requests
import urllib.parse
import base64
import secrets
from datetime import datetime
from ..services.rokolify_users_service import update_user
from ..validators import host_session_required


spotify_auth = Blueprint("spotify_auth", __name__)


@spotify_auth.get("/spotify_login")
@host_session_required
def spotify_login():

    client_id = current_app.config["SPOTIFY_CLIENT_ID"]
    scope = current_app.config["SPOTIFY_SCOPE"]
    redirect_uri = current_app.config["BASE_URL"] + "/spotify_auth_callback"
    state = secrets.token_hex(16)

    query_params = {
        "response_type": "code",
        "client_id": client_id,
        "scope": scope,
        "redirect_uri": redirect_uri,
        "state": state
    }

    authorize_url = "https://accounts.spotify.com/authorize?" + urllib.parse.urlencode(query_params)

    return redirect(authorize_url)


@spotify_auth.get("/spotify_auth_callback")
@host_session_required
def spotify_auth_callback():

    client_id = current_app.config["SPOTIFY_CLIENT_ID"]
    client_secret = current_app.config["SPOTIFY_CLIENT_SECRET"]
    redirect_uri = current_app.config["BASE_URL"] + "/spotify_auth_callback"

    # Código de autorización obtenido luego de que el usuario se haya logeado:
    login_authorization_code = request.args.get("code")

    # Request Access Token:
    auth_str = f"{client_id}:{client_secret}"
    auth_b64 = base64.b64encode(auth_str.encode("ascii")).decode("ascii")
    headers = {
        "Authorization": f"Basic {auth_b64}"
    }
    data = {
        "code": login_authorization_code,
        "redirect_uri": redirect_uri,
        "grant_type": "authorization_code"
    }
    
    response = requests.post("https://accounts.spotify.com/api/token", headers=headers, data=data)

    # La solicitud fue exitosa
    if response.status_code == 200:
        spotify_access_token_data = response.json()
        spotify_access_token_data["requested_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
       
        user_email = session["host_session"]["user_email"]

        # Guardo los datos del token de acceso en la db:
        update_user(user_email, {"spotify_access_token_data":spotify_access_token_data})

    else:
        return jsonify({"success": False, "message": "Error linking with Spotify account", "status_code": response.status_code}), response.status_code

    # ----------------------------------------------

    return redirect(url_for("owner_bp.account_settings"))


def refresh_access_token(owner_email, refresh_token):

    client_id = current_app.config["SPOTIFY_CLIENT_ID"]
    client_secret = current_app.config["SPOTIFY_CLIENT_SECRET"]

    auth_str = f"{client_id}:{client_secret}"
    auth_b64 = base64.b64encode(auth_str.encode("ascii")).decode("ascii")
    headers = {
        "Authorization": f"Basic {auth_b64}"
    }
    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token
    }
    response = requests.post("https://accounts.spotify.com/api/token", headers=headers, data=data)

    spotify_access_token_data = response.json()
    spotify_access_token_data["refresh_token"] = refresh_token
    spotify_access_token_data["requested_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Actualización de los datos almacenados del token:
    update_user(owner_email, {"spotify_access_token_data":spotify_access_token_data})

    return spotify_access_token_data


def get_access_token(user_data, get_full_data=False):
    
    """
    Recibe los datos del usuario. Lee los datos del token de acceso de spotify y lo renueva si es necesario. Retorna el token de acceso.
    """

    spotify_access_token_data = user_data["spotify_access_token_data"]

    if not spotify_access_token_data:   # Si todavia no se enlazó una cuenta de Spotify
        return spotify_access_token_data

    token_request_date = datetime.strptime(spotify_access_token_data["requested_at"], "%Y-%m-%d %H:%M:%S")
    token_time_since_requested = (datetime.now() - token_request_date).total_seconds()

    current_app.logger.info(f"-------------- Token time since requested: {token_time_since_requested}")

    if token_time_since_requested > spotify_access_token_data["expires_in"] - 30:   # Si quedan menos de 30 seg para que se venza se renueva
        spotify_access_token_data = refresh_access_token(user_data["email"], spotify_access_token_data["refresh_token"])  # Se renueva el token

    if get_full_data:
        # Se agrega el dato de cuanto tiempo resta para que venza el token:
        spotify_access_token_data["time_left_to_expire"] = spotify_access_token_data["expires_in"] - token_time_since_requested
        return spotify_access_token_data
    else:
        return spotify_access_token_data["access_token"]
