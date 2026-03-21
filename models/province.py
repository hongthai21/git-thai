from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

class Province(models.Model):
    _name = 'province'
    _description = 'Province'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='name',required=True)

    district_ids = fields.One2many(
        'district',
        'province_id'
    )