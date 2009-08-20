# encoding: utf-8
# vim: shiftwidth=4 expandtab

from .loginout import login_page, logout_page
from .manage import (manage_page,
    manage_org_page, create_org_page,
    manage_network_page, create_network_page,
    manage_client_page, create_client_page,
    manage_server_page, create_server_page,
    manage_group_page, create_group_page,
    manage_org_map_page,
    add_client_to_group_page, remove_client_from_group_page,
    add_client_to_org_page, remove_client_from_org_page,
    add_admin_group_to_org_page, remove_admin_group_from_org_page)
from .logs import manage_log_page
from .revoke import revoke_page
from .order import order_page
from .main import main_page
from .setup import setup_page
