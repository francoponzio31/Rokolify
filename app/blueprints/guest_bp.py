from flask import Blueprint, render_template, request, current_app, jsonify, session, redirect, url_for
from ..services.spotify_user_account_service import get_user_playlists, get_user_profile
from ..services.spotify_catalog_service import get_playlist, get_playlist_items, search_tracks_in_catalog, get_track, get_artist, check_if_playlist_is_in_user_playlists,  check_if_track_is_in_playlist
from ..services.spotify_user_playback_service import add_item_to_queue, get_user_queue, get_available_devices, skip_to_next, push_to_player
from ..services.rokolify_users_service import get_user_data, check_if_track_was_recently_added_by_guests, add_recently_added_track_by_guest, check_if_guest_is_allowed_to_add_to_queue, check_if_playlist_is_allowed_by_user, validate_access_link_existence, validate_access_link_expiration
from ..blueprints.spotify_auth import get_access_token
from ..validators import guest_session_required, owner_with_linked_spotify_account_validation, owner_with_guest_access_allowed_validation
from itsdangerous import URLSafeSerializer
import uuid
from datetime import datetime
from urllib.parse import urlparse


guest_bp = Blueprint("guest_bp", __name__)


@guest_bp.get("/guest/gateway/<token>")
def guest_gateway(token):
    serializer = URLSafeSerializer(current_app.secret_key)
    access_link_data = serializer.loads(token)
    host_email = access_link_data["host_email"]
    
    if (
        not validate_access_link_existence(host_email, access_link_data["id"])
        or not validate_access_link_expiration(access_link_data)
    ):
        return render_template("generic_page.html", title="Link de acceso inválido", content="<h1> El link para acceder a la sección de invitados no es válido. </h1>")

    # Se añade el identificador de la cuenta huesped a la sesion:
    session["guest_session"] = {
        "guest_id": str(uuid.uuid4()),
        "host_email": host_email
    }
    session.permanent = True

    return redirect(url_for("guest_bp.show_allowed_playlists"))


@guest_bp.get("/guest/allowed_playlists")
@guest_session_required
def show_allowed_playlists():

    #? Validaciones:
    host_email = session["guest_session"]["host_email"]
    host_user_data = get_user_data(host_email)
    
    # Validaciones sobre la cuenta del anfitrión:
    validation_response = owner_with_linked_spotify_account_validation(host_user_data)
    if validation_response:
        return validation_response

    validation_response = owner_with_guest_access_allowed_validation(host_user_data)
    if validation_response:
        return validation_response

    succes, allowed_playlists, next_playlists_url = _get_user_allowed_playlists(host_user_data, limit=50)
    
    guest_permissions = host_user_data["guest_settings"]["guest_permissions"]
    free_mode = guest_permissions["free_mode"]
    owner_playlists_access = guest_permissions["owner_playlists_access"]

    # Se valida si está habilitado el recurso:
    if not owner_playlists_access or not allowed_playlists or not succes:
        if free_mode:
            return redirect(url_for("guest_bp.guest_search_page"))
        else:
            return render_template("generic_page.html", title="Sin recursos disponibles", content="<h1> No hay recursos habilitados por el propietario de la cuenta... </h1>")

    context = {
        "allowed_playlists": allowed_playlists,
        "free_mode": free_mode,
        "owner_playlists_access": owner_playlists_access,
        "next_playlists_url": next_playlists_url
    }

    return render_template("guest_templates/guest_allowed_playlists_view.html", **context)


@guest_bp.get("/guest/playlist/<playlist_id>")
@guest_session_required
def show_playlist_items(playlist_id):

    #? Validaciones:
    host_email = session["guest_session"]["host_email"]
    host_user_data = get_user_data(host_email)
    spotify_access_token = get_access_token(host_user_data)

    # Validaciones sobre la cuenta del anfitrión:
    validation_response = owner_with_linked_spotify_account_validation(host_user_data)
    if validation_response:
        return validation_response

    validation_response = owner_with_guest_access_allowed_validation(host_user_data)
    if validation_response:
        return validation_response

    guest_permissions = host_user_data["guest_settings"]["guest_permissions"]
    free_mode = guest_permissions["free_mode"]
    owner_playlists_access = guest_permissions["owner_playlists_access"]

    # Se valida si está habilitado el recurso:
    if owner_playlists_access:
        # Se valida que la playlist este entre las habilitadas:
        profile_succes, profile_response = get_user_profile(spotify_access_token)
        spotify_user_id = profile_response["id"]
        if not (
            check_if_playlist_is_in_user_playlists(spotify_access_token, spotify_user_id, playlist_id) and check_if_playlist_is_allowed_by_user(host_user_data, playlist_id)
        ):
            return render_template("generic_page.html", content="<h1> Lo sentimos, la playlist no se encuentra disponible. </h1>")
    else:
        if free_mode:
            return redirect(url_for("guest_bp.guest_search_page"))
        else:
            return render_template("guest_templates/guest_no_resources_allowed.html")

    #? Datos de la playlist:
    success, response = get_playlist(spotify_access_token, playlist_id)

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
@guest_session_required
def guest_search_page():

    host_email = session["guest_session"]["host_email"]
    host_user_data = get_user_data(host_email)
    guest_permissions = host_user_data["guest_settings"]["guest_permissions"]
    free_mode = guest_permissions["free_mode"]
    owner_playlists_access = guest_permissions["owner_playlists_access"]

    # Validaciones sobre la cuenta del anfitrión:
    validation_response = owner_with_linked_spotify_account_validation(host_user_data)
    if validation_response:
        return validation_response

    validation_response = owner_with_guest_access_allowed_validation(host_user_data)
    if validation_response:
        return validation_response

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
@guest_session_required
def add_item_to_owner_queue():

    request_body = request.json

    # Track:
    track_uri = request_body["track_uri"]

    # User data:
    guest_id = session["guest_session"]["guest_id"]
    host_email = session["guest_session"]["host_email"]
    host_user_data = get_user_data(host_email)
    spotify_access_token = get_access_token(host_user_data)

    #? Validaciones -------------------------------------------------------------------------------

    # Se valida que la petición venga de alguno de los endpoints habilitados:
    allowed_referrer_endpoints = [current_app.config["BASE_URL"] + "/guest/playlist/", current_app.config["BASE_URL"] + "/guest/search_track"]  # Endpoints habilitados
    if not any(request.referrer.startswith(allowed_endpoint) for allowed_endpoint in allowed_referrer_endpoints):
        return jsonify({"success": False, "message": "Petición inválida", "status_code": 403})

    # Validaciones sobre la cuenta del anfitrión:
    validation_response = owner_with_linked_spotify_account_validation(host_user_data)
    if validation_response:
        return jsonify({"success": False, "message": "Se ha producido un error, el usuario anfitrión no tiene una cuenta de Spotify vinculada", "status_code": 403})

    validation_response = owner_with_guest_access_allowed_validation(host_user_data)
    if validation_response:
        return jsonify({"success": False, "message": "La intervención de invitados ha sido deshabilitada", "status_code": 403})
    
    # Se valida que la canción esta habilitada para agregar:
    if check_if_track_was_recently_added_by_guests(host_user_data, track_uri) is True:
        return jsonify({"success": False, "message": "La canción ya ha sido agregada a la cola recientemente, prueba agregar otra canción", "status_code": 403})
    
    # Se valida que el invitado pueda agregar una canción:
    if check_if_guest_is_allowed_to_add_to_queue(host_user_data, guest_id) is False:
        return jsonify({"success": False, "message": f"Debes esperar {host_user_data['guest_settings'].get('cooldown_time_to_add', 0)} segundos antes de agregar otra canción a la cola de reproducción", "status_code": 403})
    
    # Si la petición se hace desde dentro de la vista de una playlist:
    if request.referrer.startswith(current_app.config["BASE_URL"] + "/guest/playlist/"):
        playlist_id = urlparse(request.referrer).path.split('/')[-1]
        playlist_track_index = request_body["playlist_track_index"]
        track_validation = check_if_track_is_in_playlist(spotify_access_token, track_uri, playlist_id, playlist_track_index)    # Se valida que la canción a agregar pertenezca a la playlist
        if not track_validation:
            return jsonify({"success": False, "message": "La canción que se intenta agregar no se encuentra en la playlist", "status_code": 403})
    

    #? Se agrega la canción a la cola ----------------------------------------------------------------

    # Se intenta añadir la canción a la cola del reproductor activo:
    success, response = add_item_to_queue(spotify_access_token, track_uri)
    if success:
        add_recently_added_track_by_guest(host_user_data, guest_id, track_uri)  # Se actualiza el registro de canciones agregadas recientemente por invitados
        return jsonify({"success":True, "message": "Canción agregada a la cola", "status_code": 200})


    # Si no se pudo añadir la canción a un dispositivo activo se intenta agregar la canción a alguno de los dispositivos disponibles y volverlo uno activo:
    if response["status_code"] == 404:  # Error provocado por no encontrar dispositivos activos

        # Obtengo los dispositivos disponibles:
        get_devices_succes, available_devices = get_available_devices(spotify_access_token)

        if not get_devices_succes:
            return jsonify({"success": False, "message": "Error al obtener dispositivos disponibles", "status_code": available_devices["status_code"]})
        if not available_devices:
            return jsonify({"success": False, "message": "No se encontraron dispositivos disponibles", "status_code": 404})

        # Primer dispositivo disponible:
        target_device_id = available_devices[0]["id"]

        try:
            # Se intenta agregar a la cola y saltear a la siguiente para reproducir la canción agregada:
            add_to_queue_succes, _ = add_item_to_queue(spotify_access_token, track_uri, device_id=target_device_id)
            if not add_to_queue_succes:
                raise Exception("Error al agregar el item a la cola")

            skip_succes, _ = skip_to_next(spotify_access_token, device_id=target_device_id)
            if not skip_succes:
                raise Exception("Error al pasar de canción")
        
        except:
            # Si no se logra agregar a la cola y saltear se fuerza la cancion al reproductor:
            push_success, push_response = push_to_player(spotify_access_token, "track", track_uri, device_id=target_device_id)
            if not push_success:
                return jsonify({"success": False, "message": "No se puede reproducir la canción", "status_code": push_response["status_code"]})

        add_recently_added_track_by_guest(host_user_data, guest_id, track_uri)    # Se actualiza el registro de canciones agregadas recientemente por invitados
        return jsonify({"success": True, "message": "La canción se reproducirá a continuación", "status_code": 200})
                

    # Si nada funciona se devuelve el siguiente mensaje de error:
    return jsonify({"success": False, "message": "No se ha podido agregar la canción a la cola", "status_code": response["status_code"]})


@guest_bp.get("/guest/api/queue")
@guest_session_required
def get_owner_queue():

    # User data:
    host_email = session["guest_session"]["host_email"]
    host_user_data = get_user_data(host_email)
    spotify_access_token = get_access_token(host_user_data)

    # Validaciones sobre la cuenta del anfitrión:
    validation_response = owner_with_linked_spotify_account_validation(host_user_data)
    if validation_response:
        return jsonify({"success": False, "message": "Se ha producido un error, el usuario anfitrión no tiene una cuenta de Spotify vinculada", "status_code": 403})

    validation_response = owner_with_guest_access_allowed_validation(host_user_data)
    if validation_response:
        return jsonify({"success": False, "message": "Se ha producido un error, el usuario anfitrión ha deshabilitado la intervención de invitados", "status_code": 403})

    success, response = get_user_queue(spotify_access_token)

    if success:
        response.update({"success": True, "status_code": 200})
        return jsonify(response)
    
    else:
        return jsonify({"success": False, "message":"Error al obtener la cola de reproducción", "status_code": response["status_code"]})


@guest_bp.get("/guest/api/track/<string:track_id>")
@guest_session_required
def get_track_data(track_id):

    # User data:
    host_email = session["guest_session"]["host_email"]
    host_user_data = get_user_data(host_email)
    spotify_access_token = get_access_token(host_user_data)

    # Validaciones sobre la cuenta del anfitrión:
    validation_response = owner_with_linked_spotify_account_validation(host_user_data)
    if validation_response:
        return jsonify({"success": False, "message": "Se ha producido un error, el usuario anfitrión no tiene una cuenta de Spotify vinculada", "status_code": 403})

    validation_response = owner_with_guest_access_allowed_validation(host_user_data)
    if validation_response:
        return jsonify({"success": False, "message": "Se ha producido un error, el usuario anfitrión ha deshabilitado la intervención de invitados", "status_code": 403})

    track_success, track_response = get_track(spotify_access_token, track_id)
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
        artist_success, artist_response = get_artist(spotify_access_token, artist["id"])
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
@guest_session_required
def search_in_catalog(search):

    # User data:
    host_email = session["guest_session"]["host_email"]
    host_user_data = get_user_data(host_email)
    spotify_access_token = get_access_token(host_user_data)
    
    # Validaciones sobre la cuenta del anfitrión:
    validation_response = owner_with_linked_spotify_account_validation(host_user_data)
    if validation_response:
        return jsonify({"success": False, "message": "Se ha producido un error, el usuario anfitrión no tiene una cuenta de Spotify vinculada", "status_code": 403})

    validation_response = owner_with_guest_access_allowed_validation(host_user_data)
    if validation_response:
        return jsonify({"success": False, "message": "Se ha producido un error, el usuario anfitrión ha deshabilitado la intervención de invitados", "status_code": 403})

    success, response = search_tracks_in_catalog(spotify_access_token, search)

    if success:
        response.update({"success": True, "status_code": 200})
        return jsonify(response)
    else:
        return jsonify({"success": False, "message":"Error al realizar la busqueda", "status_code": response["status_code"]})


@guest_bp.get("/guest/api/get_playlist_items/<string:playlist_id>/<int:offset>/<int:limit>")
@guest_session_required
def get_more_playlist_items(playlist_id, offset, limit):
    
    # User data:
    host_email = session["guest_session"]["host_email"]
    host_user_data = get_user_data(host_email)
    spotify_access_token = get_access_token(host_user_data)

    # Validaciones sobre la cuenta del anfitrión:
    validation_response = owner_with_linked_spotify_account_validation(host_user_data)
    if validation_response:
        return jsonify({"success": False, "message": "Se ha producido un error, el usuario anfitrión no tiene una cuenta de Spotify vinculada", "status_code": 403})

    validation_response = owner_with_guest_access_allowed_validation(host_user_data)
    if validation_response:
        return jsonify({"success": False, "message": "Se ha producido un error, el usuario anfitrión ha deshabilitado la intervención de invitados", "status_code": 403})

    success, response = get_playlist_items(spotify_access_token, playlist_id, offset=offset, limit=limit)

    if success:
        response.update({"success": True, "status_code": 200})
        return jsonify(response)
    else:
        return jsonify({"success": False, "message":"Error al obtener las canciones", "status_code": response["status_code"]})


@guest_bp.get("/guest/api/get_playlists/<int:offset>/<int:limit>")
@guest_session_required
def get_more_playlists(offset, limit):
    
    host_email = session["guest_session"]["host_email"]
    host_user_data = get_user_data(host_email)

    # Validaciones sobre la cuenta del anfitrión:
    validation_response = owner_with_linked_spotify_account_validation(host_user_data)
    if validation_response:
        return jsonify({"success": False, "message": "Se ha producido un error, el usuario anfitrión no tiene una cuenta de Spotify vinculada", "status_code": 403})

    validation_response = owner_with_guest_access_allowed_validation(host_user_data)
    if validation_response:
        return jsonify({"success": False, "message": "Se ha producido un error, el usuario anfitrión ha deshabilitado la intervención de invitados", "status_code": 403})

    success, allowed_playlists, next_playlists_url = _get_user_allowed_playlists(host_user_data, offset=offset, limit=limit)

    if success:
        return jsonify({"success": True, "status_code": 200, "playlists": allowed_playlists, "next": next_playlists_url})
    else:
        return jsonify({"success": False, "message":"Error al obtener las playlists"})



def _get_user_allowed_playlists(user_data, offset=0, limit=20):

    spotify_access_token = get_access_token(user_data)

    success, response = get_user_playlists(spotify_access_token, offset=offset, limit=limit)
    owner_playlists = response["items"] if success else []
    next_playlists_url = response["next"] if success else ""

    # Se filtran las playlists del huesped que no esten habilitadas:
    allowed_playlists = []
    for playlist in owner_playlists:

        if check_if_playlist_is_allowed_by_user(user_data, playlist["id"]):
            allowed_playlists.append(playlist)

    return success, allowed_playlists, next_playlists_url
