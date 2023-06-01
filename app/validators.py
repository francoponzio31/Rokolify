from flask import session, request, current_app, redirect, jsonify, url_for, render_template
from .services.rokolify_users_service import get_user_data
from functools import wraps


#? ------------------------ Endpoints decorators:
def login_required(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        if not session.get("owner_email"):
            return render_template("generic_page.html", title="Sesión expirada", content="<h1> Sesión expirada </h1>")
        else:
            return function(*args, **kwargs)
    return wrapper


def owner_with_linked_spotify_account_required(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        owner_email = session["owner_email"]
        user_data = get_user_data(owner_email)
        if not user_has_linked_spotify_account(user_data):
            return render_template(
                "generic_page.html", 
                content="""
                    <h1> Acceso no permitido </h1>
                    <p class="mt-3"> El acceso a esta sección no está permitido. El usuario anfitrión debe tener una cuanta de Spotify vinculada para acceder a este recurso.</p>
                """
            )
        else:
            return function(*args, **kwargs)
    return wrapper


#? ------------------------ Functions:

def user_has_linked_spotify_account(user_data):
    return bool(user_data["spotify_access_token_data"])