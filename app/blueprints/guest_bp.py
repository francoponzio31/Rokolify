from flask import Blueprint, render_template, request, current_app, jsonify, session, redirect, url_for
from ..services.owner_account_service import get_user_playlists
from ..services.spotify_catalog_service import get_playlist, get_playlist_items, search_tracks_in_catalog, get_track, get_artist, check_if_track_is_in_playlist
from ..services.owner_playback_service import add_item_to_queue, get_user_queue, get_available_devices, skip_to_next, push_to_player
from ..services.rokolify_users_service import get_user_data, check_if_track_was_recently_added_by_guests, add_recently_added_track_by_guest
from ..blueprints.spotify_auth import get_access_token
from itsdangerous import URLSafeSerializer
from datetime import datetime
from urllib.parse import urlparse


guest_bp = Blueprint("guest_bp", __name__)


@guest_bp.get("/guest/gateway/<token>")
def guest_gateway(token):
    serializer = URLSafeSerializer(current_app.secret_key)
    data = serializer.loads(token)
    owner_email = data["owner_email"]
    # Se añade el identificador de la cuenta huesped a la sesion:
    session["owner_email"] = owner_email
    session.permanent = True

    return redirect(url_for("guest_bp.show_allowed_playlists"))


@guest_bp.get("/guest/allowed_playlists")
def show_allowed_playlists():

    #? Validaciones:
    owner_email = session.get("owner_email")
    user_data = get_user_data(owner_email)
    
    succes, allowed_playlists, next_playlists_url = get_allowed_playlists(user_data, limit=50)
    
    guest_permissions = user_data["guest_settings"]["guest_permissions"]
    free_mode = guest_permissions["free_mode"]
    owner_playlists_access = guest_permissions["owner_playlists_access"]

    # Se valida si está habilitado el recurso:
    if not owner_playlists_access or not allowed_playlists or not succes:
        if free_mode:
            return redirect(url_for("guest_bp.guest_search_page"))
        else:
            return render_template("guest_templates/guest_no_resources_allowed.html")


    context = {
        "allowed_playlists": allowed_playlists,
        "free_mode": free_mode,
        "owner_playlists_access": owner_playlists_access,
        "next_playlists_url": next_playlists_url
    }

    return render_template("guest_templates/guest_allowed_playlists_view.html", **context)


@guest_bp.get("/guest/playlist/<playlist_id>")
def show_playlist_items(playlist_id):

    #? Validaciones:
    owner_email = session.get("owner_email")
    user_data = get_user_data(owner_email)
    access_token = get_access_token(user_data)

    guest_permissions = user_data["guest_settings"]["guest_permissions"]
    free_mode = guest_permissions["free_mode"]
    owner_playlists_access = guest_permissions["owner_playlists_access"]

    # Se valida si está habilitado el recurso:
    if owner_playlists_access:
        # TODO: cuar el playlist_id para validar que la playlist este entre las habilitadas
        pass
    else:
        if free_mode:
            return redirect(url_for("guest_bp.guest_search_page"))
        else:
            return render_template("guest_templates/guest_no_resources_allowed.html")

    #? Datos de la playlist:
    success, response = get_playlist(access_token, playlist_id)

    playlist_name = response["name"] if success else []
    playlist_items = response["tracks"]["items"] if success else []
    next_tracks_url = response["tracks"]["next"] if success else ""

    context = {
        "playlist_name": playlist_name,
        "playlist_items": playlist_items,
        "next_tracks_url": next_tracks_url
    }

    return render_template("guest_templates/guest_playlist_view.html", **context)


@guest_bp.get("/guest/search_track")
def guest_search_page():

    owner_email = session.get("owner_email")
    user_data = get_user_data(owner_email)
    guest_permissions = user_data["guest_settings"]["guest_permissions"]
    free_mode = guest_permissions["free_mode"]
    owner_playlists_access = guest_permissions["owner_playlists_access"]

    # Se valida si está habilitado el recurso:
    if not free_mode:
        if owner_playlists_access:
            return redirect(url_for("guest_bp.show_allowed_playlists"))
        else:
            return render_template("guest_templates/guest_no_resources_allowed.html")

    context = {
        "free_mode": free_mode,
        "owner_playlists_access": owner_playlists_access,
    }

    return render_template("guest_templates/guest_search_page.html", **context)


@guest_bp.post("/guest/api/queue")
def add_item_to_owner_queue():

    request_body = request.json

    # Track:
    track_uri = request_body["track_uri"]

    # User data:
    owner_email = session.get("owner_email")
    user_data = get_user_data(owner_email)
    access_token = get_access_token(user_data)

    #? Validaciones -------------------------------------------------------------------------------
    guest_permissions = user_data["guest_settings"]["guest_permissions"]
    allow_guest_access = guest_permissions["allow_guest_access"]

    # Se valida que la petición venga de alguno de los endpoints habilitados:
    allowed_referrer_endpoints = [current_app.config["BASE_URL"] + "/guest/playlist/", current_app.config["BASE_URL"] + "/guest/search_track"]
    if not any(request.referrer.startswith(allowed_endpoint) for allowed_endpoint in allowed_referrer_endpoints):
        return jsonify({"success": False, "message": "Petición inválida", "status_code": 403})
    
    if allow_guest_access is False:
        return jsonify({"success": False, "message": "La intervención de invitados ha sido deshabilitada", "status_code": 403})

    if check_if_track_was_recently_added_by_guests(user_data, track_uri) is True:
        return jsonify({"success": False, "message": "La canción ya ha sido agregada a la cola recientemente, prueba agregar otra canción", "status_code": 403})
    
    # Si la petición se hace desde dentro de la vista de una playlist:
    if request.referrer.startswith(current_app.config["BASE_URL"] + "/guest/playlist/"):
        playlist_id = urlparse(request.referrer).path.split('/')[-1]
        playlist_track_index = request_body["playlist_track_index"]
        track_validation = check_if_track_is_in_playlist(access_token, track_uri, playlist_id, playlist_track_index)
        if not track_validation:
            return {"success": False, "message": "La canción que se intenta agregar no se encuentra en la playlist"}
    
    #TODO: implementar un tiempo de retardo para que un mismo usuario pueda añadir otra cancion, para que no abusen del sistema

    #TODO: implementar validacion de que el dueño de la cuenta este logueado

    #? Se agrega la canción a la cola ----------------------------------------------------------------

    # Se intenta añadir la canción a la cola del reproductor activo:
    success, response = add_item_to_queue(access_token, track_uri)
    if success:
        add_recently_added_track_by_guest(user_data, track_uri)  # Se actualiza el registro de canciones agregadas recientemente por invitados
        return jsonify({"success":True, "message": "Canción agregada a la cola", "status_code": 200})


    # Si no se pudo añadir la canción a un dispositivo activo se intenta agregar la canción a alguno de los dispositivos disponibles y volverlo uno activo:
    if response["status_code"] == 404:  # Error provocado por no encontrar dispositivos activos

        # Obtengo los dispositivos disponibles:
        get_devices_succes, available_devices = get_available_devices(access_token)

        if not get_devices_succes:
            return jsonify({"success": False, "message": "Error al obtener dispositivos disponibles", "status_code": available_devices["status_code"]})
        if not available_devices:
            return jsonify({"success": False, "message": "No se encontraron dispositivos disponibles", "status_code": 404})

        # Primer dispositivo disponible:
        target_device_id = available_devices[0]["id"]

        try:
            # Se intenta agregar a la cola y saltear a la siguiente para reproducir la canción agregada:
            add_to_queue_succes, _ = add_item_to_queue(access_token, track_uri, device_id=target_device_id)
            if not add_to_queue_succes:
                raise Exception("Error al agregar el item a la cola")

            skip_succes, _ = skip_to_next(access_token, device_id=target_device_id)
            if not skip_succes:
                raise Exception("Error al pasar de canción")
        
        except:
            # Si no se logra agregar a la cola y saltear se fuerza la cancion al reproductor:
            push_success, push_response = push_to_player(access_token, "track", track_uri, device_id=target_device_id)
            if not push_success:
                return jsonify({"success": False, "message": "No se puede reproducir la canción", "status_code": push_response["status_code"]})

        add_recently_added_track_by_guest(user_data, track_uri)    # Se actualiza el registro de canciones agregadas recientemente por invitados
        return jsonify({"success": True, "message": "La canción se reproducirá a continuación", "status_code": 200})
                

    # Si nada funciona se devuelve el siguiente mensaje de error:
    return jsonify({"success": False, "message": "No se ha podido agregar la canción a la cola", "status_code": response["status_code"]})


@guest_bp.get("/guest/api/queue")
def get_owner_queue():

    # User data:
    owner_email = session.get("owner_email")
    user_data = get_user_data(owner_email)
    access_token = get_access_token(user_data)
    
    success, response = get_user_queue(access_token)

    if success:
        response.update({"success": True, "status_code": 200})
        return jsonify(response)
    
    else:
        return jsonify({"success": False, "message":"Error al obtener la cola de reproducción", "status_code": response["status_code"]})


@guest_bp.get("/guest/api/track/<string:track_id>")
def get_track_data(track_id):

    # User data:
    owner_email = session.get("owner_email")
    user_data = get_user_data(owner_email)
    access_token = get_access_token(user_data)

    track_success, track_response = get_track(access_token, track_id)
    if not track_success:
        return jsonify({"success": False, "message":"Error al obtener los datos de la canción", "status_code": track_response["status_code"]})
    
    #? Parseo de los datos de la canción:
    track_data = {}
    track_data["name"] = track_response["name"]
    track_data["album_name"] = track_response["album"]["name"]
    track_data["album_img_url"] = track_response["album"]["images"][0]["url"] if track_response["album"]["images"] else ""
    track_data["album_spotify_url"] = track_response["album"]["external_urls"]["spotify"]

    # Date format:
    if track_response["album"]["release_date_precision"] == "day":  # Day presicion format: 1979-03-29 
        track_data["album_release_date"] = datetime.strptime(track_response["album"]["release_date"], "%Y-%m-%d").strftime("%d/%m/%Y")
    elif track_response["album"]["release_date_precision"] == "month":  # Month presicion format: 1967-09
        track_data["album_release_date"] = datetime.strptime(track_response["album"]["release_date"], "%Y-%m").strftime("%m/%Y")
    else:  # Year presicion format: 1967
        track_data["album_release_date"] = track_response["album"]["release_date"]

    # Duration format:
    total_seconds = track_response["duration_ms"] // 1000
    track_data["duration"] = "{}:{:02d}".format(total_seconds // 60, total_seconds % 60)

    track_data["spotify_url"] = track_response["external_urls"]["spotify"]
    track_data["preview_url"] = track_response["preview_url"]

    track_data["artists"] = []
    for artist in track_response["artists"]:
        artist_success, artist_response = get_artist(access_token, artist["id"])
        if not artist_success:
            continue
        
        track_data["artists"].append({
            "name": artist_response["name"],
            "img_url": artist_response["images"][0]["url"] if artist_response["images"] else "",
            "spotify_url": artist_response["external_urls"]["spotify"]
        })

    track_data.update({"success": True, "status_code": 200})
    return jsonify(track_data)


@guest_bp.get("/guest/api/search_in_catalog/<string:search>")
def search_in_catalog(search):

    # User data:
    owner_email = session.get("owner_email")
    user_data = get_user_data(owner_email)
    access_token = get_access_token(user_data)
    
    success, response = search_tracks_in_catalog(access_token, search)

    if success:
        response.update({"success": True, "status_code": 200})
        return jsonify(response)
    else:
        return jsonify({"success": False, "message":"Error al realizar la busqueda", "status_code": response["status_code"]})


@guest_bp.get("/guest/api/get_playlist_items/<string:playlist_id>/<int:offset>/<int:limit>")
def get_more_playlist_items(playlist_id, offset, limit):
    
    # User data:
    owner_email = session.get("owner_email")
    user_data = get_user_data(owner_email)
    access_token = get_access_token(user_data)

    success, response = get_playlist_items(access_token, playlist_id, offset=offset, limit=limit)

    if success:
        response.update({"success": True, "status_code": 200})
        return jsonify(response)
    else:
        return jsonify({"success": False, "message":"Error al obtener las canciones", "status_code": response["status_code"]})


@guest_bp.get("/guest/api/get_playlists/<int:offset>/<int:limit>")
def get_more_playlists(offset, limit):
    
    owner_email = session.get("owner_email")
    user_data = get_user_data(owner_email)
    success, allowed_playlists, next_playlists_url = get_allowed_playlists(user_data, offset=offset, limit=limit)

    if success:
        return jsonify({"success": True, "status_code": 200, "playlists": allowed_playlists, "next": next_playlists_url})
    else:
        return jsonify({"success": False, "message":"Error al obtener las playlists"})


def get_allowed_playlists(user_data, offset=0, limit=20):

    access_token = get_access_token(user_data)

    success, response = get_user_playlists(access_token, offset=offset, limit=limit)
    owner_playlists = response["items"] if success else []
    next_playlists_url = response["next"] if success else ""

    playlists_access_settings = user_data["guest_settings"]["playlists_settings"]

    allowed_playlists = []
    for playlist in owner_playlists:

        if playlist["id"] in playlists_access_settings:
            if playlists_access_settings[playlist["id"]].get("allowed") is False:
               continue
            else:
                allowed_playlists.append(playlist)

        else:
            allowed_playlists.append(playlist)

    return success, allowed_playlists, next_playlists_url
