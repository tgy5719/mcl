# -*- coding: utf-8 -*-
import logging

from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)


class SendWAMessage(models.TransientModel):
    _inherit = 'whatsapp.msg'

    @api.model
    def default_get(self, fields):
        result = super(SendWAMessage, self).default_get(fields)
        active_model = self.env.context.get('active_model')
        res_id = self.env.context.get('active_id')
        rec = self.env[active_model].browse(res_id)
        msg = result.get('message', '')
        if active_model == 'purchase.order':
            doc_name = _('Request for Quotation') if rec.state in ['draft', 'sent'] else _('Purchase Order')
            msg = "Dear *PARTNER*" \
            "\nHere is in attachment a " + doc_name + " *" + rec.name + "*"
            if rec.partner_ref:
                msg += " with reference: " + rec.partner_ref
            if rec.state == 'purchase':
                msg += " amounting in *" + self.format_amount(rec.amount_total, rec.currency_id) + "*"
            msg += " from " + rec.company_id.name + ".\n\n"
            msg += "If you have any questions, please do not hesitate to contact us.\n\n" \
            "Best regards."
        result['message'] = msg
        return result
