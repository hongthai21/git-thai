from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

class StudentExam(models.Model):
    _name = "student.exam"
    _description = "student exam"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Exam Name")
    student_name = fields.Char(string="Student")
    exam_date = fields.Date(string="Exam Date")
    score = fields.Float(string="Score")
    line_ids = fields.One2many(
        "student.exam.line",
        "exam_id",
        string="Subjects"
    )
    # state_id = fields.Many2one('res.country.state', string='State'
    def action_export_excel(self):
        return {
            'type': 'ir.actions.act_url',
            'url': '/exam/export_excel/%s' % self.id,
            'target': 'self',
        }


    def action_import_excel(self):
        print(self.id, 'mmmm')
        return {
            'type': 'ir.actions.act_window',
            'name': 'Import Excel',
            'res_model': 'import.excel.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {

                'record_id': self.id
            }
        }