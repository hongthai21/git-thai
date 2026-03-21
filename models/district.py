from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

class District(models.Model):
    _name = 'district'
    _description = 'District'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(required=True)

    province_id = fields.Many2one(
        'province',
        string="Province"
    )

    is_active = fields.Boolean(
        default=True
    )

    ward_ids = fields.One2many(
        'ward',
        'district_id'
    )