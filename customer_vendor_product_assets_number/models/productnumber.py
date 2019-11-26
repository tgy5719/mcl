from odoo import models, fields, api, _
import psycopg2

from odoo.addons import decimal_precision as dp

from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError, RedirectWarning, except_orm

class ProductTemplate(models.Model):
    _name = 'product.template'
    _inherit =['product.template']
    categ_id=fields.Many2one('product.category')
    default_code= fields.Char(string='Internal Reference',compute = "_trackcode",invisible = True)
    parent_id=fields.Many2one('product.category')
    rate=fields.Integer(string='rate',compute='damage',readonly=True)
    numb = fields.Char(string = 'nummer',readonly=True,compute = '_cege')
    product_code = fields.Char(string = "Product Code")
    state = fields.Selection([('draft', 'Open to Generate Sequence'),('sent', 'Auto Generated Sequence'),], string='Status',readonly=True, select=True, help='sequenceflow stages', default='draft')
    @api.one
    def damage(self):
        for lita in self:
            count = self.env['product.template'].search_count([('categ_id.xander.name','=',lita.categ_id.xander.name)])
            if count == 0:
                self.rate = count
            else:
                self.rate = count
    @api.one
    def _cege(self):
        count = self.env['product.template'].search_count([('categ_id.xander.name','=',self.categ_id.xander.name)])
        n = count
        count=0
        while(n>0):
            count=count+1
            n=n//10
            if count == 1:
                self.numb = "0000"
            if count == 2:
                self.numb = "000"
            if count == 3:
                self.numb = "00"
            if count == 4:
                self.numb = "0"
    @api.one
    @api.depends('product_code')
    def _trackcode(self):
        self.default_code = self.product_code        
    @api.multi
    def product_sequence_generator(self):
        self.ensure_one()
        self.write({
            'state': 'sent',
            })
        for lita in self:
            count = self.env['product.template'].search_count([('categ_id.xander.name','=',lita.categ_id.xander.name)])
            if count == 0:
                self.rate = count
            else:
                self.rate = count   
            count = self.env['product.template'].search_count([('categ_id.xander.name','=',self.categ_id.xander.name)])
            n = count
            count=0
            while(n>0):
                count=count+1
                n=n//10
                if count == 1:
                    self.numb = "0000"
                if count == 2:
                    self.numb = "000"
                if count == 3:
                    self.numb = "00"
                if count == 4:
                    self.numb = "0"
            self.product_code = str(self.categ_id.xander.name)+"-"+str(self.numb)+""+str(self.rate)
            self.default_code = str(self.categ_id.xander.name)+"-"+str(self.numb)+""+str(self.rate)
            
    '''@api.model
    def create(self, vals):
        vals['default_code'] = str(self.categ_id.xander.name)+"-"+str(self.numb)+""+str(self.rate)
        vals['product_number'] = str(self.categ_id.xander.name)+"-"+str(self.numb)+""+str(self.rate)
        """Override default Odoo create function and extend."""
        # Do your custom logic here
        return super(ProductTemplate, self).create(vals)
    @api.multi
    def write(self, vals):
        vals['default_code'] = str(self.categ_id.xander.name)+"-"+str(self.numb)+""+str(self.rate)
        vals['product_number'] = str(self.categ_id.xander.name)+"-"+str(self.numb)+""+str(self.rate)
        """Override default Odoo write function and extend."""
        # Do your custom logic here
        return super(ProductTemplate, self).write(vals)'''
    '''@api.constrains('product_code')
    def _check_employee_code(self):
        for r in self:
            if r.product_code == False:
                raise models.ValidationError('Can Not Save Without Product Code')''' 
    _sql_constraints = [('product_code_uniq', 'unique (product_code)', "The code ID must be unique, this one is already assigned to another product.")]
