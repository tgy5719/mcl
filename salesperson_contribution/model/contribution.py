from odoo import api, fields, models,_
from odoo.exceptions import UserError

class InvoiceContribution(models.Model):
    _name = 'invoice.contribution'
    z_contribute = fields.Many2one('account.invoice')
    z_invoice_no = fields.Char('Invoice NO',store=True,compute="contribution_invoice")
    z_invoice_value = fields.Float('Invoice Value',store=True)
    z_salesperson = fields.Many2one('res.users','Salesperson',store=True)
    z_contribution = fields.Integer('Contribution %',store=True)
    z_sp_contribution = fields.Float('SP Contribution',store=True)
    z_sl_no = fields.Integer('SL NO')
    z_partner = fields.Char('Customer',store=True,compute="contribution_invoice")

    @api.depends('z_contribute.number','z_contribution')
    def contribution_invoice(self):
        c = 0
        for line in self:
            line.z_invoice_no = line.z_contribute.number
            line.z_invoice_value = line.z_contribute.amount_total
            line.z_partner = line.z_contribute.partner_id.name


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    z_contribute_ids = fields.One2many('invoice.contribution','z_contribute')
    z_contribution_total = fields.Integer('total')

    @api.onchange('z_contribute_ids')
    def sl_no(self):
    	sl = cl = 0
    	for l in self.z_contribute_ids:
    		sl = sl + 1
    		l.z_sl_no = sl
    	for line in self.z_contribute_ids:
    		if line.z_sl_no == 1:
    			if line.z_contribution == False:
    				line.z_contribution = 100
    		if line.z_contribution:
    			cl += line.z_contribution
    			self.z_contribution_total = cl
    			line.z_sp_contribution = line.z_invoice_value * line.z_contribution / 100

    @api.multi
    def write(self, vals):
        res = super(AccountInvoice,self).write(vals)
        price = 0
        if 'z_contribution_total' in vals:
            for line in self:
                price = vals['z_contribution_total']
                if int(price) > 100:
                    raise UserError(_('The contribution amount should not Exceed 100'))
                if int(price) < 100:
                    raise UserError(_('The contribution amount should not be less than 100'))
        return res

    	





    	