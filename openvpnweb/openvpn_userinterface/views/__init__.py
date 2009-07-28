# encoding: utf-8
# vim: shiftwidth=4 expandtab

from .loginout import login_page, logout_page
from .manage import manage_page, manage_org_page, manage_net_page
from .revoke import revoke_page
from .order import order_page
from .main import main_page
from .setup import setup_wizard

__all__ = [
    "login_page",
    "logout_page",
    "manage_page",
    "manage_org_page",
    "manage_net_page",
    "revoke_page",
    "order_page",
    "main_page",
    "setup_wizard",
]
