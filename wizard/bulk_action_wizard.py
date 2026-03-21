from odoo import api, fields, models, _
from odoo.exceptions import UserError


class BulkActionWizard(models.TransientModel):
    _name = 'equipment.bulk.action.wizard'
    _description = 'Bulk Action Wizard'

    action_type = fields.Selection(
        [
            ('manager_approve', 'Manager Approve'),
            ('director_approve', 'Director Approve'),
            ('refuse', 'Refuse'),
            ('done', 'Mark as Done'),
        ],
        string='Action',
        required=True,
    )
    refuse_reason = fields.Text(string="Refuse Reason")
    request_ids = fields.Many2many(
        'equipment.request',
        string='Requests',
    )

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        active_ids = self.env.context.get('active_ids', [])
        res['request_ids'] = [(6, 0, active_ids)]
        return res

    def action_apply(self):
        if not self.request_ids:
            raise UserError(_("No requests selected!"))

        count = 0
        errors = []
        for req in self.request_ids:
            try:
                if self.action_type == 'manager_approve':
                    if req.state == 'confirmed':
                        req.action_manager_approve()
                        count += 1
                    else:
                        errors.append(_("%s: not in 'Confirmed' state") % req.name)
                elif self.action_type == 'director_approve':
                    if req.state == 'manager_approved':
                        req.action_director_approve()
                        count += 1
                    else:
                        errors.append(_("%s: not in 'Manager Approved' state") % req.name)
                elif self.action_type == 'refuse':
                    if req.state in ('confirmed', 'manager_approved'):
                        req.refuse_reason = self.refuse_reason
                        req.action_refuse()
                        count += 1
                    else:
                        errors.append(_("%s: not in a refusable state") % req.name)
                elif self.action_type == 'done':
                    if req.state == 'director_approved':
                        req.action_done()
                        count += 1
                    else:
                        errors.append(_("%s: not in 'Director Approved' state") % req.name)
            except Exception as e:
                errors.append(_("%s: %s") % (req.name, str(e)))

        message = _("✅ Successfully processed %d request(s).") % count
        if errors:
            message += "\n\n⚠️ " + _("Skipped:\n") + "\n".join(errors)

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Bulk Action Result'),
                'message': message,
                'type': 'success' if not errors else 'warning',
                'sticky': True,
                'next': {'type': 'ir.actions.act_window_close'},
            }
        }
