
from odoo import fields, models


class AccountCostCenterType(models.Model):
    _name = 'account.cost.center.type'

    name = fields.Char(string="Type")

class AccountCostCenterGroup(models.Model):
    _name = 'account.cost.center.group'

    name = fields.Char(string="Group")

class AccountCostCenter(models.Model):
    _name = 'account.cost.center'
    _description = 'Account Dimension'

    name = fields.Char(string='Description', required=True)
    code = fields.Char(required=True)
    z_type = fields.Many2one('account.cost.center.type',string="Type")
    z_group = fields.Many2one('account.cost.center.group',string="Group")
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.user.company_id
    )

    _sql_constraints = [
        ('code_company_uniq', 'unique (name,company_id)', 'The description of the Dimension must be unique per company !')
    ]
