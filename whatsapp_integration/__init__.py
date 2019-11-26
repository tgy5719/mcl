# -*- coding: utf-8 -*-

import os
from . import models
from . import wizard

from odoo.api import Environment, SUPERUSER_ID


def add_dir_to_icp(cr, registery):
    env = Environment(cr, SUPERUSER_ID, {})
    dir_path = os.path.dirname(os.path.abspath(__file__))
    dir_path = os.path.abspath(dir_path + '/wizard')
    env['ir.config_parameter'].sudo().set_param('whatsapp_path', dir_path)
