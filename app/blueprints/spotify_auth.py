from flask import Blueprint, request, redirect, url_for, session, current_app
import requests
import urllib.parse
import base64
import secrets
from datetime import datetime
from ..services.app_users_service import get_user_data, add_user, update_user
from ..models import User


spotify_auth = Blueprint("spotify_auth", __name__)


@spotify_auth.get("/spotify_login")
def spotify_login():

    client_id = current_app.config["CLIENT_ID"]
    scope = current_app.config["SCOPE"]
    redirect_uri = current_app.config["BASE_URL"] + "/callback"
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


@spotify_auth.get("/callback")
def callback():

    client_id = current_app.config["CLIENT_ID"]
    client_secret = current_app.config["CLIENT_SECRET"]
    redirect_uri = current_app.config["BASE_URL"] + "/callback"

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

    access_token_data = response.json()
    access_token_data["requested_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # TODO: emprolijar esta parte
    #--------------- Obtengo el email del usuario logeado y lo almaceno en la sesión:    
    url = "https://api.spotify.com/v1/me"

    headers = {
        "Authorization": f"Bearer {access_token_data['access_token']}",
        "Content-Type": "application/json"
    }
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        # La solicitud fue exitosa
        user_spotify_data = response.json()
        user_email = user_spotify_data["email"]
        user_data = get_user_data(user_email)

        if not user_data:
            new_user = User(email=user_email, access_token_data=access_token_data)
            add_user(new_user)

        # TODO: validar que se haya podido crear el usuario

        update_user(user_email, {"access_token_data":access_token_data})

        # Guardo el email del dueño de la cuenta en la sesion:
        session["owner_email"] = user_email
    
    else:
        #TODO: en caso de no poder obtener los datos del usuario y guardarlo en la sesion arrojar un error
        pass

    # ----------------------------------------------

    return redirect(url_for("owner_bp.account_settings"))


def refresh_access_token(owner_email, refresh_token):

    client_id = current_app.config["CLIENT_ID"]
    client_secret = current_app.config["CLIENT_SECRET"]

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

    access_token_data = response.json()
    access_token_data["refresh_token"] = refresh_token
    access_token_data["requested_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Actualización de los datos almacenados del token:
    update_user(owner_email, {"access_token_data":access_token_data})

    return access_token_data


def get_access_token(user_data, get_full_data=False):
    
    """
    Recibe los datos del usuario. Lee los datos del token de acceso de spotify y lo renueva si es necesario. Retorna el token de acceso.
    """

    access_token_data = user_data["access_token_data"]

    token_request_date = datetime.strptime(access_token_data["requested_at"], "%Y-%m-%d %H:%M:%S")
    token_time_since_requested = (datetime.now() - token_request_date).total_seconds()

    current_app.logger.info(f"-------------- Token time since requested: {token_time_since_requested}")

    if token_time_since_requested > access_token_data["expires_in"] - 30:
        access_token_data = refresh_access_token(user_data["email"], access_token_data["refresh_token"])  # Se renueva el token

    if get_full_data:
        # Se agrega el dato de cuanto tiempo resta para que venza el token:
        access_token_data["time_left_to_expire"] = access_token_data["expires_in"] - token_time_since_requested
        return access_token_data
    else:
        access_token = access_token_data["access_token"]
        return access_token

