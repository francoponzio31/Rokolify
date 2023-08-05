from flask import session, current_app, redirect, url_for, render_template, make_response
from functools import wraps


#? ------------------------ Endpoints decorators:

def host_session_required(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        if not session.get("host_session"):
            return redirect(url_for("login"))
        else:
            return function(*args, **kwargs)
    return wrapper


def guest_session_required(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        if not session.get("guest_session"):
            return render_template("generic_page.html", title="Sesión expirada", content="<h1> Sesión de invitado expirada. </h1>")
        else:
            return function(*args, **kwargs)
    return wrapper

#? ------------------------ Functions:

def owner_with_linked_spotify_account_validation(owner_user_data):

    if not user_has_linked_spotify_account(owner_user_data):
        return make_response(render_template(
                "generic_page.html", 
                content="""
                    <h1> Acceso no permitido </h1>
                    <p class="mt-3"> El acceso a esta sección no está permitido. El usuario anfitrión debe tener una cuanta de Spotify vinculada para acceder a este recurso.</p>
                """
            )
        )


def owner_with_guest_access_allowed_validation(owner_user_data):

    if not user_has_guest_access_allowed(owner_user_data):
        return make_response(render_template(
                "generic_page.html", 
                content="""
                    <h1> Acceso no permitido </h1>
                    <p class="mt-3"> El acceso a la sección de invitados está deshabilitado. El usuario anfitrión ha desactivado la intervención de invitados.</p>
                """
            )
        )


def user_has_linked_spotify_account(user_data):
    return bool(user_data.get("spotify_access_token_data"))


def user_has_guest_access_allowed(user_data):
    return user_data["guest_settings"]["guest_permissions"]["allow_guest_access"]