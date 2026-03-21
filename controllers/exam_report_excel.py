from odoo import http
from odoo.http import request
import io
import xlsxwriter


class ExamExcelReport(http.Controller):

    @http.route('/exam/export_excel/<int:record_id>', type='http', auth='user')
    def export_excel(self, record_id=None, **kwargs):

        record = request.env['student.exam'].browse(record_id)

        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet('Exam Report')

        bold = workbook.add_format({'bold': True})

        # header
        sheet.write('A1', 'Name', bold)
        sheet.write('B1', 'Student', bold)
        sheet.write('C1', 'Exam Date', bold)
        sheet.write('D1', 'Score', bold)

        # data
        sheet.write('A2', record.name or '')
        sheet.write('B2', record.student_name or '')
        sheet.write('C2', str(record.exam_date or ''))
        sheet.write('D2', record.score or 0)

        workbook.close()
        output.seek(0)

        return request.make_response(
            output.read(),
            headers=[
                ('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
                ('Content-Disposition', 'attachment; filename=exam_report.xlsx;')
            ]
        )