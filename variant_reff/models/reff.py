import uuid
from datetime import datetime

from itertools import groupby
from datetime import datetime, timedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError, AccessError
from odoo.osv import expression
from odoo.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT

from odoo.tools.misc import formatLang

from odoo.addons import decimal_precision as dp

# models : for get models features in your class
# fields: for declare fields
# api: for accessing decorators
# _ : translation
class ProductProduct(models.Model):
	_inherit = "product.product"
	default_code = fields.Char('Internal Reference', index=True,store = True,related = 'product_tmpl_id.default_code')

class ProductTemplate(models.Model):
	_inherit = "product.template"
	
