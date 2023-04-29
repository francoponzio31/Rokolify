from flask import Blueprint, render_template, current_app, url_for, session, send_file, request, Response, jsonify
from itsdangerous import URLSafeSerializer
import json
from ..services.owner_account_service import get_user_playlists, get_user_profile
from ..services.owner_playback_service import get_available_devices
from ..services.app_users_service import get_user_data, update_guest_permission, update_playlists_access_settings
from ..blueprints.spotify_auth import get_access_token
from ..utilities import generate_qr_img


owner_bp = Blueprint("owner_bp", __name__)


@owner_bp.get("/owner/account_settings")
def account_settings():

    # User data:
    owner_email = session.get("owner_email")
    user_data = get_user_data(owner_email)
    access_token = get_access_token(user_data)

    profile_succes, profile_response = get_user_profile(access_token)
    spotify_profile = profile_response if profile_succes else {}
    
    devices_succes, devices_response = get_available_devices(access_token)
    available_devices = devices_response if devices_succes else None
    active_devices = [device for device in available_devices if device["is_active"]]

    context = {
        "current_page": "account_settings",
        "available_devices_existence": bool(available_devices),
        "spotify_profile": spotify_profile,
        "available_devices": available_devices,
        "active_device": active_devices[0] if active_devices else None
    }

    return render_template("owner_settings_templates/owner_account_settings.html", **context)


@owner_bp.get("/owner/guest_settings")
def owner_settings_for_guests():

    # User data:
    owner_email = session.get("owner_email")
    user_data = get_user_data(owner_email)
    access_token = get_access_token(user_data)

    guest_url = generate_guest_url(owner_email)
    
    playlists_amount_to_show = 20
    # TODO: manejar error si no se encuentra data
    playlists_succes, playlists_response = get_user_playlists(access_token, limit=playlists_amount_to_show)
    owner_playlists = playlists_response if playlists_succes else []

    # TODO: manejar error si no se encuentra data
    devices_succes, devices_response = get_available_devices(access_token)
    available_devices = devices_response if devices_succes else None

    # TODO: manejar error si no se encuentra data
    user_data = get_user_data(owner_email)
    guest_permissions = user_data["guest_settings"]["guest_permissions"]
    playlists_access_settings = user_data["guest_settings"]["playlists_settings"]
    playlists_settings = json.dumps(playlists_access_settings)

    context = {
        "current_page": "settings_for_guests",
        "guest_url": guest_url,
        "get_qr_url": url_for("owner_bp.get_qr"),
        "owner_playlists": owner_playlists,
        "available_devices_existence": bool(available_devices),

        # User guest settings:
        "allow_guest_access": guest_permissions["allow_guest_access"],
        "free_mode": guest_permissions["free_mode"],
        "owner_playlists_access": guest_permissions["owner_playlists_access"],

        # Playlist settings:
        "playlists_settings": playlists_settings,
        "playlists_amount_to_show": playlists_amount_to_show
    }

    return render_template("owner_settings_templates/owner_settings_for_guests.html", **context)


@owner_bp.get("/owner/automate_player")
def automate_player():
    context = {
        "current_page": "automate_player",
    }

    return render_template("owner_settings_templates/owner_automate_player.html", **context)


@owner_bp.get("/owner/get_qr")
def get_qr():

    guest_url = request.args.get("guest_url")
    qr_img = generate_qr_img(guest_url)
    
    return send_file(qr_img, mimetype="image/png", download_name="qr_code.png", as_attachment=True)


@owner_bp.put("/owner/api/guest_permissions")
def update_guest_permissions():

    owner_email = session.get("owner_email")
    request_body = request.json

    if request_body.get("permission") and isinstance(request_body.get("value"), bool):

        #TODO: agregar una clave para el usuario en el token de la sesion y en el documento en mongo y validarla antes de actualizar el documento
        if request_body["permission"] == "guest-access":
            update_guest_permission(owner_email, "allow_guest_access", request_body["value"])
        elif request_body["permission"] == "free-mode":
            update_guest_permission(owner_email, "free_mode", request_body["value"])
        elif request_body["permission"] == "playlist-access":
            update_guest_permission(owner_email, "owner_playlists_access", request_body["value"])

    else:
        # TODO: retornar mensaje de error  al actualizar los ajustes, codigo de estatus que relfeje un error
        # return Response("hubo un error", status=400)
        pass

    return {"message": "La operación se realizó correctamente"}


@owner_bp.put("/owner/api/playlists_settings")
def update_playlists_settings():

    owner_email = session.get("owner_email")
    request_body = request.json

    # ------------ Validaciones de los datos enviados:
    # TODO: validar mejor los datos enviados, validar que la id de la playlist este entre las las playlists del usuario (get_user_Playlists) y los tipos de datos sean correctos 
    if not request_body or type(request_body) != dict:
        # TODO: retornar mensaje de error  al actualizar los ajustes, codigo de estatus que relfeje un error
        # return Response("hubo un error", status=400)
        pass

    # ------------ Validaciones de los datos enviados:

    # Se pasaron las validaciones:
    new_settings = request_body

    updated_settings = update_playlists_access_settings(owner_email, new_settings)

    return jsonify(updated_settings)


@owner_bp.get("/owner/api/get_playlists/<int:offset>/<int:limit>")
def get_more_playlists(offset, limit):

    # User data:
    owner_email = session.get("owner_email")
    user_data = get_user_data(owner_email)
    access_token = get_access_token(user_data)

    success, allowed_playlists = get_user_playlists(access_token, offset=offset, limit=limit)

    if success:
        return jsonify({"success": True, "status_code": 200, "playlists": allowed_playlists})
    else:
        return {"success": False, "message":"Error al obtener las playlists"}


def generate_guest_url(owner_email):

    serializer = URLSafeSerializer(current_app.secret_key)
    data = {"owner_email": owner_email}
    token = serializer.dumps(data) 
    BASE_URL = current_app.config["BASE_URL"]
    
    guest_url = f"{BASE_URL}/guest/gateway/{token}"

    return guest_url
