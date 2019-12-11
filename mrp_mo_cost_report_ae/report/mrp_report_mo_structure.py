# -*- coding: utf-8 -*-

import json

from odoo import api, models, _
from odoo.tools import float_round, formatLang
class ReportBomStructure(models.AbstractModel):
    _name = 'report.mrp_mo_cost_report_ae.report_mo_structure'
    _description = 'MO Structure and Cost Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        # print(">>>>>>>>>>>>>>>> okkk innn data", data)
        docs = []
        # for bom_id in docids:
        #     bom = self.env['mrp.bom'].browse(bom_id)
        #     variant = data and data.get('variant')
        #     candidates = variant and self.env['product.product'].browse(variant) or bom.product_tmpl_id.product_variant_ids
        #     for product_variant_id in candidates:
        #         if data and data.get('childs'):
        #             doc = self._get_pdf_line(bom_id, product_id=product_variant_id, qty=float(data.get('quantity')), child_bom_ids=json.loads(data.get('childs')))
        #         else:
        #             doc = self._get_pdf_line(bom_id, product_id=product_variant_id, unfolded=True)
        #         doc['report_type'] = 'pdf'
        #         doc['report_structure'] = data and data.get('report_type') or 'all'
        #         docs.append(doc)
        #     if not candidates:
        #         if data and data.get('childs'):
        #             doc = self._get_pdf_line(bom_id, qty=float(data.get('quantity')), child_bom_ids=json.loads(data.get('childs')))
        #         else:
        #             doc = self._get_pdf_line(bom_id, unfolded=True)
        #         doc['report_type'] = 'pdf'
        #         doc['report_structure'] = data and data.get('report_type') or 'all'
        #         docs.append(doc)
        date_from = data and data.get('date_from')
        date_to = data and data.get('date_to')
        product_id = data and data.get('product_id') or False
        product_name = data and data.get('product_name') or False
        lot_id = data and data.get('lot_id') or False
        docs.append(self._get_report_data(bom_id=False, lot_id=lot_id, product_id=product_id, product_name=product_name, date_from=date_from, date_to=date_to))
        return {
            'doc_ids': docids,
            'doc_model': 'mrp.production',
            'docs': docs,
        }

    @api.model
    def get_html(self, bom_id=False, searchQty=1, searchVariant=False, lot_id=False, product_id=False, product_name=False, date_from=False, date_to=False):
        if product_id:
            product_id = [int(p) for p in product_id if p != '0']
        res = self._get_report_data(bom_id=bom_id, searchQty=searchQty, searchVariant=searchVariant, lot_id=lot_id, product_id=product_id, product_name=product_name,  date_from=date_from, date_to=date_to)
        if res and res['lines']:
            res['lines'][0]['report_type'] = 'html'
            res['lines'][0]['report_structure'] = 'all'
            # # res['lines'][0]['has_attachments'] = res['lines'][0]['attachments'] or any(component['attachments'] for component in [li['components'] for li in res['lines']])
            # res['lines'][0]['has_attachments'] = res['lines'][0]['attachments'] or any(component['attachments'] for component in res['lines'][0]['components'])
            res['lines'] = self.env.ref('mrp_mo_cost_report_ae.report_mrp_bom').render({'data': res['lines']})
        return res

    @api.model
    def get_bom(self, bom_id=False, mo=False, product_id=False, line_qty=False, line_id=False, level=False):
        mo = self.env['mrp.production'].search([('name', '=', mo)], limit=1)
        lines = []
        lines.append(self._get_bom(bom_id=bom_id, mo=mo, product_id=product_id, line_qty=line_qty, line_id=line_id, level=level))
        return self.env.ref('mrp_mo_cost_report_ae.report_mrp_bom_line').render({'data': lines})

    @api.model
    def get_operations(self, bom_id=False, qty=0, level=0):
        bom = self.env['mrp.bom'].browse(bom_id)
        lines = self._get_operation_line(bom.routing_id, float_round(qty / bom.product_qty, precision_rounding=1, rounding_method='UP'), level)
        values = {
            'bom_id': bom_id,
            'currency': self.env.user.company_id.currency_id,
            'operations': lines,
        }
        return self.env.ref('mrp_mo_cost_report_ae.report_mrp_operation_line').render({'data': values})

    def _get_bom_reference(self, bom):
        return bom.display_name

    @api.model
    def _get_report_data(self, bom_id, searchQty=0, searchVariant=False, lot_id=False, product_id=False, product_name=False,  date_from=False, date_to=False):
        lines = []
        lots = {}
        products = {}
        bom_product_variants = {}
        bom_quantity = searchQty or 1
        mos = self.env['mrp.production'].search([('state', '=', 'done'), ('date_finished', '!=', False)])
        product_ids = mos.mapped('product_id')
        lot_ids = self.env['stock.production.lot'].sudo().search([])

        for product in product_ids:
            products[product.id] = product.display_name

        if product_id:
            if isinstance(product_id, str) and ',' not in product_id:
                mos = mos.filtered(lambda m: m.product_id.id == int(product_id))
                lot_ids = lot_ids.filtered(lambda l: l.product_id.id == int(product_id))
            if isinstance(product_id, str) and ',' in product_id:
                product_ids = product_id.split(',')
                mos = mos.filtered(lambda m: str(m.product_id.id) in product_ids)
                lot_ids = lot_ids.filtered(lambda l: str(l.product_id.id) in product_ids)
            if isinstance(product_id, list):
                mos = mos.filtered(lambda m: m.product_id.id in product_id)
            if isinstance(product_id, list):
                lot_ids = lot_ids.filtered(lambda l: l.product_id.id in product_id)
        else:
            mos = mos.filtered(lambda m: False)
        if product_name:
            mos = mos.filtered(lambda m: product_name.lower() in m.product_id.display_name.lower())
            lot_ids = lot_ids.filtered(lambda l: product_name.lower() in l.product_id.display_name.lower())

        for lot in lot_ids:
            lots[lot.id] = lot.name
        if lot_id:
            mos = mos.filtered(lambda m: m.finished_move_line_ids.filtered(lambda l: l.lot_id.id == int(lot_id)))
        for mo in mos.filtered(lambda m: str(m.date_finished)[:10] >= date_from and str(m.date_finished)[:10] <= date_to):
            bom = self.env['mrp.bom'].browse(mo.bom_id.id)
            bom_quantity = searchQty or bom.product_qty

            if not searchVariant:
                searchVariant = mo.product_id

                # Get variants used for search
                if not bom.product_id:
                    for variant in bom.product_tmpl_id.product_variant_ids:
                        bom_product_variants[variant.id] = variant.display_name

            level=0
            line = self._get_mo(mo, searchQty, date_from, date_to, level)
            if [mo.name] not in [l.get('child_mos').get('child_mos') and l.get('child_mos').get('child_mos').mapped('name') or [] for l in lines]:
                lines.append(line)
        return {
            'lines': lines,
            'variants': bom_product_variants,
            'is_lot_enabled': self.env.user.user_has_groups('stock.group_production_lot'),
            'lots': lots,
            'products': products,
            'bom_qty': bom_quantity,
            'is_variant_applied': self.env.user.user_has_groups('product.group_product_variant') and len(bom_product_variants) > 1,
            'is_uom_applied': self.env.user.user_has_groups('uom.group_uom')
        }

    def _get_mo(self, mo, searchQty, date_from, date_to, level=0):
        mo_cost = self._get_mo_cost(mo)['total_cost']
        currency = self._get_mo_cost(mo)['currency']
        op_cost = self._get_mo_cost(mo)['op_cost']
        op_time = self._get_mo_cost(mo)['op_time']
        scrap_cost = self._get_mo_cost(mo)['scrap_cost']
        operations = self._get_mo_cost(mo)['operations']
        # operations = self._get_operation_line(mo.routing_id, float_round(searchQty / mo.bom_id.product_qty, precision_rounding=1, rounding_method='UP'), 0)

        bom_quantity = mo.product_qty
        if searchQty > 1:
            bom_quantity = searchQty
        mo_cost = (mo_cost + op_cost)
        components = mo.move_raw_ids
        child_mos = self.env['mrp.production'].search([('state', '=', 'done'), ('date_finished', '!=', False), ('product_id', 'in', components.mapped('product_id').ids)])
        child_mos = child_mos.filtered(lambda m: str(m.date_finished)[:10] >= date_from and str(m.date_finished)[:10] <= date_to)
        if child_mos:
            mo.has_child_mo = True
        for c in child_mos:
            c.level = mo.level + 1
            c.parent_id = mo.id
        return {
            'mo': mo,
            'qty': bom_quantity,
            'parent_id': mo.parent_id,
            'mo_cost': mo_cost,
            'child_mos': {'parent_id': mo.id, 'child_mos': child_mos},
            'level': level or '0',
            'op_cost': op_cost,
            'op_time': op_time,
            'currency': currency,
            'operations': operations,
            'components': components,
        }

    def get_child_mo(self, moId, date_from, date_to, level=0):
        lines = {}
        mo = self.env['mrp.production'].browse([moId])
        mo_cost = self._get_mo_cost(mo)['total_cost']
        currency = self._get_mo_cost(mo)['currency']
        op_cost = self._get_mo_cost(mo)['op_cost']
        op_time = self._get_mo_cost(mo)['op_time']
        scrap_cost = self._get_mo_cost(mo)['scrap_cost']
        operations = self._get_mo_cost(mo)['operations']
        # operations = self._get_operation_line(mo.routing_id, float_round(searchQty / mo.bom_id.product_qty, precision_rounding=1, rounding_method='UP'), 0)
        mo_cost = (mo_cost + op_cost)
        components = mo.move_raw_ids
        child_mos = self.env['mrp.production'].search([('state', '=', 'done'), ('date_finished', '!=', False), ('product_id', 'in', components.mapped('product_id').ids)])
        lines.update({
            'self': self,
            'mo_cost': mo_cost,
            'qty': mo.product_qty,
            'currency': currency,
            'operations': operations,
            'child_mos': child_mos,
            'parent_id': mo.id,
        })
        return self.env.ref('mrp_mo_cost_report_ae.report_mrp_child').render({'data': lines})

    def get_components(self, mo_id):
        mo = self.env['mrp.production'].browse([mo_id])
        components = mo.move_raw_ids
        components = {
            'components': components,
            'currency': self.env.user.company_id.currency_id,
            'parent_id': mo.id,
        }
        return self.env.ref('mrp_mo_cost_report_ae.report_mo_products').render({'components': components})

    def get_ops(self, mo_id):
        mo = self.env['mrp.production'].browse([mo_id])
        currency = self._get_mo_cost(mo)['currency']
        operations = self._get_mo_cost(mo)['operations']
        operations = {
            'mo_id': mo_id,
            'operations': operations,
            'currency': currency,
            'level': mo.level + 1,
        }
        return self.env.ref('mrp_mo_cost_report_ae.report_mrp_operations').render({'data': operations})

    @api.multi
    def _get_mo_cost(self, productions):
        ProductProduct = self.env['product.product']
        StockMove = self.env['stock.move']
        for product in productions.mapped('product_id'):
            mos = productions.filtered(lambda m: m.product_id == product)
            total_cost = 0.0

            #get the cost of operations
            operations = []
            if self.env.user.user_has_groups('mrp.group_mrp_routings'):
                Workorders = self.env['mrp.workorder'].search([('production_id', 'in', mos.ids)])
                if Workorders:
                    query_str = """SELECT w.operation_id, op.name, wc.name, partner.name, sum(t.duration), wc.costs_hour
                                    FROM mrp_workcenter_productivity t
                                    LEFT JOIN mrp_workorder w ON (w.id = t.workorder_id)
                                    LEFT JOIN mrp_workcenter wc ON (wc.id = t.workcenter_id )
                                    LEFT JOIN res_users u ON (t.user_id = u.id)
                                    LEFT JOIN res_partner partner ON (u.partner_id = partner.id)
                                    LEFT JOIN mrp_routing_workcenter op ON (w.operation_id = op.id)
                                    WHERE t.workorder_id IS NOT NULL AND t.workorder_id IN %s
                                    GROUP BY w.operation_id, op.name, wc.name, partner.name, t.user_id, wc.costs_hour
                                    ORDER BY op.name, partner.name
                                """
                    self.env.cr.execute(query_str, (tuple(Workorders.ids), ))
                    for op_id, op_name, wc_name, user, duration, cost_hour in self.env.cr.fetchall():
                        operations.append([user, op_id, op_name + ' - ' + wc_name, duration, cost_hour])

            #get the cost of raw material effectively used
            raw_material_moves = []
            query_str = """SELECT product_id, bom_line_id, SUM(product_qty), abs(SUM(price_unit * product_qty))
                            FROM stock_move WHERE raw_material_production_id in %s AND state != 'cancel'
                            GROUP BY bom_line_id, product_id"""
            self.env.cr.execute(query_str, (tuple(mos.ids), ))
            for product_id, bom_line_id, qty, cost in self.env.cr.fetchall():
                raw_material_moves.append({
                    'qty': qty,
                    'cost': cost,
                    'product_id': ProductProduct.browse(product_id),
                    'bom_line_id': bom_line_id
                })
                total_cost += cost

            #get the cost of scrapped materials
            scraps = StockMove.search([('production_id', 'in', mos.ids), ('scrapped', '=', True), ('state', '=', 'done')])
            uom = mos and mos[0].product_uom_id
            mo_qty = 0
            if not all(m.product_uom_id.id == uom.id for m in mos):
                uom = product.uom_id
                for m in mos:
                    qty = sum(m.move_finished_ids.filtered(lambda mo: mo.state != 'cancel' and mo.product_id == product).mapped('product_qty'))
                    if m.product_uom_id.id == uom.id:
                        mo_qty += qty
                    else:
                        mo_qty += m.product_uom_id._compute_quantity(qty, uom)
            else:
                for m in mos:
                    mo_qty += sum(m.move_finished_ids.filtered(lambda mo: mo.state != 'cancel' and mo.product_id == product).mapped('product_qty'))
            for m in mos:
                sub_product_moves = m.move_finished_ids.filtered(lambda mo: mo.state != 'cancel' and mo.product_id != product)
            
            # operations cost for MO
            op_cost = 0
            op_time = 0
            for op in operations:
                op_cost += (op[3] / 60 ) * op[4]
                op_time += op[3]

            # scrap cost for MO
            scrap_cost = 0
            for scrap in scraps:
                scrap_cost += (scrap.product_uom_qty * scrap.price_unit)

        return {
            'product': product,
            'mo_qty': mo_qty,
            'mo_uom': uom,
            'operations': operations,
            'op_cost': op_cost,
            'op_time': op_time,
            'scrap_cost': scrap_cost,
            'currency': self.env.user.company_id.currency_id,
            'raw_material_moves': raw_material_moves,
            'total_cost': total_cost,
            'scraps': scraps,
            'mocount': len(mos),
            'sub_product_moves': sub_product_moves
        }

    def _get_bom(self, bom_id=False, mo=False, product_id=False, line_qty=False, line_id=False, level=False):
        bom = self.env['mrp.bom'].browse(bom_id)
        bom_quantity = line_qty
        if line_id:
            current_line = self.env['mrp.bom.line'].browse(int(line_id))
            bom_quantity = current_line.product_uom_id._compute_quantity(line_qty, bom.product_uom_id)
        # Display bom components for current selected product variant
        if product_id:
            product = self.env['product.product'].browse(int(product_id))
        else:
            product = bom.product_id or bom.product_tmpl_id.product_variant_id
        if product:
            attachments = self.env['mrp.document'].search(['|', '&', ('res_model', '=', 'product.product'),
            ('res_id', '=', product.id), '&', ('res_model', '=', 'product.template'), ('res_id', '=', product.product_tmpl_id.id)])
        else:
            product = bom.product_tmpl_id
            attachments = self.env['mrp.document'].search([('res_model', '=', 'product.template'), ('res_id', '=', product.id)])
        operations = self._get_operation_line(bom.routing_id, float_round(bom_quantity / bom.product_qty, precision_rounding=1, rounding_method='UP'), 0)
        # mo = self.env['mrp.production'].search([('product_id', '=', product.id)], limit=1)
        lines = {
            'bom': bom,
            'bom_qty': bom_quantity,
            'bom_prod_name': product.display_name,
            'currency': self.env.user.company_id.currency_id,
            'product': product,
            'code': bom and self._get_bom_reference(bom) or '',
            'price': product.uom_id._compute_price(product.standard_price, bom.product_uom_id) * bom_quantity,
            'total': sum([op['total'] for op in operations]),
            'level': level or 0,
            'operations': operations,
            'mo': mo,
            'operations_cost': sum([op['total'] for op in operations]),
            'attachments': attachments,
            'operations_time': sum([op['duration_expected'] for op in operations])
        }
        components, total = self._get_bom_lines(bom, mo, bom_quantity, product, line_id, level)
        lines['components'] = components
        lines['total'] += total
        return lines

    def _get_bom_lines(self, bom, mo, bom_quantity, product, line_id, level):
        components = []
        total = 0
        for line in bom.bom_line_ids:
            line_quantity = (bom_quantity / (bom.product_qty or 1.0)) * line.product_qty
            if line._skip_bom_line(product):
                continue
            price = line.product_id.uom_id._compute_price(line.product_id.standard_price, line.product_uom_id) * line_quantity
            if line.child_bom_id:
                factor = line.product_uom_id._compute_quantity(line_quantity, line.child_bom_id.product_uom_id) / line.child_bom_id.product_qty
                sub_total = self._get_price(line.child_bom_id, factor, line.product_id)
            else:
                sub_total = price
            sub_total = self.env.user.company_id.currency_id.round(sub_total)
            components.append({
                'prod_id': line.product_id.id,
                'prod_name': line.product_id.display_name,
                'code': line.child_bom_id and self._get_bom_reference(line.child_bom_id) or '',
                'prod_qty': line_quantity,
                'prod_uom': line.product_uom_id.name,
                'prod_cost': self.env.user.company_id.currency_id.round(price),
                'parent_id': bom.id,
                'line_id': line.id,
                'level': level or 0,
                'mo': mo,
                'total': sub_total,
                'child_bom': line.child_bom_id.id,
                'phantom_bom': line.child_bom_id and line.child_bom_id.type == 'phantom' or False,
                'attachments': self.env['mrp.document'].search(['|', '&',
                    ('res_model', '=', 'product.product'), ('res_id', '=', line.product_id.id), '&', ('res_model', '=', 'product.template'), ('res_id', '=', line.product_id.product_tmpl_id.id)]),

            })
            total += sub_total
        return components, total

    def _get_operation_line(self, routing, qty, level):
        operations = []
        total = 0.0
        for operation in routing.operation_ids:
            operation_cycle = float_round(qty / operation.workcenter_id.capacity, precision_rounding=1, rounding_method='UP')
            duration_expected = operation_cycle * operation.time_cycle + operation.workcenter_id.time_stop + operation.workcenter_id.time_start
            total = ((duration_expected / 60.0) * operation.workcenter_id.costs_hour)
            operations.append({
                'level': level or 0,
                'operation': operation,
                'name': operation.name + ' - ' + operation.workcenter_id.name,
                'duration_expected': duration_expected,
                'total': self.env.user.company_id.currency_id.round(total),
            })
        return operations

    def _get_price(self, bom, factor, product):
        price = 0
        if bom.routing_id:
            # routing are defined on a BoM and don't have a concept of quantity.
            # It means that the operation time are defined for the quantity on
            # the BoM (the user produces a batch of products). E.g the user
            # product a batch of 10 units with a 5 minutes operation, the time
            # will be the 5 for a quantity between 1-10, then doubled for
            # 11-20,...
            operation_cycle = float_round(factor, precision_rounding=1, rounding_method='UP')
            operations = self._get_operation_line(bom.routing_id, operation_cycle, 0)
            price += sum([op['total'] for op in operations])

        for line in bom.bom_line_ids:
            if line._skip_bom_line(product):
                continue
            if line.child_bom_id:
                qty = line.product_uom_id._compute_quantity(line.product_qty * factor, line.child_bom_id.product_uom_id)
                sub_price = self._get_price(line.child_bom_id, qty, line.product_id)
                price += sub_price
            else:
                prod_qty = line.product_qty * factor
                not_rounded_price = line.product_id.uom_id._compute_price(line.product_id.standard_price, line.product_uom_id) * prod_qty
                price += self.env.user.company_id.currency_id.round(not_rounded_price)
        return price

    def _get_pdf_line(self, bom_id, product_id=False, qty=1, child_bom_ids=[], unfolded=False):

        data = self._get_bom(bom_id=bom_id, product_id=product_id, line_qty=qty)

        def get_sub_lines(bom, product_id, line_qty, line_id, level):
            data = self._get_bom(bom_id=bom.id, product_id=product_id, line_qty=line_qty, line_id=line_id, level=level)
            bom_lines = data['components']
            lines = []
            for bom_line in bom_lines:
                lines.append({
                    'name': bom_line['prod_name'],
                    'type': 'bom',
                    'quantity': bom_line['prod_qty'],
                    'uom': bom_line['prod_uom'],
                    'prod_cost': bom_line['prod_cost'],
                    'bom_cost': bom_line['total'],
                    'level': bom_line['level'],
                    'code': bom_line['code']
                })
                if bom_line['child_bom'] and (unfolded or bom_line['child_bom'] in child_bom_ids):
                    line = self.env['mrp.bom.line'].browse(bom_line['line_id'])
                    lines += (get_sub_lines(line.child_bom_id, line.product_id, bom_line['prod_qty'], line, level + 1))
            if data['operations']:
                lines.append({
                    'name': _('Operations'),
                    'type': 'operation',
                    'quantity': data['operations_time'],
                    'uom': _('minutes'),
                    'bom_cost': data['operations_cost'],
                    'level': level,
                })
                for operation in data['operations']:
                    if unfolded or 'operation-' + str(bom.id) in child_bom_ids:
                        lines.append({
                            'name': operation['name'],
                            'type': 'operation',
                            'quantity': operation['duration_expected'],
                            'uom': _('minutes'),
                            'bom_cost': operation['total'],
                            'level': level + 1,
                        })
            return lines

        bom = self.env['mrp.bom'].browse(bom_id)
        product = product_id or bom.product_id or bom.product_tmpl_id.product_variant_id
        pdf_lines = get_sub_lines(bom, product, qty, False, 1)
        data['components'] = []
        data['lines'] = pdf_lines
        return data


class MoCostXlsx(models.AbstractModel):
    _name = 'report.mrp_mo_cost_report_ae.mo_cost_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, partners):
        date_from = data.get('date_from')
        date_to = data.get('date_to')
        product_ids = data.get('product_ids') and data.get('product_ids').split(',')
        lot_ids = data.get('lot_ids') and data.get('lot_ids').split(',')
        if product_ids:
            product_ids = [int(p) for p in product_ids if p != '0']
        res = self.env['report.mrp_mo_cost_report_ae.report_mo_structure']._get_report_data(bom_id=False, searchQty=False, searchVariant=False, lot_id=lot_ids, product_id=product_ids, product_name=False,  date_from=date_from, date_to=date_to)
        report_name = 'MO Structure & Cost Report'
        sheet = workbook.add_worksheet(report_name[:31])
        bold = workbook.add_format({'bold': True})
        merge_format = workbook.add_format({
            'bold': 2,
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'font_size': 26,
        })
        right_format = workbook.add_format({'align': 'right'})
        sheet.set_column('A:H', 17)
        sheet.set_row(0, 30)
        sheet.merge_range('C1:G1', report_name, merge_format)
        sheet.write(1, 0, 'Product', bold)
        sheet.write(1, 1, 'MO', bold)
        sheet.write(1, 2, 'Production Qty', bold)
        sheet.write(1, 3, 'Production Cost', bold)
        sheet.write(1, 4, 'Component Name', bold)
        sheet.write(1, 5, 'Consumption Qty', bold)
        col = 6
        if self.env.user.user_has_groups('uom.group_uom'):
            sheet.write(1, col, 'Component UoM', bold)
            col += 1
        sheet.write(1, col, 'Unit Cost', bold)
        col += 1
        sheet.write(1, col, 'Component Cost', bold)
        row = 2
        for obj in res.get('lines'):
            sheet.write(row, 0, obj.get('mo').product_id.display_name)
            sheet.write(row, 1, obj.get('mo').name)
            sheet.write(row, 2, obj.get('qty'))
            currency = obj.get('currency')
            mo_cost = formatLang(self.env, obj.get('mo_cost'), currency_obj=currency)
            sheet.write(row, 3, mo_cost, right_format)
            row += 1
            for component in obj.get('components'):
                sheet.write(row, 4, component.product_id.display_name)
                sheet.write(row, 5, component.quantity_done)
                col = 6
                if self.env.user.user_has_groups('uom.group_uom'):
                    sheet.write(row, col, component.product_uom.name)
                    col += 1
                price_unit = formatLang(self.env, component.price_unit, currency_obj=currency)
                sheet.write(row, col, price_unit, right_format)
                col += 1
                component_cost = formatLang(self.env, abs(component.price_unit * component.quantity_done), currency_obj=currency)
                sheet.write(row, col, component_cost, right_format)
                row += 1
            row += 1
