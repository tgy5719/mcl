from odoo import models, fields, api, _,exceptions

class CrmLeadLoginRestriction(models.Model):
    _name = 'crm.lead.login.restriction'

    name = fields.Many2one('res.users',string="Sales Person Name")
    z_sales_person = fields.Many2one('res.users',string="Sales Person")
    z_password = fields.Char(string='Password')
    z_valid_sales_person = fields.Boolean(string="Validate",default=False)

    @api.multi
    def validate_sales_person(self):
        #function to check the valid user and login credentials
        for line in self:
            if line.z_sales_person:
                if line.z_password:
                    if line.z_sales_person.z_password == line.z_password:
                        line.z_valid_sales_person = True
                        line.name = line.z_sales_person.id
                    else:
                        raise exceptions.Warning(("Please enter valid password"))
                else:
                    raise exceptions.Warning(("Please enter password"))
            else:
                raise exceptions.Warning(("Please enter User name"))

    @api.multi
    def logout(self):
        log = self.env['crm.lead.login.restriction'].search([('id', '=', self.id)]).unlink()
        return super(CrmLeadLoginRestriction, self).unlink()

    @api.multi
    def create_leads(self):
        #on click of button viewing the leads screen to create
        view_id = self.env.ref('crm.crm_case_form_view_leads').id
        context = self._context.copy()
        return {
            'name':'Create Leads',
            'view_type':'form',
            'view_mode':'form',
            'views' : [(view_id,'form')],
            'res_model':'crm.lead',
            'view_id':view_id,
            'type':'ir.actions.act_window',
            'target':'new',
            'context': {'default_user_id': self.z_sales_person.id}
            }

    @api.multi
    def view_leads(self):
        #on click of button viewing the leads screen(widget)
        team_lead = res_team_lead = 0
        #check from team master for leader allocation
        team_leader =  self.env['crm.team'].search([('user_id', '=', self.z_sales_person.id)])
        team_leader_ids =[]
        team_ids =[]

        for leader in team_leader:
            #assigning the user id
            leader_id = leader.user_id.id
            team_leader_ids.append(leader_id)
            #assigning the team id
            team = leader.id
            team_ids.append(team)

        sale_partner_user = self.env['res.partner'].search([('name', '=', self.z_sales_person.name)])
        if sale_partner_user.z_sales_manager == True:
            for user in team_leader_ids:
                partner_user = self.env['res.partner'].search([('user_id', '=', user)])
                if partner_user:
                    for line in partner_user:
                        tree_view = self.env.ref('crm.crm_case_tree_view_leads')
                        view_id = self.env.ref('crm.crm_case_form_view_leads')
                        return {
                            'name': _('Leads'),
                            'view_type': 'form',
                            'view_mode': 'tree, form',
                            'res_model': 'crm.lead',
                            'domain': [('type', '=', 'lead'),('team_id','=',team_ids)],
                            'res_id': self.id,
                            'view_id': view_id.id,
                            'views': [
                                (tree_view.id, 'tree'),(view_id.id, 'form')
                            ],
                            'type': 'ir.actions.act_window',
                            }   
        else:
            tree_view = self.env.ref('crm.crm_case_tree_view_leads')
            view_id = self.env.ref('crm.crm_case_form_view_leads')
            return {
                'name': _('Leads'),
                'view_type': 'form',
                'view_mode': 'tree, form',
                'res_model': 'crm.lead',
                'domain': [('type', '=', 'lead'),('user_id','=',self.z_sales_person.id)],
                'res_id': self.id,
                'view_id': view_id.id,
                'views': [
                    (tree_view.id, 'tree'),(view_id.id, 'form')
                ],
                'type': 'ir.actions.act_window',
                }   


    @api.multi
    def create_pipeline(self):
        #on click of button creating the leads screen
        view_id = self.env.ref('crm.crm_case_form_view_oppor').id
        return {
            'name':'Create Leads Opportunity',
            'view_type':'form',
            'view_mode':'form',
            'views' : [(view_id,'form')],
            'res_model':'crm.lead',
            'view_id':view_id,
            'type':'ir.actions.act_window',
            'target':'new',
            'context': {'default_type': 'opportunity',
            			'default_user_id': self.z_sales_person.id}
            }

    @api.multi
    def view_pipeline(self):
        team_lead = res_team_lead = 0
        #check from team master for leader allocation
        team_leader =  self.env['crm.team'].search([('user_id', '=', self.z_sales_person.id)])
        team_leader_ids =[]
        team_ids =[]

        for leader in team_leader:
            #assigning the user id
            leader_id = leader.user_id.id
            team_leader_ids.append(leader_id)
            #assigning the team id
            team = leader.id
            team_ids.append(team)

        sale_partner_user = self.env['res.partner'].search([('name', '=', self.z_sales_person.name)])
        if sale_partner_user.z_sales_manager == True:
            for user in team_leader_ids:
                partner_user = self.env['res.partner'].search([('user_id', '=', user)])
                if partner_user:
                    for line in partner_user:
                        tree_view = self.env.ref('crm.crm_case_tree_view_oppor')
                        view_id = self.env.ref('crm.crm_case_form_view_oppor')
                        return {
                            'name': _('Opportunity'),
                            'view_type': 'form',
                            'view_mode': 'tree, form',
                            'res_model': 'crm.lead',
                            'domain': [('type', '=', 'opportunity'),('team_id','=',team_ids)],
                            'res_id': self.id,
                            'view_id': view_id.id,
                            'views': [
                                (tree_view.id, 'tree'),(view_id.id, 'form')
                            ],
                            'type': 'ir.actions.act_window',
                        } 
        else:
            tree_view = self.env.ref('crm.crm_case_tree_view_oppor')
            view_id = self.env.ref('crm.crm_case_form_view_oppor')
            return {
                'name': _('Opportunity'),
                'view_type': 'form',
                'view_mode': 'tree, form',
                'res_model': 'crm.lead',
                'domain': [('type', '=', 'opportunity'),('user_id','=',self.z_sales_person.id)],
                'res_id': self.id,
                'view_id': view_id.id,
                'views': [
                    (tree_view.id, 'tree'),(view_id.id, 'form')
                ],
                'type': 'ir.actions.act_window',
            } 

    @api.multi
    def create_sale_order(self):
        #on click of button create the sale order
        view_id = self.env.ref('sale.view_order_form').id
        return {
            'name':'Create Sales Order',
            'view_type':'form',
            'view_mode':'form',
            'views' : [(view_id,'form')],
            'res_model':'sale.order',
            'view_id':view_id,
            'type':'ir.actions.act_window',
            'target':'new',
            'context': {'default_z_sales_person': self.z_sales_person.id}
        }

    @api.multi
    def view_sale_order(self):
        team_lead = res_team_lead = 0
        #check from team master for leader allocation
        team_leader =  self.env['crm.team'].search([('user_id', '=', self.z_sales_person.id)])
        team_leader_ids =[]
        team_ids =[]

        for leader in team_leader:
            #assigning the user id
            leader_id = leader.user_id.id
            team_leader_ids.append(leader_id)
            #assigning the team id
            team = leader.id
            team_ids.append(team)

        sale_partner_user = self.env['res.partner'].search([('name', '=', self.z_sales_person.name)])
        if sale_partner_user.z_sales_manager == True:
            for user in team_leader_ids:
                partner_user = self.env['res.partner'].search([('user_id', '=', user)])
                if partner_user:
                    for line in partner_user:
                        tree_view = self.env.ref('sale.view_order_tree')
                        view_id = self.env.ref('sale.view_order_form')
                        return {
                            'name': _('Sale Orders'),
                            'view_type': 'form',
                            'view_mode': 'tree, form',
                            'res_model': 'sale.order',
                            'domain': [('state', '=', 'sale'),('team_id','=',team_ids)],
                            'res_id': self.id,
                            'view_id': view_id.id,
                            'views': [
                                (tree_view.id, 'tree'),(view_id.id, 'form')
                            ],
                            'type': 'ir.actions.act_window',
                        }
        else:
            tree_view = self.env.ref('sale.view_order_tree')
            view_id = self.env.ref('sale.view_order_form')
            return {
                'name': _('Sale Order'),
                'view_type': 'form',
                'view_mode': 'tree, form',
                'res_model': 'sale.order',
                'domain': [('state', '=', 'sale'),('user_id','=',self.z_sales_person.id)],
                'res_id': self.id,
                'view_id': view_id.id,
                'views': [
                    (tree_view.id, 'tree'),(view_id.id, 'form')
                ],
                'type': 'ir.actions.act_window',
                }


    @api.multi
    def create_quotation(self):
        view_id = self.env.ref('sale.view_order_form').id
        return {
            'name':'Create Quotation',
            'view_type':'form',
            'view_mode':'form',
            'views' : [(view_id,'form')],
            'res_model':'sale.order',
            'view_id':view_id,
            'type':'ir.actions.act_window',
            'target':'new',
            'context': {'default_z_sales_person': self.z_sales_person.id}
        }

    @api.multi
    def view_quotation(self):
        team_lead = res_team_lead = 0
        #check from team master for leader allocation
        team_leader =  self.env['crm.team'].search([('user_id', '=', self.z_sales_person.id)])
        team_leader_ids =[]
        team_ids =[]

        for leader in team_leader:
            #assigning the user id
            leader_id = leader.user_id.id
            team_leader_ids.append(leader_id)
            #assigning the team id
            team = leader.id
            team_ids.append(team)

        sale_partner_user = self.env['res.partner'].search([('name', '=', self.z_sales_person.name)])
        if sale_partner_user.z_sales_manager == True:
            for user in team_leader_ids:
                partner_user = self.env['res.partner'].search([('user_id', '=', user)])
                if partner_user:
                    for line in partner_user:
                        tree_view = self.env.ref('sale.view_quotation_tree_with_onboarding')
                        view_id = self.env.ref('sale.view_order_form')
                        return {
                            'name': _('Quotation'),
                            'view_type': 'form',
                            'view_mode': 'tree, form',
                            'res_model': 'sale.order',
                            'domain': [('state', '!=', 'sale'),('team_id','=',team_ids)],
                            'res_id': self.id,
                            'view_id': view_id.id,
                            'views': [
                                (tree_view.id, 'tree'),(view_id.id, 'form')
                            ],
                            'type': 'ir.actions.act_window',
                            }
        else:
            tree_view = self.env.ref('sale.view_quotation_tree_with_onboarding')
            view_id = self.env.ref('sale.view_order_form')
            return {
                'name': _('Quotation'),
                'view_type': 'form',
                'view_mode': 'tree, form',
                'res_model': 'sale.order',
                'domain': [('state', '!=', 'sale'),('user_id','=',self.z_sales_person.id)],
                'res_id': self.id,
                'view_id': view_id.id,
                'views': [
                    (tree_view.id, 'tree'),(view_id.id, 'form')
                ],
                'type': 'ir.actions.act_window',
                }


    @api.multi
    def view_tax_invoices(self):
        team_lead = res_team_lead = 0
        #check from team master for leader allocation
        team_leader =  self.env['crm.team'].search([('user_id', '=', self.z_sales_person.id)])
        team_leader_ids =[]
        team_ids =[]

        for leader in team_leader:
            #assigning the user id
            leader_id = leader.user_id.id
            team_leader_ids.append(leader_id)
            #assigning the team id
            team = leader.id
            team_ids.append(team)

        sale_partner_user = self.env['res.partner'].search([('name', '=', self.z_sales_person.name)])
        if sale_partner_user.z_sales_manager == True:
            for user in team_leader_ids:
                partner_user = self.env['res.partner'].search([('user_id', '=', user)])
                if partner_user:
                    for line in partner_user:
                        tree_view = self.env.ref('account.invoice_tree_with_onboarding')
                        view_id = self.env.ref('account.invoice_form')
                        return {
                        'name': _('Tax Invoice'),
                        'view_type': 'form',
                        'view_mode': 'tree, form',
                        'res_model': 'account.invoice',
                        'domain': [('team_id','=',team_ids)],
                        'res_id': self.id,
                        'view_id': view_id.id,
                        'views': [
                            (tree_view.id, 'tree'),(view_id.id, 'form')
                        ],
                        'type': 'ir.actions.act_window',
                        }
        else:
            tree_view = self.env.ref('account.invoice_tree_with_onboarding')
            view_id = self.env.ref('account.invoice_form')
            return {
            'name': _('Tax Invoice'),
            'view_type': 'form',
            'view_mode': 'tree, form',
            'res_model': 'account.invoice',
            'domain': [('user_id','=',self.z_sales_person.id)],
            'res_id': self.id,
            'view_id': view_id.id,
            'views': [
                (tree_view.id, 'tree'),(view_id.id, 'form')
            ],
            'type': 'ir.actions.act_window',
            }

        
    @api.multi
    def create_collection_details(self):
        #on click of a button creating collection summary
        view_id = self.env.ref('collection_summary.view_sale_calculation').id
        return {
            'name':'Collection Details',
            'view_type':'form',
            'view_mode':'form',
            'views' : [(view_id,'form')],
            'res_model':'sale.calculation',
            'view_id':view_id,
            'type':'ir.actions.act_window',
            'target':'self',
            'context': {'default_user_id': self.z_sales_person.id}
  
        }

    @api.multi
    def view_collection_summary(self):
        #on click of button viewing the collection summary screen
        tree_view = self.env.ref('collection_summary.view_sale_calculation_detail_tree')
        view_id = self.env.ref('collection_summary.view_sale_calculation_detail_form')
        return {
        'name': _('Collection Summary'),
        'view_type': 'form',
        'view_mode': 'tree',
        'res_model': 'detail.calculation.line',
        'domain': [('user_id','=',self.z_sales_person.id)],
        'res_id': self.id,
        'view_id': view_id.id,
        'views': [
            (tree_view.id, 'tree'),(view_id.id, 'form')
        ],
        'type': 'ir.actions.act_window',
        }

    @api.multi
    def view_stock_summary(self):
        tree_view = self.env.ref('stock_summary.view_stock_quant_tree_inherited')
        pivot_view = self.env.ref('stock.view_stock_quant_pivot')
        return {
        'name': _('Stock Summary'),
        'view_mode': 'tree',
        'res_model': 'stock.quant',
        'domain': ['|','|','|','|','|',['product_id.categ_id.name','=','FG'],['product_id.categ_id.parent_id.name','=','FG'],['product_id.categ_id.parent_id.parent_id.name','=','FG'],['product_id.categ_id.name','=','BG'],['product_id.categ_id.parent_id.name','=','BG'],['product_id.categ_id.parent_id.parent_id.name','=','BG'],['location_id.usage','=', 'internal']],
        'res_id': self.id,
        'views': [
            (tree_view.id, 'tree'),(pivot_view.id,'pivot')
        ],
        'type': 'ir.actions.act_window',
        }

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    #@api.model
    #def _get_default_teams(self):
        #return self.env['crm.team']._get_default_team_id()    

    z_sales_person = fields.Many2one('res.users',string="Sales Person")
    #z_team_id = fields.Many2one('crm.team', 'Sales Team', change_default=True, default=_get_default_teams, oldname='section_id')

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

        if self.z_sales_person:	
            values = {
    		'pricelist_id': self.z_sales_person.property_product_pricelist and self.z_sales_person.property_product_pricelist.id or False,
    		'payment_term_id': self.partner_id.property_payment_term_id and self.partner_id.property_payment_term_id.id or False,
    		'partner_invoice_id': addr['invoice'],
    		'partner_shipping_id': addr['delivery'],
            #passing sales person and team. Rest are standard function
    		'user_id': self.z_sales_person.id,
            'team_id':self.z_sales_person.team_id.id,
            'z_sale_ofc':self.z_sales_person.z_sales_office.id,
            'pricelist_id':self.z_sales_person.property_product_pricelist.id
			}
        else:
            values = {
    		'pricelist_id': self.user_id.property_product_pricelist and self.user_id.property_product_pricelist.id or False,
    		'payment_term_id': self.partner_id.property_payment_term_id and self.partner_id.property_payment_term_id.id or False,
    		'partner_invoice_id': addr['invoice'],
    		'partner_shipping_id': addr['delivery'],
    		'user_id': self.partner_id.user_id.id or self.env.uid
			}

        if self.env['ir.config_parameter'].sudo().get_param('sale.use_sale_note') and self.env.user.company_id.sale_note:
            values['note'] = self.with_context(lang=self.partner_id.lang).env.user.company_id.sale_note

        if self.z_sales_person:
            if self.partner_id.team_id:
                values['team_id'] = self.z_sales_person.team_id.id
        else:
            if self.partner_id.team_id:
                values['team_id'] = self.partner_id.team_id.id
        self.update(values)


    # @api.model
    # def create(self, vals):
    #     if vals.get('name', _('New')) == _('New'):
    #         if 'company_id' in vals:
    #             vals['name'] = self.env['ir.sequence'].with_context(force_company=vals['company_id']).next_by_code('sale.order') or _('New')
    #         else:
    #             vals['name'] = self.env['ir.sequence'].next_by_code('sale.order') or _('New')

    #     # Makes sure partner_invoice_id', 'partner_shipping_id' and 'pricelist_id' are defined
    #     if any(f not in vals for f in ['partner_invoice_id', 'partner_shipping_id', 'pricelist_id']):
    #         partner = self.env['res.partner'].browse(vals.get('partner_id'))
    #         addr = partner.address_get(['delivery', 'invoice'])
    #         vals['partner_invoice_id'] = vals.setdefault('partner_invoice_id', addr['invoice'])
    #         vals['partner_shipping_id'] = vals.setdefault('partner_shipping_id', addr['delivery'])
    #         #vals['pricelist_id'] = vals.setdefault('pricelist_id', partner.property_product_pricelist and partner.property_product_pricelist.id)
    #     result = super(SaleOrder, self).create(vals)
    #     return result