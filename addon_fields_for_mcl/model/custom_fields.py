from odoo import api, fields, models

class PortOrder(models.Model):
	_name = 'port.order'

	name = fields.Char('Name')
	city = fields.Char('City')
	country = fields.Many2one('res.country','Country')

class ExportShipment(models.Model):
	_name = 'export.shipment'
	
	name = fields.Char('Name')

class ContainerType(models.Model):
	_name = 'type.container'
	name = fields.Char('Name')


class CustomerTag(models.Model):
	_name = 'cust.name'

	name = fields.Char(string='Customer Tag')
	z_description = fields.Char(string='Description')

class ProjectSite(models.Model):
    _name = 'site.name'

    name = fields.Char(string='Project Site')
    z_description = fields.Char(string='Description')


class CustomFields(models.Model):
    _name = "custom.fields"
    name= fields.Char(string='Name',store=True ,index=True,ondelete='cascade')


class OfficeName(models.Model):
    _name = 'office.name'

    name = fields.Char('Sale Office')
    z_description = fields.Char('Description')
    z_check = fields.Boolean('Check',default=True)

class ReasonName(models.Model):
	_name = 'reason.name'

	name = fields.Char(string='Reason')
	
   