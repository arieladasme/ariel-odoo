from odoo import fields, models


class LoanApplication(models.Model):
    _name = "loan.application"
    _description = "Loan Application"

    name = fields.Char(string="Application Number", required=True)
    currency_id = fields.Many2one(comodel_name="res.currency", string="Currency")

    date_application = fields.Date(string="Application Date")
    date_approval = fields.Date(string="Approval Date")
    date_rejection = fields.Date(string="Rejection Date")
    date_signed = fields.Date(string="Signed Date")

    dowm_payment = fields.Monetary(string="Down Payment", required=True, currency_field="currency_id")
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

    # client = fields.Char(string="Client")
    # seller = fields.Char(string="Seller")
    # sale_order = fields.Many2one("sale.order", string="Orden de Venta")
    # TODO: agregar campo etiqueta y documentos justificativos
