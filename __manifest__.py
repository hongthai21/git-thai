{
    'name': "Equipment Request Management",
    'summary': """Advanced Equipment Request Management with Multi-Level Approval""",
    'description': """
        Hệ thống quản lý yêu cầu thiết bị nội bộ doanh nghiệp.
        - Phê duyệt đa cấp (Employee → Manager → Director)
        - Quản lý ngân sách phòng ban
        - Danh mục thiết bị phân cấp
        - Luồng cấp phát & trả thiết bị
        - Cron nhắc nhở tự động
        - Wizard duyệt hàng loạt
        - Phân quyền User/Manager/Director
        - PDF & Excel Report
        - Dashboard tổng quan
    """,
    'author': "hongthai",
    'website': "",
    'category': 'Human Resources/Equipment',
    'sequence': 4,
    'version': '19.0.4.0.0',
    'license': 'LGPL-3',
    'depends': [
        'product', 'base', 'mail',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/sequence_data.xml',
        'data/cron_data.xml',
        'data/province_data.xml',
        'data/district_data.xml',
        'views/equipment_dashboard_views.xml',
        'views/equipment_request_views.xml',
        'views/equipment_category_budget_views.xml',
        'views/citizen_view.xml',
        'views/district_view.xml',
        'views/province_view.xml',
        'views/ward_view.xml',
        'views/exam_views.xml',
        'report/exam_report.xml',
        'report/exam_report_template.xml',
        'report/equipment_request_report.xml',
        'report/equipment_request_report_template.xml',
        'wizard/import_excel_wizard.xml',
        'wizard/bulk_action_wizard.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'equipment_request/static/src/scss/equipment_request.scss',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
}
