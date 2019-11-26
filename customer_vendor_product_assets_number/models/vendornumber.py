from odoo import models, fields, api, _

class ResPartners(models.Model):
	_name = 'res.partner'
	_inherit = 'res.partner'
	reffer = fields.Char(string='reffer',store= True)
	Vendor_code1 = fields.Many2one('res.partner1',string = 'Vendor Category',store = True)
	Custumer_code1 = fields.Many2one('res.partner2',string = 'Customer Category',store = True)
	ratey=fields.Integer(string='rate',compute='damagey',readonly=True)
	row=fields.Integer(string='row',compute='damagery',readonly=True)
	umb=fields.Char(string='umb')
	than = fields.Char(string='than',store=True)
	numb = fields.Char(string = 'nummer',readonly=True,compute = '_cege')
	numb1 = fields.Char(string = 'nummerer',readonly=True,compute = '_cege1')
	ref_code = fields.Char('Code',store = True)
	ref = fields.Char('Internal Refference',store = True,compute = "_trackcode",invisible = True)
	state = fields.Selection([('draft', 'Open to Generate Sequence'),('sent', 'Auto Generated Sequence'),], string='Status',readonly=True, select=True, help='sequenceflow stages', default='draft')
	status = fields.Selection([('draft', 'Open to Generate Sequence'),('sent', 'Auto Generated Sequence'),], string='Status',readonly=True, select=True, help='sequenceflow stages', default='draft')
	'''@api.onchange('customer')
	def _concate(self):
		return {'value':{'customer':self.customer,'supplier':False}}
	@api.onchange('supplier')
	def _concate2(self):
		return {'value':{'supplier':self.supplier,'customer':False}}'''
	'''@api.model
	def create(self, vals):
		vals['ref'] = self.env['ir.sequence'].next_by_code('vendor.number')
		return super(ResPartners, self).create(vals)'''
	@api.one
	def damagey(self):
		for lita in self:
			count = self.env['res.partner'].search_count([('Vendor_code1.name','=',lita.Vendor_code1.name)])
			if count == 0:
				self.ratey = count
			else:
				self.ratey = count
	@api.one
	def _cege(self):
		count = self.env['res.partner'].search_count([('Vendor_code1.name','=',self.Vendor_code1.name)])
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
	def damagery(self):
		for lita in self:
			count = self.env['res.partner'].search_count([('Custumer_code1.name','=',lita.Custumer_code1.name)])
			if count == 0:
				self.row = count
			else:
				self.row = count
	@api.one
	def _cege1(self):
		count = self.env['res.partner'].search_count([('Custumer_code1.name','=',self.Custumer_code1.name)])
		n = count
		count=0
		while(n>0):
			count=count+1
			n=n//10
			if count == 1:
				self.numb1 = "0000"
			if count == 2:
				self.numb1 = "000"
			if count == 3:
				self.numb1 = "00"
			if count == 4:
				self.numb1 = "0"
	
	@api.multi
	def customer_sequence_generator(self):
		self.ensure_one()
		self.write({'state': 'sent',})
		for lita in self:
			count = self.env['res.partner'].search_count([('Custumer_code1.name','=',lita.Custumer_code1.name)])
			if count == 0:
				self.row = count
			else:
				self.row = count
			count = self.env['res.partner'].search_count([('Custumer_code1.name','=',self.Custumer_code1.name)])
			n = count
			count=0
			while(n>0):
				count=count+1
				n=n//10
				if count == 1:
					self.numb1 = "0000"
				if count == 2:
					self.numb1 = "000"
				if count == 3:
					self.numb1 = "00"
				if count == 4:
					self.numb1 = "0"
			self.ref_code = str(self.Custumer_code1.name)+"-"+str(self.numb1)+""+str(self.row)
	@api.multi
	def vendor_sequence_generator(self):
		self.ensure_one()
		self.write({'status': 'sent',})
		for lita in self:
			count = self.env['res.partner'].search_count([('Vendor_code1.name','=',lita.Vendor_code1.name)])
			if count == 0:
				self.ratey = count
			else:
				self.ratey = count
			count = self.env['res.partner'].search_count([('Vendor_code1.name','=',self.Vendor_code1.name)])
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
			self.ref_code = str(self.Vendor_code1.name)+"-"+str(self.numb)+""+str(self.ratey)
	@api.one
	@api.depends('ref_code')
	def _trackcode(self):
		self.ref = self.ref_code  
	'''@api.model
	def create(self, vals):
		#vals['ref'] = str(self.Custumer_code1.name)+"-"+str(self.numb1)+""+str(self.row)
		#vals['reffer'] = str(self.Custumer_code1.name)+"-"+str(self.numb1)+""+str(self.row)
		vals['customer_number'] = str(self.Custumer_code1.name)+"-"+str(self.numb1)+""+str(self.row)
		vals['vendor_number'] = str(self.Vendor_code1.name)+"-"+str(self.numb)+""+str(self.ratey)
		#vals['reffer'] = str(self.Custumer_code1.name)+"-"+str(self.numb)+"-"+str(self.row)
		"""Override default Odoo create function and extend."""
		# Do your custom logic here
		return super(ResPartners, self).create(vals)
	@api.multi
	def write(self, vals):
		#vals['ref'] = str(self.Custumer_code1.name)+"-"+str(self.numb1)+""+str(self.row)
		#vals['reffer'] = str(self.Custumer_code1.name)+"-"+str(self.numb1)+""+str(self.row)
		vals['customer_number'] = str(self.Custumer_code1.name)+"-"+str(self.numb1)+""+str(self.row)
		vals['vendor_number'] = str(self.Vendor_code1.name)+"-"+str(self.numb)+""+str(self.ratey)
		#vals['reffer'] = str(self.Custumer_code1.name)+"-"+str(self.numb)+"-"+str(self.row)
		"""Override default Odoo write function and extend."""
		# Do your custom logic here
		return super(ResPartners, self).write(vals)
	@api.constrains('supplier')
	def _check_release_check_sale_su(self):
			if self.supplier == False and self.customer == False:
				raise models.ValidationError('please check or enable any:customer for sale or vendor for purchase ')
			if self.supplier == True and self.customer == True:
				raise models.ValidationError('please check or enable any one customer for sale or vendor for purchase ')'''
_sql_constraints = [('product_code_uniq', 'unique (ref_code)', "The code ID must be unique, this one is already assigned to another partner.")]
