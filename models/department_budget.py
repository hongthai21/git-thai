from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class DepartmentBudget(models.Model):
    _name = "department.budget"
    _description = "Department Budget"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'display_name'

    department = fields.Selection(
        [
            ('hr', 'HR'),
            ('it', 'IT'),
            ('accounting', 'Accounting'),
            ('sales', 'Sales'),
        ],
        string='Department',
        required=True,
        tracking=True,
    )
    fiscal_year = fields.Char(
        string="Fiscal Year",
        required=True,
        default=lambda self: str(fields.Date.today().year),
    )
    total_budget = fields.Float(string="Total Budget", tracking=True)
    used_budget = fields.Float(
        string="Used Budget",
        compute='_compute_used_budget',
        store=True,
    )
    remaining_budget = fields.Float(
        string="Remaining Budget",
        compute='_compute_used_budget',
        store=True,
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        default=lambda self: self.env.company.currency_id.id,
    )
    display_name = fields.Char(
        compute='_compute_display_name',
        store=True,
    )
    usage_percentage = fields.Float(
        string='Usage Percentage',
        compute='_compute_usage_percentage',
        store=True,
    )

    _sql_constraints = [
        ('check_total_budget', 'CHECK(total_budget >= 0)', 'Total budget must be non-negative!'),
        ('unique_department_year', 'UNIQUE(department, fiscal_year)', 'Each department can only have one budget per fiscal year!'),
    ]

    @api.depends('used_budget', 'total_budget')
    def _compute_usage_percentage(self):
        for budget in self:
            if budget.total_budget:
                budget.usage_percentage = min((budget.used_budget / budget.total_budget) * 100.0, 100.0)
            else:
                budget.usage_percentage = 0.0

    @api.depends('department', 'fiscal_year')
    def _compute_display_name(self):
        dept_labels = dict(self._fields['department'].selection)
        for rec in self:
            dept_name = dept_labels.get(rec.department, rec.department or '')
            rec.display_name = f"{dept_name} - {rec.fiscal_year}"

    @api.depends('total_budget')
    def _compute_used_budget(self):
        for rec in self:
            approved_requests = self.env['equipment.request'].search([
                ('department', '=', rec.department),
                ('state', 'in', ['director_approved', 'done', 'assigned']),
                ('request_date', '>=', f'{rec.fiscal_year}-01-01'),
                ('request_date', '<=', f'{rec.fiscal_year}-12-31'),
            ])
            rec.used_budget = sum(approved_requests.mapped('estimated_cost'))
            rec.remaining_budget = rec.total_budget - rec.used_budget
