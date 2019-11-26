# -*- coding: utf-8 -*-

import os
import shutil

from odoo import models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    def action_logout(self):
        user = self.env.uid
        dir_path = self.env['ir.config_parameter'].sudo().get_param('whatsapp_path', '.')
        data_dir = '.user_data_uid_' + str(user)
        try:
            shutil.rmtree(dir_path + '/' + data_dir)
        except:
            os.system('rm -rf ' + dir_path + '/' + data_dir)
