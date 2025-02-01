from odoo import fields, models, api
from odoo.exceptions import UserError, ValidationError
from datetime import date

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

    @api.onchange('attachment')
    def _onchange_attachment(self):
        for record in self:
            if record.attachment:
                record.state = 'new'

    def action_approve(self):
        for record in self:
            record.write({'state': 'approved'})

    def action_reject(self):
        for record in self:
            record.write({'state': 'rejected'})

class LoanTag(models.Model):
    _name = 'loan.tag'
    _description = 'Loan Tag'

    name = fields.Char(string='Name', required=True)
    color = fields.Integer(string='Color')

    _sql_constraints = [('unique_tag_name', 'UNIQUE(name)', 'Tag name must be unique!')]

class LoanApplication(models.Model):
    _name = "loan.application"
    _description = "Loan Application"

    name = fields.Char(string="Application Number", required=True)
    currency_id = fields.Many2one(comodel_name="res.currency", related='sale_order_id.currency_id',
    store=True,string="Currency")

    date_application = fields.Date(string="Application Date")
    date_approval = fields.Date(string="Approval Date")
    date_rejection = fields.Date(string="Rejection Date")
    date_signed = fields.Date(string="Signed Date")

    down_payment = fields.Monetary(string="Down Payment", required=True, currency_field="currency_id")
    interest_rate = fields.Float(string="Interest Rate (%)", required=True, digits=(5, 2))
    loan_amount = fields.Monetary(
        string="Loan Amount",
        compute='_compute_loan_amount',
        inverse='_inverse_loan_amount',
        store=True,
        currency_field="currency_id"
    )
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
    document_ids = fields.One2many('loan.document', 'application_id', string='Documents')
    partner_id = fields.Many2one(
        'res.partner',
        related='sale_order_id.partner_id',
        store=True,
        string='Customer'
    )
    sale_order_id = fields.Many2one('sale.order', string='Sale Order', required=False)  # False temporal
    tag_ids = fields.Many2many('loan.tag', string='Tags')
    user_id = fields.Many2one(
        'res.users',
        related='sale_order_id.user_id',
        store=True,
        string='Salesperson'
    )
    document_count = fields.Integer(
        string="Required Documents",
        compute='_compute_document_count',
        store=True
    )
    document_count_approved = fields.Integer(
        string="Approved Documents",
        compute='_compute_document_count_approved',
        store=True
    )
    sale_order_total = fields.Monetary(
        string="Sale Order Total",
        related='sale_order_id.amount_total',
        store=True,
        currency_field='currency_id'
    )

    _sql_constraints = [
        ('check_down_payment', 'CHECK(down_payment >= 0)', 'Down payment cannot be negative!'),
        ('check_loan_amount', 'CHECK(loan_amount >= 0)', 'Loan amount cannot be negative!')
    ]

    @api.depends('sale_order_total', 'down_payment')
    def _compute_loan_amount(self):
        for record in self:
            record.loan_amount = record.sale_order_total - record.down_payment

    @api.depends('sale_order_total', 'loan_amount')
    def _compute_down_payment(self):
        for record in self:
            record.down_payment = record.sale_order_total - record.loan_amount

    def _inverse_loan_amount(self):
        for record in self:
            record.down_payment = record.sale_order_total - record.loan_amount

    def _inverse_down_payment(self):
        for record in self:
            record.loan_amount = record.sale_order_total - record.down_payment

    @api.depends('document_ids', 'document_ids.state')
    def _compute_document_count(self):
        for record in self:
            record.document_count = len(record.document_ids)
            record.document_count_approved = len(
                record.document_ids.filtered(lambda d: d.state == 'approved')
            )

    def action_send(self):
        self.ensure_one()
        if not all(doc.state == 'approved' for doc in self.document_ids):
            raise UserError('All documents must be approved before sending.')
        
        return self.write({'state': 'sent', 'date_application': fields.Date.today()})

    def action_approve(self):
        self.ensure_one()
        return self.write({'state': 'approved', 'date_approval': fields.Date.today()})

    def action_reject(self):
        self.ensure_one()
        return self.write({'state': 'rejected', 'date_rejection': fields.Date.today()})

    @api.constrains('down_payment', 'sale_order_total')
    def _check_down_payment_limit(self):
        for record in self:
            if record.down_payment > record.sale_order_total:
                raise ValidationError('Down payment cannot be greater than the sale order total amount!')
    