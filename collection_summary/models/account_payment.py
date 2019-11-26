from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

MAP_INVOICE_TYPE_PARTNER_TYPE = {
    'out_invoice': 'customer',
    'out_refund': 'customer',
    'in_invoice': 'supplier',
    'in_refund': 'supplier',
}

class account_payment(models.Model):
    _inherit = "account.payment"

    z_invoice_id = fields.Many2one('account.invoice', string="Invoice")
    z_number = fields.Char('Invoice Number',related='z_invoice_id.name')
    inv_ref = fields.Many2one(string="Code")


    @api.multi
    def post(self):
        for l in self:
            if l.invoice_lines:
                for lines in l.invoice_lines:
                    var = self.env['detail.calculation.line'].search(['&',('invoice','=',lines.invoice),('collection_amount','=',lines.allocation)])
                    if var:
                        for v in var:
                            if v.z_state != 'Close':
                                v.update({'z_state':'Close',
                                'refference':l.id})
            
            if l.z_invoice_id:
                detail = self.env['detail.calculation.line'].search(['&',('invoice','=',l.z_invoice_id.number),('collection_amount','=',l.amount)])
                if detail:
                    for line in detail:
                        if line.z_state != 'Close':
                            line.z_state = 'Close'
                            line.refference = l.id
        return  super(account_payment,self).post()

    def action_validate_invoice_payment(self):
        """ Posts a payment used to pay an invoice. This function only posts the
        payment by default but can be overridden to apply specific post or pre-processing.
        It is called by the "validate" button of the popup window
        triggered on invoice form by the "Register Payment" button.
        """
        if any(len(record.invoice_ids) != 1 for record in self):
            # For multiple invoices, there is account.register.payments wizard
            raise UserError(_("This method should only be called to process a single invoice's payment."))
        return self.post()

    # @api.multi
    # def onchange_partner_id(self):
    #     for k in self.invoice_lines:
    #         pay_ref = self.env['detail.calculation.line'].search([('invoice','=',k.invoice)])
    #         for pay in pay_ref:
    #             if pay.z_state == 'Open':
    #                 k.z_seq = 'dd'

    #     return super(account_payment,self).onchange_partner_id()
    # @api.multi
    # def update_invoice_lines(self):
    #     for line in self:
    #         for inv in line.invoice_lines:
    #             pay_ref = self.env['detail.calculation.line'].search([('invoice','=',inv.invoice)])
    #             for pay in pay_ref:
    #                 inv.z_seq = 'eee'
    #     return super(account_payment,self).update_invoice_lines()


class account_abstract_payment(models.AbstractModel):
    _inherit = "account.abstract.payment"

    @api.model
    def default_get(self, fields):
        rec = super(account_abstract_payment, self).default_get(fields)
        active_ids = self._context.get('active_ids')
        active_model = self._context.get('active_model')

        # Check for selected invoices ids
        if not active_ids or active_model != 'account.invoice':
            return rec

        invoices = self.env['account.invoice'].browse(active_ids)

        # Check all invoices are open
        if any(invoice.state != 'open' for invoice in invoices):
            raise UserError(_("You can only register payments for open invoices"))
        # Check all invoices have the same currency
        if any(inv.currency_id != invoices[0].currency_id for inv in invoices):
            raise UserError(_("In order to pay multiple invoices at once, they must use the same currency."))

        # Look if we are mixin multiple commercial_partner or customer invoices with vendor bills
        multi = any(inv.commercial_partner_id != invoices[0].commercial_partner_id
            or MAP_INVOICE_TYPE_PARTNER_TYPE[inv.type] != MAP_INVOICE_TYPE_PARTNER_TYPE[invoices[0].type]
            or inv.account_id != invoices[0].account_id
            or inv.partner_bank_id != invoices[0].partner_bank_id
            for inv in invoices)

        currency = invoices[0].currency_id
        total_amount = self._compute_payment_amount(invoices=invoices, currency=currency)

        rec.update({
            'amount': abs(total_amount),
            'currency_id': currency.id,
            'payment_type': total_amount > 0 and 'inbound' or 'outbound',
            'partner_id': False if multi else invoices[0].commercial_partner_id.id,
            'partner_type': False if multi else MAP_INVOICE_TYPE_PARTNER_TYPE[invoices[0].type],
            'communication': ' '.join([ref for ref in invoices.mapped('reference') if ref]),
            'z_invoice_id': invoices.id,
            'invoice_ids': [(6, 0, invoices.ids)],
            'multi': multi,
        })
        return rec

class PaymentInvoiceLine(models.Model):
    _inherit = 'payment.invoice.line'
    z_seq = fields.Char(string='Collection Reference',compute="check_seq")

    @api.multi
    @api.depends('invoice','allocation')
    def check_seq(self):
        for line in self:
            pay_ref = self.env['detail.calculation.line'].search([('invoice','=',line.invoice),('collection_amount','=',line.allocation)])
            for pay in pay_ref:
                if pay.z_state == 'Open':
                    line.z_seq = pay.z_seq

