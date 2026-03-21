from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

class StudentExam(models.Model):
    _name = 'student.exam'
    _inherit = 'student.exam'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    def generate_xlsx_report(self, workbook, data, exams):

        sheet = workbook.add_worksheet('Exams')

        sheet.write(0, 0, 'Exam Name')
        sheet.write(0, 1, 'Student')
        sheet.write(0, 2, 'Score')

        row = 1

        for exam in exams:
            sheet.write(row, 0, exam.name)
            sheet.write(row, 1, exam.student_name)
            sheet.write(row, 2, exam.score)
            row += 1