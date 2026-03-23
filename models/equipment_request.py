from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class EquipmentRequest(models.Model):
    _name = "equipment.request"
    _description = "Equipment Request"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'priority desc, id desc'

    # === Core Fields ===
    name = fields.Char(
        string="Reference", tracking=True, readonly=True,
        copy=False, default=lambda self: _('New'),
    )
    employee_name = fields.Char(string="Employee", tracking=True)
    equipment_name = fields.Char(string="Equipment", tracking=True)
    quantity = fields.Integer(string="Quantity")
    request_date = fields.Date(string="Request Date", default=fields.Date.today)
    deadline = fields.Date(string="Deadline", tracking=True)
    note = fields.Text(string="Manager Note")
    description = fields.Html(string="Description")

    # === Category & Cost ===
    category_id = fields.Many2one(
        'equipment.category', string='Equipment Category',
        tracking=True,
    )
    estimated_cost = fields.Float(
        string="Estimated Cost",
        tracking=True,
        help="Estimated total cost to check against department budget.",
    )
    currency_id = fields.Many2one(
        'res.currency', string='Currency',
        default=lambda self: self.env.company.currency_id.id,
    )

    # === Department ===
    department = fields.Selection(
        [
            ('hr', 'HR'),
            ('it', 'IT'),
            ('accounting', 'Accounting'),
            ('sales', 'Sales'),
        ],
        string='Department', tracking=True,
    )

    # === Multi-Level Approval ===
    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('confirmed', 'Confirmed'),
            ('manager_approved', 'Manager Approved'),
            ('director_approved', 'Director Approved'),
            ('done', 'Done'),
            ('assigned', 'Assigned'),
            ('returned', 'Returned'),
            ('refused', 'Refused'),
        ],
        default='draft', string="Status", tracking=True,
    )
    manager_id = fields.Many2one('res.users', string='Approved by Manager', tracking=True)
    director_id = fields.Many2one('res.users', string='Approved by Director', tracking=True)
    confirmed_date = fields.Datetime(string="Confirmed Date")
    manager_approved_date = fields.Datetime(string="Manager Approved Date")
    director_approved_date = fields.Datetime(string="Director Approved Date")
    refused_by = fields.Many2one('res.users', string='Refused By', tracking=True)
    refused_date = fields.Datetime(string="Refused Date")
    refuse_reason = fields.Text(string="Refuse Reason")

    # === Return & Assignment ===
    assigned_date = fields.Date(string="Assigned Date")
    return_date = fields.Date(string="Return Date")
    return_condition = fields.Selection(
        [
            ('good', 'Good Condition'),
            ('damaged', 'Damaged'),
            ('lost', 'Lost'),
        ],
        string='Return Condition',
    )

    # === Others ===
    gender = fields.Selection(
        [('male', 'Male'), ('female', 'Female')],
        string='Gender', default='male',
    )
    priority = fields.Selection(
        [('0', 'Normal'), ('1', 'Low'), ('2', 'High'), ('3', 'Urgent')],
        string='Priority', default='0',
    )
    pet_image = fields.Image(
        string="Image", max_width=1024, max_height=1024,
    )

    # === Equipment Lines ===
    line_ids = fields.One2many(
        'equipment.request.line', 'request_id', string='Equipment Lines',
    )
    total_quantity = fields.Integer(
        string="Total Quantity", compute='_compute_total_quantity', store=True,
    )
    line_count = fields.Integer(
        string="Items Count", compute='_compute_total_quantity', store=True,
    )
    total_cost = fields.Float(
        string="Total Lines Cost",
        compute='_compute_total_cost',
        store=True,
    )

    # === Smart Button: previous requests ===
    previous_request_count = fields.Integer(
        string="Previous Requests", compute='_compute_previous_request_count',
    )

    # === UI Enhancement Fields ===
    progress = fields.Float(
        string="Approval Progress",
        compute='_compute_progress',
        store=True,
        help="Percentage of completion in the approval workflow.",
    )
    is_overdue = fields.Boolean(
        string="Is Overdue",
        compute='_compute_is_overdue',
        search='_search_is_overdue',
    )
    kanban_color = fields.Integer(
        string="Kanban Color",
        compute='_compute_kanban_color',
    )

    _sql_constraints = [
        ('check_quantity', 'CHECK(quantity >= 0)', 'Quantity must be positive!'),
        ('check_estimated_cost', 'CHECK(estimated_cost >= 0)', 'Estimated cost must be positive!'),
    ]

    # ==================== COMPUTED ====================
    @api.depends('line_ids.quantity', 'quantity')
    def _compute_total_quantity(self):
        for rec in self:
            if rec.line_ids:
                rec.total_quantity = sum(rec.line_ids.mapped('quantity'))
                rec.line_count = len(rec.line_ids)
            else:
                rec.total_quantity = rec.quantity
                rec.line_count = 0

    @api.depends('line_ids.subtotal')
    def _compute_total_cost(self):
        for rec in self:
            rec.total_cost = sum(rec.line_ids.mapped('subtotal'))

    def _compute_previous_request_count(self):
        for rec in self:
            if rec.employee_name:
                rec.previous_request_count = self.search_count([
                    ('employee_name', '=', rec.employee_name),
                    ('id', '!=', rec.id),
                ])
            else:
                rec.previous_request_count = 0

    @api.depends('state')
    def _compute_progress(self):
        progress_map = {
            'draft': 10,
            'confirmed': 25,
            'manager_approved': 50,
            'director_approved': 75,
            'done': 85,
            'assigned': 100,
            'returned': 100,
            'refused': 0,
        }
        for rec in self:
            rec.progress = progress_map.get(rec.state, 0)

    @api.depends('deadline', 'state')
    def _compute_is_overdue(self):
        today = fields.Date.today()
        for rec in self:
            if rec.deadline and rec.state not in ('done', 'assigned', 'returned', 'refused'):
                rec.is_overdue = rec.deadline < today
            else:
                rec.is_overdue = False

    def _search_is_overdue(self, operator, value):
        today = fields.Date.today()
        if (operator == '=' and value) or (operator == '!=' and not value):
            return [
                ('deadline', '<', today),
                ('state', 'not in', ['done', 'assigned', 'returned', 'refused']),
            ]
        return [
            '|',
            ('deadline', '>=', today),
            ('deadline', '=', False),
        ]

    def _compute_kanban_color(self):
        color_map = {
            'draft': 0,
            'confirmed': 4,
            'manager_approved': 2,
            'director_approved': 10,
            'done': 10,
            'assigned': 7,
            'returned': 1,
            'refused': 9,
        }
        for rec in self:
            rec.kanban_color = color_map.get(rec.state, 0)

    @api.model
    def _group_expand_states(self, states, domain):
        """Explicitly define valid Kanban columns to prevent stale DB values from creating invalid columns."""
        return ['draft', 'confirmed', 'manager_approved', 'director_approved', 'done', 'assigned', 'returned', 'refused']

    # ==================== CRUD ====================
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('name') or vals['name'] == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('equipment.request') or _('New')
            if vals.get('quantity', 0) < 0:
                raise ValidationError(_("Quantity must be positive!"))
            if not vals.get('request_date'):
                vals['request_date'] = fields.Date.today()
        return super().create(vals_list)

    def write(self, vals):
        for record in self:
            if record.state in ('director_approved', 'done', 'assigned'):
                if 'equipment_name' in vals or 'quantity' in vals or 'estimated_cost' in vals:
                    raise ValidationError(
                        _("Cannot modify equipment details on an approved/completed request!")
                    )
        return super().write(vals)

    # ==================== BUDGET CHECK ====================
    def _check_budget(self):
        """Check if department has enough budget for this request."""
        self.ensure_one()
        if not self.department or not self.estimated_cost:
            return
        year = str(self.request_date.year) if self.request_date else str(fields.Date.today().year)
        budget = self.env['department.budget'].search([
            ('department', '=', self.department),
            ('fiscal_year', '=', year),
        ], limit=1)
        if budget and budget.remaining_budget < self.estimated_cost:
            raise ValidationError(
                _("Insufficient budget for department %s!\n"
                  "Remaining: %s, Requested: %s") % (
                    self.department.upper(),
                    budget.remaining_budget,
                    self.estimated_cost,
                )
            )

    # ==================== MAIL HELPERS ====================
    def _send_notification(self, subject, body, partner_ids=None):
        """Send internal notification via chatter."""
        self.ensure_one()
        self.message_post(
            body=body,
            subject=subject,
            message_type='notification',
            subtype_xmlid='mail.mt_note',
            partner_ids=partner_ids or [],
        )

    # ==================== WORKFLOW BUTTONS ====================
    def action_confirm(self):
        for record in self:
            record.write({
                'state': 'confirmed',
                'confirmed_date': fields.Datetime.now(),
            })
            record._send_notification(
                subject=_("Equipment Request Confirmed"),
                body=_("Request <b>%s</b> has been confirmed by <b>%s</b> and is waiting for Manager approval.") % (
                    record.name, self.env.user.name),
            )

    def action_manager_approve(self):
        for record in self:
            record.write({
                'state': 'manager_approved',
                'manager_id': self.env.uid,
                'manager_approved_date': fields.Datetime.now(),
            })
            record._send_notification(
                subject=_("Manager Approved"),
                body=_("Request <b>%s</b> has been approved by Manager <b>%s</b>. Waiting for Director's final approval.") % (
                    record.name, self.env.user.name),
            )

    def action_director_approve(self):
        for record in self:
            record._check_budget()
            record.write({
                'state': 'director_approved',
                'director_id': self.env.uid,
                'director_approved_date': fields.Datetime.now(),
            })
            record._send_notification(
                subject=_("Director Approved"),
                body=_("Request <b>%s</b> has been finally approved by Director <b>%s</b>. Ready to be fulfilled.") % (
                    record.name, self.env.user.name),
            )

    def action_done(self):
        for record in self:
            record.state = 'done'
            record._send_notification(
                subject=_("Request Completed"),
                body=_("Request <b>%s</b> has been marked as Done.") % record.name,
            )

    def action_assign(self):
        for record in self:
            record.write({
                'state': 'assigned',
                'assigned_date': fields.Date.today(),
            })
            record._send_notification(
                subject=_("Equipment Assigned"),
                body=_("Equipment for request <b>%s</b> has been assigned to <b>%s</b>.") % (
                    record.name, record.employee_name),
            )

    def action_return(self):
        for record in self:
            if not record.return_condition:
                raise UserError(_("Please select the Return Condition before returning."))
            record.write({
                'state': 'returned',
                'return_date': fields.Date.today(),
            })
            record._send_notification(
                subject=_("Equipment Returned"),
                body=_("Equipment for request <b>%s</b> has been returned. Condition: <b>%s</b>.") % (
                    record.name, record.return_condition),
            )

    def action_refuse(self):
        for record in self:
            record.write({
                'state': 'refused',
                'refused_by': self.env.uid,
                'refused_date': fields.Datetime.now(),
            })
            record._send_notification(
                subject=_("Request Refused"),
                body=_("Request <b>%s</b> has been refused by <b>%s</b>. Reason: %s") % (
                    record.name, self.env.user.name, record.refuse_reason or 'N/A'),
            )

    def action_reset_draft(self):
        for record in self:
            record.write({
                'state': 'draft',
                'manager_id': False,
                'director_id': False,
                'confirmed_date': False,
                'manager_approved_date': False,
                'director_approved_date': False,
                'refused_by': False,
                'refused_date': False,
                'refuse_reason': False,
            })

    # === Smart Button: view previous requests ===
    def action_view_previous_requests(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Previous Requests by %s') % self.employee_name,
            'res_model': 'equipment.request',
            'view_mode': 'list,form',
            'domain': [('employee_name', '=', self.employee_name), ('id', '!=', self.id)],
            'context': {'create': False},
        }

    # === Cron: remind overdue ===
    @api.model
    def _cron_remind_overdue_requests(self):
        """Cron job: create activities for requests pending > 3 days."""
        three_days_ago = fields.Datetime.subtract(fields.Datetime.now(), days=3)
        overdue = self.search([
            ('state', 'in', ['confirmed', 'manager_approved']),
            ('confirmed_date', '<=', three_days_ago),
        ])
        for req in overdue:
            req.activity_schedule(
                'mail.mail_activity_data_todo',
                note=_("Request %s is pending approval for more than 3 days!") % req.name,
                user_id=req.create_uid.id,
            )

    @api.model
    def _cron_check_deadline(self):
        """Cron job: warn about requests past deadline."""
        today = fields.Date.today()
        overdue = self.search([
            ('deadline', '<', today),
            ('state', 'not in', ['done', 'assigned', 'returned', 'refused']),
        ])
        for req in overdue:
            req.activity_schedule(
                'mail.mail_activity_data_todo',
                note=_("⚠️ Request %s has passed its deadline (%s)!") % (req.name, req.deadline),
                user_id=req.create_uid.id,
            )