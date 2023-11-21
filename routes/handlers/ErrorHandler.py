from flask import Blueprint, redirect

handler = Blueprint('handler', __name__)


@handler.app_errorhandler(404)
def page_not_found(e):
    return redirect("/menu")