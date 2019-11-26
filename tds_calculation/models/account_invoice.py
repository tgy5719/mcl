# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.tools.float_utils import float_compare
from odoo.exceptions import UserError
from odoo.tools import float_is_zero

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    tds_line_ids = fields.One2many('account.invoice.tds', 'invoice_tds_id', string='TDS Lines',
        readonly=True, states={'draft': [('readonly', False)]}, copy=True)
    amount_tds = fields.Monetary(string='TDS on Base', store=True, readonly=True, compute='_compute_amount', track_visibility='always')
    round_off_value = fields.Monetary(store=True,compute='_compute_amount', string='Round off amount')
    rounded_total = fields.Monetary(store=True,compute='_compute_amount', string='Net Total')
    round_active = fields.Boolean(string="Round Active",default=True)

    @api.one
    @api.depends('invoice_line_ids.price_subtotal', 'tax_line_ids.amount','tds_line_ids.amount', 'tax_line_ids.amount_rounding',
                 'currency_id', 'company_id', 'date_invoice', 'type')
    def _compute_amount(self):
        round_curr = self.currency_id.round
        self.amount_tds = sum(line.total_tds_amount for line in self.invoice_line_ids) 
        self.amount_untaxed = sum(line.price_subtotal for line in self.invoice_line_ids)
        # can change the untaxed amount in line

        self.amount_tax = sum(round_curr(line.amount_total) for line in self.tax_line_ids)
        self.amount_total = (self.amount_untaxed + self.amount_tax) - self.amount_tds
        self.rounded_total = round(self.amount_untaxed + self.amount_tax)
        self.round_off_value = self.rounded_total - (self.amount_untaxed + self.amount_tax)
        #amount varying here
        amount_total_company_signed = self.amount_total
        amount_untaxed_signed = self.amount_untaxed
        if self.currency_id and self.company_id and self.currency_id != self.company_id.currency_id:
            currency_id = self.currency_id.with_context(date=self.date_invoice)
            amount_total_company_signed = currency_id.compute(self.amount_total, self.company_id.currency_id)
            amount_untaxed_signed = currency_id.compute(self.amount_untaxed, self.company_id.currency_id)
        sign = self.type in ['in_refund', 'out_refund'] and -1 or 1
        self.amount_total_company_signed = amount_total_company_signed * sign
        self.amount_total_signed = self.amount_total * sign
        self.amount_untaxed_signed = amount_untaxed_signed * sign

    purchase_id = fields.Many2one(
        comodel_name='purchase.order',
        string='Add Purchase Order',
        readonly=True, states={'draft': [('readonly', False)]},
        help='Encoding help. When selected, the associated purchase order lines are added to the vendor bill. Several PO can be selected.'
    )

    '''@api.multi
                def action_invoice_open(self):
                    # lots of duplicate calls to action_invoice_open, so we remove those already open
                    to_open_invoices = self.filtered(lambda inv: inv.state != 'open')
                    if to_open_invoices.filtered(lambda inv: inv.state != 'draft'):
                        raise UserError(_("Invoice must be in draft state in order to validate it."))
                    if to_open_invoices.filtered(lambda inv: inv.amount_total < 0):
                        raise UserError(_("You cannot validate an invoice with a negative total amount. You should create a credit note instead."))
                    to_open_invoices.action_date_assign()
                    to_open_invoices.action_move_create()
                    return to_open_invoices.invoice_validate()'''

    def _prepare_invoice_line_from_po_line(self, line):
        if line.product_id.purchase_method == 'purchase':
            qty = line.product_qty - line.qty_invoiced
        else:
            qty = line.qty_received - line.qty_invoiced
        if float_compare(qty, 0.0, precision_rounding=line.product_uom.rounding) <= 0:
            qty = 0.0
        taxes = line.taxes_id
        invoice_line_tax_ids = line.order_id.fiscal_position_id.map_tax(taxes)
        invoice_line = self.env['account.invoice.line']
        data = {
            'purchase_line_id': line.id,
            'name': line.order_id.name+': '+line.name,
            'origin': line.order_id.origin,
            'uom_id': line.product_uom.id,
            'product_id': line.product_id.id,
            'tds_nod_id':line.tds_nod_id,
            'tds_percent':line.tds_percent,
            'tds_percent_amount':line.tds_percent_amount,
            'non_pan_tds_percent':line.non_pan_tds_percent,
            'non_pan_tds_percent_amount':line.non_pan_tds_percent_amount,
            'surcharge_percent':line.surcharge_percent,
            'surcharge_percent_amount':line.surcharge_percent_amount,
            'e_cess_percent':line.e_cess_percent,
            'e_cess_percent_amount':line.e_cess_percent_amount,
            'she_cess_percent':line.she_cess_percent,
            'she_cess_percent_amount':line.she_cess_percent_amount,
            'total_tds_amount':line.total_tds_amount,
            'account_id': invoice_line.with_context({'journal_id': self.journal_id.id, 'type': 'in_invoice'})._default_account(),
            'price_unit': line.order_id.currency_id.with_context(date=self.date_invoice).compute(line.price_unit, self.currency_id, round=False),
            'quantity': qty,
            'discount': 0.0,
            'account_analytic_id': line.account_analytic_id.id,
            'analytic_tag_ids': line.analytic_tag_ids.ids,
            'invoice_line_tax_ids': invoice_line_tax_ids.ids
        }
        account = invoice_line.get_invoice_line_account('in_invoice', line.product_id, line.order_id.fiscal_position_id, self.env.user.company_id)
        if account:
            data['account_id'] = account.id
        return data

    @api.onchange('invoice_line_ids')
    def _onchange_invoice_line_ids(self):
        taxes_grouped = self.get_taxes_values()
        tds_grouped = self.get_tds_values()
        tax_lines = self.tax_line_ids.filtered('manual')
        for tax in taxes_grouped.values():
            tax_lines += tax_lines.new(tax)
        self.tax_line_ids = tax_lines
        
        tds_lines = self.tds_line_ids.filtered('manual')
        for line in tds_grouped.values():
            tds_lines += tds_lines.new(line)
        self.tds_line_ids = tds_lines
        return

    @api.multi
    def get_tds_values(self):
        tds_grouped = {}
        for line in self.invoice_line_ids:
        	price_unit = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
        	tds = line.tds_nod_id.compute_all_tds(price_unit, self.currency_id, line.quantity, line.product_id, self.partner_id)['tds']
        	for tds_line in tds:
        		val = self._prepare_tds_line_vals(line, tds_line)
        		key = self.env['account.nod.confg.line'].browse(tds_line['id']).get_grouping_key_tds(val)

        		if key not in tds_grouped:
        			tds_grouped[key] = val
        		else:
        			tds_grouped[key]['amount'] += val['amount']
        return tds_grouped
    
    @api.multi
    def get_taxes_values(self):
        tax_grouped = {}
        for line in self.invoice_line_ids:
            price_unit =line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            taxes = line.invoice_line_tax_ids.compute_all(price_unit, self.currency_id, line.quantity, line.product_id, self.partner_id)['taxes']
            for tax in taxes:
                val = self._prepare_tax_line_vals(line, tax)
                key = self.env['account.tax'].browse(tax['id']).get_grouping_key(val)

                if key not in tax_grouped:
                    tax_grouped[key] = val
                else:
                    tax_grouped[key]['amount'] += val['amount']
                    tax_grouped[key]['base'] += val['base']
        return tax_grouped

    def _prepare_tds_line_vals(self, line, tds_line):
        """ Prepare values to create an account.invoice.tax line

        The line parameter is an account.invoice.line, and the
        tax parameter is the output of account.tax.compute_all().
        """
        vals = {
            'invoice_id': self.id,
            'name': tds_line['name'],
            'tds_id': tds_line['id'],
            'amount': tds_line['amount'],
            'manual': False,
            'sequence': tds_line['sequence'],
            'account_analytic_id': tds_line['analytic'] and line.account_analytic_id.id or False,
            'account_id': self.type in ('out_invoice', 'in_invoice') and (tds_line['account_id'] or line.account_id.id) or (tds_line['refund_account_id'] or line.account_id.id),
        }

        # If the taxes generate moves on the same financial account as the invoice line,
        # propagate the analytic account from the invoice line to the tax line.
        # This is necessary in situations were (part of) the taxes cannot be reclaimed,
        # to ensure the tax move is allocated to the proper analytic account.
        if not vals.get('account_analytic_id') and line.account_analytic_id and vals['account_id'] == line.account_id.id:
            vals['account_analytic_id'] = line.account_analytic_id.id

        return vals

    @api.multi
    def action_move_create(self):
        account_move = self.env['account.move']
        for inv in self:
            if not inv.journal_id.sequence_id:
                raise UserError(_('Please define sequence on the journal related to this invoice.'))
            if not inv.invoice_line_ids.filtered(lambda line: line.account_id):
                raise UserError(_('Please add at least one invoice line.'))
            if inv.move_id:
                continue

            if not inv.date_invoice:
                inv.write({'date_invoice': fields.Date.context_today(self)})
            if not inv.date_due:
                inv.write({'date_due': inv.date_invoice})
            company_currency = inv.company_id.currency_id

            # create move lines (one per invoice line + eventual taxes and analytic lines)
            # sum total is added here
            iml = inv.invoice_line_move_line_get()
            #tax calculation
            iml += inv.tax_line_move_line_get()
            #discount calculation
            iml += inv.tds_line_move_line_get()

            diff_currency = inv.currency_id != company_currency
            total, total_currency, iml = inv.compute_invoice_totals(company_currency, iml)

            name = inv.name or ''
            if inv.payment_term_id:
                totlines = inv.payment_term_id.with_context(currency_id=company_currency.id).compute(total, inv.date_invoice)[0]
                res_amount_currency = total_currency
                for i, t in enumerate(totlines):
                    if inv.currency_id != company_currency:
                        amount_currency = company_currency._convert(t[1], inv.currency_id, inv.company_id, inv._get_currency_rate_date() or fields.Date.today())
                    else:
                        amount_currency = False

                    res_amount_currency -= amount_currency or 0
                    if i + 1 == len(totlines):
                        amount_currency += res_amount_currency

                    # if round off is checked in customer invoice or Vendor Bills
                    if self.round_active is True and self.type in ('in_invoice', 'out_invoice') and self.round_off_value != 0:
                        round_price = self.round_off_value
                        if self.type == 'in_invoice':
                            round_price = -self.round_off_value
                        iml.append({
                            'type': 'dest',
                            'name': name,
                            'price': t[1] + round_price,
                            'account_id': inv.account_id.id,
                            'date_maturity': t[0],
                            'amount_currency': diff_currency and amount_currency,
                            'currency_id': diff_currency and inv.currency_id.id,
                            'invoice_id': inv.id
                        })
                        acc_id = self.env['ir.config_parameter'].sudo().get_param('tds_calculation.round_off_account')
                        if not acc_id:
                            raise UserError(_('Please configure Round Off Account in Account Setting.'))
                        iml.append({
                            'type': 'dest',
                            'name': "Round off",
                            'price': -round_price,
                            'account_id': int(acc_id),
                            'date_maturity': t[0],
                            'amount_currency': diff_currency and amount_currency,
                            'currency_id': diff_currency and inv.currency_id.id,
                            'invoice_id': inv.id
                        })
                    else:
                        iml.append({
                            'type': 'dest',
                            'name': name,
                            'price': t[1],
                            'account_id': inv.account_id.id,
                            'date_maturity': t[0],
                            'amount_currency': diff_currency and amount_currency,
                            'currency_id': diff_currency and inv.currency_id.id,
                            'invoice_id': inv.id
                        })
            else:
                # if round off is checked in customer invoice or Vendor Bills
                if self.round_active is True and self.type in ('in_invoice', 'out_invoice') and self.round_off_value != 0:
                    round_price = self.round_off_value
                    if self.type == 'in_invoice':
                        round_price = -self.round_off_value
                    iml.append({
                        'type': 'dest',
                        'name': name,
                        'price': total + round_price,
                        'account_id': inv.account_id.id,
                        'date_maturity': inv.date_due,
                        'amount_currency': diff_currency and total_currency,
                        'currency_id': diff_currency and inv.currency_id.id,
                        'invoice_id': inv.id
                    })
                    acc_id = self.env['ir.config_parameter'].sudo().get_param('tds_calculation.round_off_account')
                    if not acc_id:
                        raise UserError(_('Please configure Round Off Account in Account Setting.'))
                    iml.append({
                        'type': 'dest',
                        'name': "Round off",
                        'price': -round_price,
                        'account_id': int(acc_id),
                        'date_maturity': inv.date_due,
                        'amount_currency': diff_currency and total_currency,
                        'currency_id': diff_currency and inv.currency_id.id,
                        'invoice_id': inv.id
                    })
                else:
                    iml.append({
                        'type': 'dest',
                        'name': name,
                        'price': total,
                        'account_id': inv.account_id.id,
                        'date_maturity': inv.date_due,
                        'amount_currency': diff_currency and total_currency,
                        'currency_id': diff_currency and inv.currency_id.id,
                        'invoice_id': inv.id
                    })
            part = self.env['res.partner']._find_accounting_partner(inv.partner_id)
            line = [(0, 0, self.line_get_convert(l, part.id)) for l in iml]
            line = inv.group_lines(iml, line)

            line = inv.finalize_invoice_move_lines(line)

            date = inv.date or inv.date_invoice
            move_vals = {
                'ref': inv.reference,
                'line_ids': line,
                'journal_id': inv.journal_id.id,
                'z_analytic_account_id':inv.z_analytic_account_id.id,
                'date': date,
                'narration': inv.comment,
            }
            move = account_move.create(move_vals)

            move.post(invoice = inv)
            
            vals = {
                'move_id': move.id,
                'date': date,
                'move_name': move.name,
            }
            inv.write(vals)
        return True

    @api.model
    def tds_line_move_line_get(self):
        res = []
        # keep track of taxes already processed
        done_taxes = []
        # loop the invoice.tax.line in reversal sequence
        for tds_line in sorted(self.tds_line_ids, key=lambda x: -x.sequence):
            if tds_line.amount_total:
                dis = tds_line.tds_id
                res.append({
                    'invoice_tds_line_id': tds_line.id,
                    'tds_line_id': tds_line.tds_id.id,
                    'type': 'dis',
                    'name': tds_line.name.name,
                    'price_unit': tds_line.amount_total,
                    'quantity': 1,
                    'price': tds_line.amount_total,
                    'account_id': tds_line.account_id.id,
                    'account_analytic_id': tds_line.account_analytic_id.id,
                    'invoice_id': self.id,
                    'tds_id': [(6, 0, list(done_taxes))] if tds_line.tds_id.include_base_amount else []
                })
                done_taxes.append(dis.id)
        return res


    @api.multi
    def compute_invoice_totals(self, company_currency, invoice_move_lines):
        total = 0
        total_currency = 0
        for line in invoice_move_lines:
            if self.currency_id != company_currency:
                currency = self.currency_id.with_context(date=self.date or self.date_invoice or fields.Date.context_today(self))
                if not (line.get('currency_id') and line.get('amount_currency')):
                    line['currency_id'] = currency.id
                    line['amount_currency'] = currency.round(line['price'])
                    line['price'] = currency.compute(line['price'], company_currency)
            else:
                line['currency_id'] = False
                line['amount_currency'] = False
                line['price'] = self.currency_id.round(line['price'])
            if self.type in ('out_invoice', 'in_refund'):
                total += line['price']
                total_currency += line['amount_currency'] or line['price']
                line['price'] = - line['price']
            else:
                total -= line['price']
                total_currency -= line['amount_currency'] or line['price']
        return total, total_currency, invoice_move_lines


class AccountInvoiceLine(models.Model):
    """ Override AccountInvoice_line to add the link to the purchase order line it is related to"""
    _inherit = 'account.invoice.line'

    purchase_line_id = fields.Many2one('purchase.order.line', 'Purchase Order Line', ondelete='set null', index=True, readonly=True)
    purchase_id = fields.Many2one('purchase.order', related='purchase_line_id.order_id', string='Purchase Order', store=False, readonly=True, related_sudo=False,
        help='Associated Purchase Order. Filled in automatically when a PO is chosen on the vendor bill.')
    tds_nod_id = fields.Many2many('account.nod.confg.line', 'tds_id',string='TDS',domain="[('partner_id', '=', partner_id)]")
    total_tds_amount = fields.Float(string="TDS amount", digits=(16, 4))
    product_type = fields.Char(string='Product Type')

    tds_percent = fields.Float(string="TDS %",digits=(16, 4))
    tds_percent_amount = fields.Float(string="TDS Amount",digits=(16, 4))

    non_pan_tds_percent = fields.Float(string="Non Pan TDS %",digits=(16, 4))
    non_pan_tds_percent_amount = fields.Float(string="Non Pan TDS Amount",digits=(16, 4))

    surcharge_percent = fields.Float(string="Surcharge %",digits=(16, 4))
    surcharge_percent_amount = fields.Float(string="Surcharge Amount",digits=(16, 4))

    e_cess_percent = fields.Float(string="E-Cess %",digits=(16, 4))
    e_cess_percent_amount = fields.Float(string="E-Cess amount",digits=(16, 4))

    she_cess_percent = fields.Float(string="She_cess %",digits=(16, 4))
    she_cess_percent_amount = fields.Float(string="She_Cess Amount",digits=(16, 4))


    @api.onchange('product_type')
    def _onchange_product(self):
        self.product_type = "%s" % (self.product_id.type or "")
        
#this function is used only in case of manual vendor bill creation
    @api.onchange('quantity','price_unit','tds_nod_id')
    def _onchange_partner(self):
        if self.tds_nod_id.name.concession_code.id == self.tds_nod_id.concession_code.id:
            if self.tds_nod_id.tds_threshold_applicable == True:
                if self.price_subtotal >= self.tds_nod_id.name.tds_group.tds_threshold_amount:
                    if self.tds_nod_id.name.non_pan_tds_req == True:
                        if not self.tds_nod_id.partner_id.pan_no:
                            self.tds_percent_amount = 0
                            self.tds_percent = 0
                            self.non_pan_tds_percent = self.tds_nod_id.name.non_pan_tds  # Fetching Non Pan TDS Percent Value
                            self.total_tds_amount = ((self.price_unit * self.quantity) * self.non_pan_tds_percent /100) #calculating Non Pan TDS total Value
                            self.non_pan_tds_percent_amount = self.total_tds_amount #Non Pad Calculated amount
                            if self.tds_nod_id.name.surcharge > 0:
                                self.surcharge_percent = self.tds_nod_id.name.surcharge  # Fetching Surcharge Percent Value
                                self.surcharge_percent_amount = self.total_tds_amount * self.tds_nod_id.name.surcharge/100 #calculating surcharge amount
                                self.total_tds_amount = self.surcharge_percent_amount + self.total_tds_amount # adding surcharge to the total tds amount
                            if self.tds_nod_id.name.e_cess > 0:
                                if self.tds_nod_id.name.she_cess > 0:
                                    self.she_cess_percent = self.tds_nod_id.name.she_cess  # Fetching She_Cess Percent Value
                                    self.e_cess_percent = self.tds_nod_id.name.e_cess  # Fetching E_cess Percent Value
                                    self.she_cess_percent_amount = self.total_tds_amount * self.she_cess_percent/100 # calculating she cess amount
                                    self.e_cess_percent_amount = self.total_tds_amount * self.e_cess_percent/100 # Calculating ecess amount
                                    self.total_tds_amount = self.e_cess_percent_amount + self.she_cess_percent_amount + self.total_tds_amount # adding ecess and she_cess to total
                        else:
                            self.non_pan_tds_percent_amount = 0
                            self.non_pan_tds_percent = 0
                            self.tds_percent = self.tds_nod_id.name.tds  # fetching tds percent
                            self.total_tds_amount = ((self.price_unit * self.quantity) * self.tds_percent / 100)
                            self.tds_percent_amount = self.total_tds_amount
                            if self.tds_nod_id.name.surcharge > 0:
                                self.surcharge_percent = self.tds_nod_id.name.surcharge  # Fetching Surcharge Percent Value
                                self.surcharge_percent_amount = self.total_tds_amount * self.tds_nod_id.name.surcharge/100 #calculating surcharge amount
                                self.total_tds_amount = self.surcharge_percent_amount + self.total_tds_amount # adding surcharge to the total tds amount
                            if self.tds_nod_id.name.e_cess > 0:
                                if self.tds_nod_id.name.she_cess > 0:
                                    self.she_cess_percent = self.tds_nod_id.name.she_cess  # Fetching She_Cess Percent Value
                                    self.e_cess_percent = self.tds_nod_id.name.e_cess  # Fetching E_cess Percent Value
                                    self.she_cess_percent_amount = self.total_tds_amount * self.she_cess_percent/100 # calculating she cess amount
                                    self.e_cess_percent_amount = self.total_tds_amount * self.e_cess_percent/100 # Calculating ecess amount
                                    self.total_tds_amount = self.e_cess_percent_amount + self.she_cess_percent_amount + self.total_tds_amount # adding ecess and she_cess to total
                    else:
                        self.non_pan_tds_percent = 0
                        self.non_pan_tds_percent_amount = 0
                        self.tds_percent = self.tds_nod_id.name.tds  # fetching tds percent
                        self.total_tds_amount = ((self.price_unit * self.quantity) * self.tds_percent / 100)
                        self.tds_percent_amount = self.total_tds_amount
                        if self.tds_nod_id.name.surcharge > 0:
                            self.surcharge_percent = self.tds_nod_id.name.surcharge  # Fetching Surcharge Percent Value
                            self.surcharge_percent_amount = self.total_tds_amount * self.tds_nod_id.name.surcharge/100 #calculating surcharge amount
                            self.total_tds_amount = self.surcharge_percent_amount + self.total_tds_amount # adding surcharge to the total tds amount
                        if self.tds_nod_id.name.e_cess > 0:
                            if self.tds_nod_id.name.she_cess > 0:
                                self.she_cess_percent = self.tds_nod_id.name.she_cess  # Fetching She_Cess Percent Value
                                self.e_cess_percent = self.tds_nod_id.name.e_cess  # Fetching E_cess Percent Value
                                self.she_cess_percent_amount = self.total_tds_amount * self.she_cess_percent/100 # calculating she cess amount
                                self.e_cess_percent_amount = self.total_tds_amount * self.e_cess_percent/100 # Calculating ecess amount
                                self.total_tds_amount = self.e_cess_percent_amount + self.she_cess_percent_amount + self.total_tds_amount # adding ecess and she_cess to total
            else:
                if self.tds_nod_id.name.non_pan_tds_req == True:
                    if not self.tds_nod_id.partner_id.pan_no:
                        self.tds_percent_amount = 0
                        self.tds_percent = 0
                        self.non_pan_tds_percent = self.tds_nod_id.name.non_pan_tds  # Fetching Non Pan TDS Percent Value
                        self.total_tds_amount = ((self.price_unit * self.quantity) * self.non_pan_tds_percent /100) #calculating Non Pan TDS total Value
                        self.non_pan_tds_percent_amount = self.total_tds_amount #Non Pad Calculated amount
                        if self.tds_nod_id.name.surcharge > 0:
                            self.surcharge_percent = self.tds_nod_id.name.surcharge  # Fetching Surcharge Percent Value
                            self.surcharge_percent_amount = self.total_tds_amount * self.tds_nod_id.name.surcharge/100 #calculating surcharge amount
                            self.total_tds_amount = self.surcharge_percent_amount + self.total_tds_amount # adding surcharge to the total tds amount
                        if self.tds_nod_id.name.e_cess > 0:
                            if self.tds_nod_id.name.she_cess > 0:
                                self.she_cess_percent = self.tds_nod_id.name.she_cess  # Fetching She_Cess Percent Value
                                self.e_cess_percent = self.tds_nod_id.name.e_cess  # Fetching E_cess Percent Value
                                self.she_cess_percent_amount = self.total_tds_amount * self.she_cess_percent/100 # calculating she cess amount
                                self.e_cess_percent_amount = self.total_tds_amount * self.e_cess_percent/100 # Calculating ecess amount
                                self.total_tds_amount = self.e_cess_percent_amount + self.she_cess_percent_amount + self.total_tds_amount # adding ecess and she_cess to total
                    else:
                        self.non_pan_tds_percent_amount = 0
                        self.non_pan_tds_percent = 0
                        self.tds_percent = self.tds_nod_id.name.tds  # fetching tds percent
                        self.total_tds_amount = ((self.price_unit * self.quantity) * self.tds_percent / 100)
                        self.tds_percent_amount = self.total_tds_amount
                        if self.tds_nod_id.name.surcharge > 0:
                            self.surcharge_percent = self.tds_nod_id.name.surcharge  # Fetching Surcharge Percent Value
                            self.surcharge_percent_amount = self.total_tds_amount * self.tds_nod_id.name.surcharge/100 #calculating surcharge amount
                            self.total_tds_amount = self.surcharge_percent_amount + self.total_tds_amount # adding surcharge to the total tds amount
                        if self.tds_nod_id.name.e_cess > 0:
                            if self.tds_nod_id.name.she_cess > 0:
                                self.she_cess_percent = self.tds_nod_id.name.she_cess  # Fetching She_Cess Percent Value
                                self.e_cess_percent = self.tds_nod_id.name.e_cess  # Fetching E_cess Percent Value
                                self.she_cess_percent_amount = self.total_tds_amount * self.she_cess_percent/100 # calculating she cess amount
                                self.e_cess_percent_amount = self.total_tds_amount * self.e_cess_percent/100 # Calculating ecess amount
                                self.total_tds_amount = self.e_cess_percent_amount + self.she_cess_percent_amount + self.total_tds_amount # adding ecess and she_cess to total
                else:
                    self.non_pan_tds_percent = 0
                    self.non_pan_tds_percent_amount = 0
                    self.tds_percent = self.tds_nod_id.name.tds  # fetching tds percent
                    self.total_tds_amount = ((self.price_unit * self.quantity) * self.tds_percent / 100)
                    self.tds_percent_amount = self.total_tds_amount
                    if self.tds_nod_id.name.surcharge > 0:
                        self.surcharge_percent = self.tds_nod_id.name.surcharge  # Fetching Surcharge Percent Value
                        self.surcharge_percent_amount = self.total_tds_amount * self.tds_nod_id.name.surcharge/100 #calculating surcharge amount
                        self.total_tds_amount = self.surcharge_percent_amount + self.total_tds_amount # adding surcharge to the total tds amount
                    if self.tds_nod_id.name.e_cess > 0:
                        if self.tds_nod_id.name.she_cess > 0:
                            self.she_cess_percent = self.tds_nod_id.name.she_cess  # Fetching She_Cess Percent Value
                            self.e_cess_percent = self.tds_nod_id.name.e_cess  # Fetching E_cess Percent Value
                            self.she_cess_percent_amount = self.total_tds_amount * self.she_cess_percent/100 # calculating she cess amount
                            self.e_cess_percent_amount = self.total_tds_amount * self.e_cess_percent/100 # Calculating ecess amount
                            self.total_tds_amount = self.e_cess_percent_amount + self.she_cess_percent_amount + self.total_tds_amount # adding ecess and she_cess to total




    @api.one
    @api.depends('price_unit', 'discount', 'invoice_line_tax_ids','tds_nod_id', 'quantity',
        'product_id', 'invoice_id.partner_id', 'invoice_id.currency_id', 'invoice_id.company_id',
        'invoice_id.date_invoice')
    def _compute_price(self):
        currency = self.invoice_id and self.invoice_id.currency_id or None
        price =  self.price_unit * (1 - (self.discount or 0.0) / 100.0)
        taxes = False
        if self.invoice_line_tax_ids:
            taxes = self.invoice_line_tax_ids.compute_all(price, currency, self.quantity, product=self.product_id, partner=self.invoice_id.partner_id)
        self.price_subtotal = price_subtotal_signed = taxes['total_excluded'] if taxes else self.quantity * self.price_unit
        self.price_total = taxes['total_included'] if taxes else self.price_subtotal
        if self.invoice_id.currency_id and self.invoice_id.currency_id != self.invoice_id.company_id.currency_id:
            price_subtotal_signed = self.invoice_id.currency_id.with_context(date=self.invoice_id.date_invoice).compute(price_subtotal_signed, self.invoice_id.company_id.currency_id)
        sign = self.invoice_id.type in ['in_refund', 'out_refund'] and -1 or 1
        self.price_subtotal_signed = price_subtotal_signed * sign
#need to change the sub total, based on the subtotal the tds should be deducted and tax should be calculated and the same tds amount should be added in the line of tds