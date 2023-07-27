from flask import session, current_app, redirect, url_for, render_template, jsonify
from app import create_app
from app.validators import host_session_required


app = create_app()


@app.get("/")
@host_session_required
def index():
    return redirect(url_for("owner_bp.account_settings"))


@app.get("/login")
def login():
    return render_template("login_templates/rokolify_login.html")


@app.get("/logout")
@host_session_required
def logout():
    session.pop("host_session", None)
    return redirect(url_for("login"))


@app.errorhandler(Exception)
def handle_exception(error):
    
    import os
    from dotenv import load_dotenv
    from werkzeug.exceptions import HTTPException
    
    load_dotenv()
    ENV = os.getenv("ENV")

    # Errores HTTP no se manejan:
    if isinstance(error, HTTPException):
        return error

    # En ambientes de desarrollo no se manejan excepciones:
    elif ENV != "PROD":
        raise Exception(error)

    # Manejo de excepciones ocacionadas en la lógica en ambiente productivo:
    else:
        return render_template("generic_page.html", content="<h1> Lo sentimos, se ha producido un error </h1>")


if __name__ == "__main__":
    app.run(port=8888)
