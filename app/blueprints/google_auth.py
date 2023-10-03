from flask import Blueprint, request, redirect, url_for, session, current_app, jsonify, render_template
import requests
from ..services.rokolify_users_service import get_user_data, add_user, update_user
from ..models import User
from oauthlib.oauth2 import WebApplicationClient
import json


google_auth = Blueprint("google_auth", __name__)


@google_auth.get("/google_login")
def google_login():

    google_client  = WebApplicationClient(current_app.config["GOOGLE_CLIENT_ID"])

    request_uri = google_client.prepare_request_uri(
        uri="https://accounts.google.com/o/oauth2/auth",
        redirect_uri=current_app.config["BASE_URL"] + "/google_auth_callback",
        scope=["openid", "email", "profile"],
    )
    return redirect(request_uri)


@google_auth.get("/google_auth_callback")
def google_auth_callback():

    google_client  = WebApplicationClient(current_app.config["GOOGLE_CLIENT_ID"])

    # Code enviado en el callback a intercambiar por tokens:
    code = request.args.get("code")

    # Preparo y envio una solicitud para obtener tokens:
    token_url, headers, body = google_client.prepare_token_request(
        token_url="https://oauth2.googleapis.com/token",
        authorization_response=request.url,
        redirect_url=current_app.config["BASE_URL"] + "/google_auth_callback",
        code=code
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(current_app.config["GOOGLE_CLIENT_ID"], current_app.config["GOOGLE_CLIENT_SECRET"]),
    )

    # Parseo los tokens:
    google_client.parse_request_body_response(json.dumps(token_response.json()))

    # Request para obtener la info del usuario:
    userinfo_endpoint = "https://openidconnect.googleapis.com/v1/userinfo"
    uri, headers, body = google_client.add_token(userinfo_endpoint)
    google_user_info_response = requests.get(uri, headers=headers, data=body)

    # Datos del usuario obtenidos exitosamente, se verifica si es una cuenta de gmail válida: 
    if google_user_info_response.status_code == 200 and google_user_info_response.json().get("email_verified"):

        # return jsonify(google_user_info)
        google_user_info = google_user_info_response.json()
        user_email = google_user_info["email"]

        # Se obtienen los datos de la cuenta del usuario 
        user_data = get_user_data(user_email)

        # Si no existe ningún usuario con ese email se crea uno nuevo:
        if not user_data:
            new_user = User(
                email=user_email,
                name=google_user_info["name"],
                given_name=google_user_info["given_name"],
                family_name=google_user_info["family_name"],
                profile_picture_url=google_user_info["picture"]
            )

            add_user(new_user)
        
        else: # Si ya existe actualizo sus datos por si cambiaron
            update_user(user_email, {
                "name": google_user_info["name"],
                "given_name": google_user_info["given_name"],
                "family_name": google_user_info["family_name"],
                "profile_picture": google_user_info["picture"]
            })

        # Se valida que se haya podido crear el usuario:
        if not get_user_data(user_email):
            return render_template("generic_page.html", content="<h1> Lo sentimos, se ha producido un error al registrar al usuario. Intentelo de nuevo.</h1>")

        # Guardo el email del usuario en la sesion:
        session["host_session"] = {
            "user_email": user_email
        }
        session.permanent = True

        return redirect(url_for("index"))

    else:
        return jsonify({"success": False, "message": "Error al ingresar con Google", "status_code": google_user_info_response.status_code}), google_user_info_response.status_code
