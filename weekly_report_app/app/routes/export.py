from flask import Blueprint

bp = Blueprint('export', __name__, url_prefix='/export')

@bp.route('/')
def export_home():
    return "Export Page"


'''
from flask import Blueprint, render_template, make_response
from app.models import Report, Project, ProjectUpdate
from weasyprint import HTML

bp = Blueprint('export', __name__, url_prefix='/export')


@bp.route('/report/<int:report_id>/pdf')
def export_report_pdf(report_id):
    report = Report.query.get_or_404(report_id)
    rendered = render_template('export_report.html', report=report)
    pdf = HTML(string=rendered).write_pdf()
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'inline; filename=report_{report_id}.pdf'
    return response

'''