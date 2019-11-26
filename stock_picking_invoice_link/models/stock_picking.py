from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    invoice_ids = fields.Many2many(
        comodel_name='account.invoice',
        copy=False,
        string='Invoices',
        readonly=True,
    )

    @api.multi
    def action_view_invoice(self):
        """This function returns an action that display existing invoices
        of given stock pickings.
        It can either be a in a list or in a form view, if there is only
        one invoice to show.
        """
        self.ensure_one()
        action = self.env.ref('account.action_invoice_tree1')
        result = action.read()[0]
        if len(self.invoice_ids) > 1:
            result['domain'] = "[('id', 'in', %s)]" % self.invoice_ids.ids
        else:
            form_view = self.env.ref('account.invoice_form')
            result['views'] = [(form_view.id, 'form')]
            result['res_id'] = self.invoice_ids.id
        return result
