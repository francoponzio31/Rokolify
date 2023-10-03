from flask import Blueprint, render_template, current_app, url_for, session, send_file, request, jsonify
from itsdangerous import URLSafeSerializer
from ..services.spotify_user_account_service import get_user_playlists, get_user_profile
from ..services.spotify_user_playback_service import get_available_devices
from ..services.rokolify_users_service import get_user_data, update_guest_permission, set_allow_playlist_settings, delete_allow_playlist_condition, add_allow_playlist_condition, update_user, add_guest_access_link, delete_guest_access_link, clean_expired_access_links
from ..blueprints.spotify_auth import get_access_token
from ..utilities import generate_qr_img
from ..validators import host_session_required, user_has_linked_spotify_account
from datetime import datetime
import pytz


owner_bp = Blueprint("owner_bp", __name__)


@owner_bp.get("/owner/welcome")
@host_session_required
def welcome():

    # User data:
    owner_email = session["host_session"]["user_email"]
    user_data = get_user_data(owner_email)

    context = {
        "rokolify_profile": {
            "given_name": user_data["given_name"]
        }
    }

    return render_template("owner_settings_templates/owner_welcome.html", **context)


@owner_bp.get("/owner/account_settings")
@host_session_required
def account_settings():

    # User data:
    owner_email = session["host_session"]["user_email"]
    user_data = get_user_data(owner_email)
    spotify_access_token = get_access_token(user_data)

    profile_succes, profile_response = get_user_profile(spotify_access_token)
    spotify_profile = profile_response if profile_succes else {}
    
    devices_succes, devices_response = get_available_devices(spotify_access_token)
    available_devices = devices_response if devices_succes else []
    active_devices = [device for device in available_devices if device["is_active"]]

    context = {
        "rokolify_profile": {
            "email": user_data["email"],
            "name": user_data["name"],
            "profile_picture": user_data["profile_picture"]
        },
        "linked_spotify_account_validation": user_has_linked_spotify_account(user_data),
        "spotify_profile": spotify_profile,
        "available_devices_existence": bool(available_devices),
        "available_devices": available_devices,
        "active_device": active_devices[0] if active_devices else None
    }

    return render_template("owner_settings_templates/owner_account_settings.html", **context)


@owner_bp.get("/owner/guest_settings")
@host_session_required
def owner_settings_for_guests():

    # User data:
    owner_email = session["host_session"]["user_email"]
    user_data = get_user_data(owner_email)
    spotify_access_token = get_access_token(user_data)

    
    playlists_amount_to_show = 20
    playlists_succes, playlists_response = get_user_playlists(spotify_access_token, limit=playlists_amount_to_show)
    owner_playlists = playlists_response if playlists_succes else []

    devices_succes, devices_response = get_available_devices(spotify_access_token)
    available_devices = devices_response if devices_succes else None

    user_data = get_user_data(owner_email)
    guest_permissions = user_data["guest_settings"]["guest_permissions"]

    context = {
        "linked_spotify_account_validation": user_has_linked_spotify_account(user_data),
        "available_devices_existence": bool(available_devices),
        "owner_playlists": owner_playlists,

        # User guest settings:
        "allow_guest_access": guest_permissions["allow_guest_access"],
        "free_mode": guest_permissions["free_mode"],
        "owner_playlists_access": guest_permissions["owner_playlists_access"],
        "time_to_re_add_same_track": user_data["guest_settings"].get("time_to_re_add_same_track", 0),
        "cooldown_time_to_add": user_data["guest_settings"].get("cooldown_time_to_add", 0),

        # Playlist settings:
        "playlists_amount_to_show": playlists_amount_to_show
    }

    return render_template("owner_settings_templates/owner_settings_for_guests.html", **context)


@owner_bp.get("/owner/get_access_link_qr/<access_link_token>")
@host_session_required
def get_qr(access_link_token):

    BASE_URL = current_app.config["BASE_URL"]
    guest_url = f"{BASE_URL}/guest/gateway/{access_link_token}"
    qr_img = generate_qr_img(guest_url)
    
    return send_file(qr_img, mimetype="image/png", download_name="qr_code.png", as_attachment=True)


@owner_bp.put("/owner/api/guest_permissions")
@host_session_required
def update_guest_permissions():

    owner_email = session["host_session"]["user_email"]
    request_body = request.json

    if not request_body.get("permission"):
        return jsonify({"success": False, "message": "Permiso iválido", "status_code": 403})

    if request_body["permission"] == "guest-access" and isinstance(request_body.get("value"), bool):
        update_guest_permission(owner_email, "allow_guest_access", request_body["value"])

    elif request_body["permission"] == "free-mode" and isinstance(request_body.get("value"), bool):
        update_guest_permission(owner_email, "free_mode", request_body["value"])
    
    elif request_body["permission"] == "playlist-access" and isinstance(request_body.get("value"), bool):
        update_guest_permission(owner_email, "owner_playlists_access", request_body["value"])
    
    elif request_body["permission"] == "time_to_re_add_same_track" and isinstance(request_body.get("value"), int) and request_body["value"] >= 0:
        update_user(owner_email, {"guest_settings.time_to_re_add_same_track": request_body["value"]})

    elif request_body["permission"] == "cooldown_time_to_add" and isinstance(request_body.get("value"), int) and request_body["value"] >= 0:
        update_user(owner_email, {"guest_settings.cooldown_time_to_add": request_body["value"]})

    else:
        return jsonify({"success": False, "message": "Acción rechazada", "status_code": 403})

    return jsonify({"message": "La operación se realizó correctamente"})


@owner_bp.get("/owner/api/guest_access_links")
@host_session_required
def get_guest_access_links():

    owner_email = session["host_session"]["user_email"]

    clean_expired_access_links(owner_email)
    user_data = get_user_data(owner_email)
    
    playlists_access_settings = user_data["guest_access_links"]

    return jsonify(playlists_access_settings)


@owner_bp.post("/owner/api/guest_access_links")
@host_session_required
def add_access_link():

    import uuid

    request_body = request.json
    if not request_body or (type(request_body) != dict) or "new_access_link" not in request_body:
        return jsonify({"success": False, "message": "Acción rechazada", "status_code": 403}), 403

    owner_email = session["host_session"]["user_email"]
    received_link_data = request_body["new_access_link"]

    if not received_link_data["description"].strip():
        return jsonify({"success": False, "message": "Acción rechazada", "status_code": 403}), 403

    try:
        # Obtener la zona horaria del diccionario
        timezone = pytz.timezone(received_link_data["timezone"])
    except pytz.exceptions.UnknownTimeZoneError:
        # En caso de error al obtener la zona horaria, establecer la zona de Buenos Aires
        timezone = pytz.timezone("America/Buenos_Aires")
    # Obtener la hora actual en la zona horaria dada
    current_time = datetime.now(timezone)

    new_link = {
        "id": str(uuid.uuid4()),
        "host_email": owner_email,
        "description": received_link_data["description"],
        "created_on": current_time.strftime("%d/%m/%Y %H:%M"),
        "expiration_datetime": (
            datetime.strptime(received_link_data["expiration_datetime"], "%Y-%m-%dT%H:%M").strftime("%d/%m/%Y %H:%M")
            if received_link_data["expiration_datetime"] else None
        ),
        "timezone": received_link_data["timezone"],
    }
    new_link["token"] = _generate_access_link_token(new_link)
    
    add_guest_access_link(owner_email, new_link)

    return jsonify({"message": "La operación se realizó correctamente"})


@owner_bp.delete("/owner/api/guest_access_links")
@host_session_required
def delete_access_link():

    request_body = request.json
    if not request_body or (type(request_body) != dict) or "access_link_id" not in request_body:
        return jsonify({"success": False, "message": "Acción rechazada", "status_code": 403}), 403

    owner_email = session["host_session"]["user_email"]
    access_link_id = request_body["access_link_id"]
    delete_guest_access_link(owner_email, access_link_id)

    return jsonify({"message": "La operación se realizó correctamente"})


@owner_bp.get("/owner/api/playlists_settings")
@host_session_required
def get_playlists_settings():

    owner_email = session["host_session"]["user_email"]
    user_data = get_user_data(owner_email)
    playlists_access_settings = user_data["guest_settings"]["playlists_settings"]

    return jsonify(playlists_access_settings)


@owner_bp.put("/owner/api/set_allow_playlist_value/<string:playlist_id>")
@host_session_required
def set_allow_playlist_value(playlist_id):

    request_body = request.json
    if not request_body or (type(request_body) != dict) or "allow_value" not in request_body or not isinstance(request_body["allow_value"], bool):
        return jsonify({"success": False, "message": "Acción rechazada", "status_code": 403}), 403
    
    owner_email = session["host_session"]["user_email"]
    allow_value = request_body["allow_value"]
    set_allow_playlist_settings(owner_email, playlist_id, allow_value)

    return jsonify({"message": "La operación se realizó correctamente"})


@owner_bp.post("/owner/api/add_playlist_condition/<string:playlist_id>")
@host_session_required
def add_playlist_condition(playlist_id):

    import uuid

    request_body = request.json
    if not request_body or (type(request_body) != dict) or "new_permision" not in request_body:
        return jsonify({"success": False, "message": "Acción rechazada", "status_code": 403}), 403
    
    if not _time_interval_is_valid(request_body["new_permision"]["init_time"], request_body["new_permision"]["end_time"]):
        return jsonify({"success": False, "message": "Datos inválidos", "status_code": 403}), 403

    new_condition = {
        "id": str(uuid.uuid4()),
        "day": int(request_body["new_permision"]["day"]),
        "init_time": request_body["new_permision"]["init_time"],
        "end_time": request_body["new_permision"]["end_time"],
        "timezone": request_body["new_permision"]["timezone"],
    }
    
    owner_email = session["host_session"]["user_email"]
    add_allow_playlist_condition(owner_email, playlist_id, new_condition)

    return jsonify({"message": "La operación se realizó correctamente"})


@owner_bp.delete("/owner/api/delete_playlist_condition/<string:playlist_id>")
@host_session_required    
def delete_playlist_condition(playlist_id):

    request_body = request.json
    if not request_body or (type(request_body) != dict) or "condition_id" not in request_body:
        return jsonify({"success": False, "message": "Acción rechazada", "status_code": 403}), 403

    owner_email = session["host_session"]["user_email"]
    condition_id = request_body["condition_id"]
    delete_allow_playlist_condition(owner_email, playlist_id, condition_id)

    return jsonify({"message": "La operación se realizó correctamente"})


@owner_bp.get("/owner/api/get_playlists/<int:offset>/<int:limit>")
@host_session_required
def get_more_playlists(offset, limit):

    # User data:
    owner_email = session["host_session"]["user_email"]
    user_data = get_user_data(owner_email)
    spotify_access_token = get_access_token(user_data)

    success, allowed_playlists = get_user_playlists(spotify_access_token, offset=offset, limit=limit)

    if success:
        return jsonify({"success": True, "status_code": 200, "playlists": allowed_playlists})
    else:
        return jsonify({"success": False, "message":"Error al obtener las playlists"})


@owner_bp.get("/owner/api/unlink_spotify_account")
@host_session_required
def unlink_spotify_account():

    owner_email = session["host_session"]["user_email"]
    update_user(owner_email, {"spotify_access_token_data": {}})

    return jsonify({"success": True, "status_code": 200})


def _generate_access_link_token(access_link_data):
    serializer = URLSafeSerializer(current_app.secret_key)
    token = serializer.dumps(access_link_data) 

    return token


from datetime import time

def _time_interval_is_valid(init_time, end_time):
    # Se esperan horarios con el formato "HH:MM"

    init_hour, init_minutes = map(int, init_time.split(':'))
    end_hour, end_minutes = map(int, end_time.split(':'))

    # Convertir los horarios a objetos de tipo time
    init_time = time(init_hour, init_minutes)
    end_time = time(end_hour, end_minutes)

    # Comparar los horarios
    return init_time < end_time