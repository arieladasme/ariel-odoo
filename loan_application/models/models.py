from odoo import fields, models

class LoanDocument(models.Model):
    _name = 'loan.document'
    _description = 'Loan Document'

    name = fields.Char(string='Name', required=True)
    application_id = fields.Many2one('loan.application', string='Application')
    attachment = fields.Binary(string='File')
    type = fields.Char(string='Type')
    state = fields.Selection([
        ('new', 'New'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ], string='State', required=True, default='new')

class LoanTag(models.Model):
    _name = 'loan.tag'
    _description = 'Loan Tag'

    name = fields.Char(string='Name', required=True)
    color = fields.Integer(string='Color')

class LoanApplication(models.Model):
    _name = "loan.application"
    _description = "Loan Application"

    name = fields.Char(string="Application Number", required=True)
    currency_id = fields.Many2one(comodel_name="res.currency", string="Currency")

    date_application = fields.Date(string="Application Date")
    date_approval = fields.Date(string="Approval Date")
    date_rejection = fields.Date(string="Rejection Date")
    date_signed = fields.Date(string="Signed Date")

    down_payment = fields.Monetary(string="Down Payment", required=True, currency_field="currency_id")
    interest_rate = fields.Float(string="Interest Rate (%)", required=True, digits=(5, 2))
    loan_amount = fields.Monetary(string="Loan Amount", required=True, currency_field="currency_id")
    loan_term = fields.Integer(string="Loan Term (months)", required=True, default=36)
    rejection_reason = fields.Text(string="Rejection Reason")
    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('sent', 'Sent'),
            ('review', 'Credit Check'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected'),
            ('signed', 'Signed'),
            ('cancel', 'Canceled')
        ],
        string='Status',
        default='draft'
    )
    notes = fields.Text(string="Notes")
    # Campos relacionados
    document_ids = fields.One2many('loan.document', 'application_id', string='Documents')
    partner_id = fields.Many2one('res.partner', string='Customer')
    sale_order_id = fields.Many2one('sale.order', string='Sale Order', required=False)  # False temporal
    tag_ids = fields.Many2many('loan.tag', string='Tags')
    user_id = fields.Many2one('res.users', string='Salesperson')


