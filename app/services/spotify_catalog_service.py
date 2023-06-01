import requests


"""
Este modulo contiene funciones que permiten obtener información del cátalogo de spotify.
"""


def get_playlist(spotify_access_token, playlist_id):

    """
    Retorna información de los items de una playlist.
    """

    url = f"https://api.spotify.com/v1/playlists/{playlist_id}"

    headers = {
        "Authorization": f"Bearer {spotify_access_token}",
        "Content-Type": "application/json"
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        # La solicitud fue exitosa
        data = response.json()
        return True, data
    
    else:
        return False, {"status_code": response.status_code}


def get_playlist_items(spotify_access_token, playlist_id, offset=0, limit=20):

    """
    Retorna los items de una playlist.
    """

    url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks?offset={offset}&limit={limit}"

    headers = {
        "Authorization": f"Bearer {spotify_access_token}",
        "Content-Type": "application/json"
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        # La solicitud fue exitosa
        data = response.json()
        return True, data
    
    else:
        return False, {"status_code": response.status_code}


def search_tracks_in_catalog(spotify_access_token, search_str):

    """
    Busca una canción en el catalogo de spotify.
    """

    url = f"https://api.spotify.com/v1/search?q={search_str}&type=track&limit=40"

    headers = {
        "Authorization": f"Bearer {spotify_access_token}",
        "Content-Type": "application/json"
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        # La solicitud fue exitosa
        data = response.json()
        data = data["tracks"]
        return True, data
    
    else:
        return False, {"status_code": response.status_code}


def get_track(spotify_access_token, track_id):

    """
    Retorna los datos de una canción.
    """

    url = f"https://api.spotify.com/v1/tracks/{track_id}"

    headers = {
        "Authorization": f"Bearer {spotify_access_token}",
        "Content-Type": "application/json"
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        # La solicitud fue exitosa
        data = response.json()
        return True, data
    
    else:
        return False, {"status_code": response.status_code}


def get_artist(spotify_access_token, artist_id):

    """
    Retorna los datos de un artista.
    """

    url = f"https://api.spotify.com/v1/artists/{artist_id}"

    headers = {
        "Authorization": f"Bearer {spotify_access_token}",
        "Content-Type": "application/json"
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        # La solicitud fue exitosa
        data = response.json()
        return True, data
    
    else:
        return False, {"status_code": response.status_code}


def check_if_track_is_in_playlist(spotify_access_token, track_uri, playlist_id, playlist_track_index):

    """
        Valida que la canción cuyo uri se pasa por parametro se encuentre en la playlist cuyo id se pasa por parametro. Para esto se toma el indice en donde se encuentra la canción dentro de la lista de items de la playlist (dato que se pasa por parámetro), se hace una request para obtener el item de la playlist en ese indice, y se valida que coincidan con el que se paso como parámetro.
    """

    url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks?offset={playlist_track_index}&limit=1&fields=items.track.uri"

    headers = {
        "Authorization": f"Bearer {spotify_access_token}",
        "Content-Type": "application/json"
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        # La solicitud fue exitosa
        data = response.json()

    else:
        return False, {"status_code": response.status_code}

    # Se valida que la canción obtenida en la petición a la api de spotify coincida con la que se pasa por parámetro:
    playlist_item = data["items"][0]
    track_is_in_playlist = playlist_item["track"]["uri"] == track_uri

    return track_is_in_playlist
