from odoo import api, fields, models, _


class EquipmentCategory(models.Model):
    _name = "equipment.category"
    _description = "Equipment Category"
    _parent_name = "parent_id"
    _parent_store = True
    _order = "complete_name"

    name = fields.Char(string="Name", required=True)
    complete_name = fields.Char(
        string="Full Name",
        compute='_compute_complete_name',
        recursive=True,
        store=True,
    )
    parent_id = fields.Many2one(
        'equipment.category',
        string='Parent Category',
        index=True,
        ondelete='cascade',
    )
    parent_path = fields.Char(index=True)
    child_ids = fields.One2many(
        'equipment.category',
        'parent_id',
        string='Child Categories',
    )
    code = fields.Char(string="Code")
    description = fields.Text(string="Description")
    request_count = fields.Integer(
        compute='_compute_request_count',
        string="Request Count",
    )

    @api.depends('name', 'parent_id.complete_name')
    def _compute_complete_name(self):
        for category in self:
            if category.parent_id:
                category.complete_name = '%s / %s' % (category.parent_id.complete_name, category.name)
            else:
                category.complete_name = category.name

    def _compute_request_count(self):
        for cat in self:
            cat.request_count = self.env['equipment.request'].search_count(
                [('category_id', '=', cat.id)]
            )

    @api.constrains('parent_id')
    def _check_category_recursion(self):
        if not self._check_recursion():
            raise models.ValidationError(_('You cannot create recursive categories.'))
