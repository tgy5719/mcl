from odoo import models, fields, api, _,exceptions

class SaleOrder(models.Model):
	_inherit = 'sale.order'

	@api.model
    def _get_default_teams(self):
        return self.env['crm.team']._get_default_team_id()

	z_sales_person = fields.Many2one('res.users',string="Sales Person")
	z_team_id = fields.Many2one('crm.team', 'Sales Team', change_default=True, default=_get_default_teams, oldname='section_id')


	@api.multi
	@api.onchange('partner_id')
	def onchange_partner_id(self):
		if not self.partner_id:
			self.update({
                'partner_invoice_id': False,
                'partner_shipping_id': False,
                'payment_term_id': False,
                'fiscal_position_id': False,
            })
			return
		addr = self.partner_id.address_get(['delivery', 'invoice'])
		values = {
    		'pricelist_id': self.partner_id.property_product_pricelist and self.partner_id.property_product_pricelist.id or False,
    		'payment_term_id': self.partner_id.property_payment_term_id and self.partner_id.property_payment_term_id.id or False,
    		'partner_invoice_id': addr['invoice'],
    		'partner_shipping_id': addr['delivery'],
    		'user_id': self.partner_id.user_id.id or self.env.uid
			}

		if self.z_sales_person:	
			values = {
    		'pricelist_id': self.partner_id.property_product_pricelist and self.partner_id.property_product_pricelist.id or False,
    		'payment_term_id': self.partner_id.property_payment_term_id and self.partner_id.property_payment_term_id.id or False,
    		'partner_invoice_id': addr['invoice'],
    		'partner_shipping_id': addr['delivery'],
    		'user_id': self.z_sales_person.id,
    		'team_id':self.z_team_id.id
			}
		else:
			values = {
    		'pricelist_id': self.partner_id.property_product_pricelist and self.partner_id.property_product_pricelist.id or False,
    		'payment_term_id': self.partner_id.property_payment_term_id and self.partner_id.property_payment_term_id.id or False,
    		'partner_invoice_id': addr['invoice'],
    		'partner_shipping_id': addr['delivery'],
    		'user_id': self.partner_id.user_id.id or self.env.uid,
    		'team_id':self.z_team_id.id
			}

		if self.env['ir.config_parameter'].sudo().get_param('sale.use_sale_note') and self.env.user.company_id.sale_note:
			values['note'] = self.with_context(lang=self.partner_id.lang).env.user.company_id.sale_note

		if self.z_sales_person:
			if self.partner_id.team_id:
				values['team_id'] = self.z_team_id.id
		else:
			if self.partner_id.team_id:
				values['team_id'] = self.partner_id.team_id.id
		self.update(values)