from odoo import api, models, fields


class EquipmentRequestLine(models.Model):
    _name = "equipment.request.line"
    _description = "Equipment Request Line"

    request_id = fields.Many2one(
        'equipment.request',
        string='Request Reference',
        required=True,
        ondelete='cascade',
    )
    product_id = fields.Many2one(
        'product.product',
        string='Product',
    )
    description = fields.Char(string='Description')
    quantity = fields.Integer(string='Quantity', default=1)
    unit_price = fields.Float(string='Unit Price')
    subtotal = fields.Float(
        string='Subtotal',
        compute='_compute_subtotal',
        store=True,
    )

    @api.depends('quantity', 'unit_price')
    def _compute_subtotal(self):
        for line in self:
            line.subtotal = line.quantity * line.unit_price
