from odoo import models, fields
from odoo.exceptions import UserError, ValidationError

class StudentExamLine(models.Model):
    _name = "student.exam.line"
    _description = "Student Exam Line"
    _rec_name = "subject"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    exam_id = fields.Many2one("student.exam",string="Exam")
    subject = fields.Char(string="Subject")
    score = fields.Float(string="Score")

