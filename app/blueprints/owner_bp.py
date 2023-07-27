from flask import Blueprint, render_template, current_app, url_for, session, send_file, request, jsonify
from itsdangerous import URLSafeSerializer
import json
from ..services.spotify_user_account_service import get_user_playlists, get_user_profile
from ..services.spotify_user_playback_service import get_available_devices
from ..services.rokolify_users_service import get_user_data, update_guest_permission, update_playlists_access_settings, update_user
from ..blueprints.spotify_auth import get_access_token
from ..utilities import generate_qr_img
from ..validators import host_session_required, user_has_linked_spotify_account


owner_bp = Blueprint("owner_bp", __name__)


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

    guest_url = generate_guest_url(owner_email)
    
    playlists_amount_to_show = 20
    playlists_succes, playlists_response = get_user_playlists(spotify_access_token, limit=playlists_amount_to_show)
    owner_playlists = playlists_response if playlists_succes else []

    devices_succes, devices_response = get_available_devices(spotify_access_token)
    available_devices = devices_response if devices_succes else None

    user_data = get_user_data(owner_email)
    guest_permissions = user_data["guest_settings"]["guest_permissions"]
    playlists_access_settings = user_data["guest_settings"]["playlists_settings"]
    playlists_settings = json.dumps(playlists_access_settings)

    context = {
        "guest_url": guest_url,
        "get_qr_url": url_for("owner_bp.get_qr"),
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
        "playlists_settings": playlists_settings,
        "playlists_amount_to_show": playlists_amount_to_show
    }

    return render_template("owner_settings_templates/owner_settings_for_guests.html", **context)


@owner_bp.get("/owner/automate_player")
@host_session_required
def automate_player():
    context = {
    }

    return render_template("owner_settings_templates/owner_automate_player.html", **context)


@owner_bp.get("/owner/get_qr")
@host_session_required
def get_qr():

    guest_url = request.args.get("guest_url")
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


    return {"message": "La operación se realizó correctamente"}


@owner_bp.put("/owner/api/playlists_settings")
@host_session_required
def update_playlists_settings():

    owner_email = session["host_session"]["user_email"]
    request_body = request.json

    # ------------ Validaciones de los datos enviados:
    if not request_body or type(request_body) != dict:
        return jsonify({"success": False, "message": "Acción rechazada", "status_code": 403}), 403

    # ------------ Validaciones de los datos enviados:

    # Se pasaron las validaciones:
    new_settings = request_body

    updated_settings = update_playlists_access_settings(owner_email, new_settings)

    return jsonify(updated_settings)


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
        return {"success": False, "message":"Error al obtener las playlists"}


@owner_bp.get("/owner/api/unlink_spotify_account")
@host_session_required
def unlink_spotify_account():

    owner_email = session["host_session"]["user_email"]
    update_user(owner_email, {"spotify_access_token_data": {}})

    return jsonify({"success": True, "status_code": 200})


def generate_guest_url(owner_email):

    serializer = URLSafeSerializer(current_app.secret_key)
    data = {"host_email": owner_email}
    token = serializer.dumps(data) 
    BASE_URL = current_app.config["BASE_URL"]
    
    guest_url = f"{BASE_URL}/guest/gateway/{token}"

    return guest_url
