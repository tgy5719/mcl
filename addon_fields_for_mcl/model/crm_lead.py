from odoo import api, fields, models,_

class Lead(models.Model):
    _inherit = "crm.lead"

    z_project_site = fields.Many2one('site.name',string="Project Site")

    z_partner_id = fields.Many2one('res.partner', string='Customer', track_visibility='onchange', track_sequence=1, index=True,
        help="Linked partner (optional). Usually created when converting the lead. You can find a partner by its Name, TIN, Email or Internal Reference.")
    active = fields.Boolean('Active', default=True, track_visibility=True)

