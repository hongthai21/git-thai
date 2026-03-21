from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

class Ward(models.Model):
    _name = 'ward'
    _description = 'Ward'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(required=True)

    district_id = fields.Many2one(
        'district',
        string="District"
    )

    active = fields.Boolean(default=True)