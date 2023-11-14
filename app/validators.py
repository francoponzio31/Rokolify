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
            return render_template("generic_page.html", title="Session expired", content="<h1> Guest session expired. </h1>")
        else:
            return function(*args, **kwargs)
    return wrapper

#? ------------------------ Functions:

def owner_with_linked_spotify_account_validation(owner_user_data):

    if not user_has_linked_spotify_account(owner_user_data):
        return make_response(render_template(
                "generic_page.html", 
                content="""
                    <h1> Access not allowed </h1>
                    <p class="mt-3 text-center"> Access to this section is not allowed. The host user must have a linked Spotify account to access this resource. </p>
                """
            )
        )


def owner_with_guest_access_allowed_validation(owner_user_data):

    if not user_has_guest_access_allowed(owner_user_data):
        return make_response(render_template(
                "generic_page.html", 
                content="""
                    <h1> Access not allowed </h1>
                    <p class="mt-3 text-center"> Access to the guest section is disabled. The host user has deactivated guest intervention. </p>
                """
            )
        )


def user_has_linked_spotify_account(user_data):
    return bool(user_data.get("spotify_access_token_data"))


def user_has_guest_access_allowed(user_data):
    return user_data["guest_settings"]["guest_permissions"]["allow_guest_access"]