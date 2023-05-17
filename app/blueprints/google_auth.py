from flask import Blueprint, request, redirect, url_for, session, current_app
import requests
from ..services.rokolify_users_service import get_user_data, add_user, update_user
from ..models import User


google_auth = Blueprint("google_auth", __name__)


