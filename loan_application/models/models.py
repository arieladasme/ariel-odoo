from odoo import fields, models, api
from odoo.exceptions import UserError, ValidationError
from datetime import date


class LoanApplication(models.Model):
    _name = "loan.application"
    _description = "Loan Application"
    _order = "date_application desc, id desc"

    _sql_constraints = [
        ('check_down_payment', 'CHECK(down_payment >= 0)', 'Down payment cannot be negative!'),
        ('check_loan_amount', 'CHECK(loan_amount >= 0)', 'Loan amount cannot be negative!')
    ]

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
            if record.sale_order_total:
                safe_down_payment = min(record.down_payment or 0, record.sale_order_total)
                record.loan_amount = max(0, record.sale_order_total - safe_down_payment)
            else:
                record.loan_amount = 0.0

    @api.depends('sale_order_total', 'loan_amount')
    def _compute_down_payment(self):
        for record in self:
            if record.sale_order_total:
                safe_loan_amount = min(record.loan_amount or 0, record.sale_order_total)
                record.down_payment = max(0, record.sale_order_total - safe_loan_amount)
            else:
                record.down_payment = 0.0

    def _inverse_loan_amount(self):
        for record in self:
            if record.sale_order_total:
                safe_loan_amount = min(max(0, record.loan_amount or 0), record.sale_order_total)
                record.down_payment = max(0, record.sale_order_total - safe_loan_amount)
            else:
                record.down_payment = 0.0

    def _inverse_down_payment(self):
        for record in self:
            if record.sale_order_total:
                safe_down_payment = min(max(0, record.down_payment or 0), record.sale_order_total)
                record.loan_amount = max(0, record.sale_order_total - safe_down_payment)
            else:
                record.loan_amount = 0.0

    @api.onchange('down_payment', 'sale_order_total')
    def _onchange_down_payment(self):
        if self.down_payment and self.sale_order_total:
            if self.down_payment > self.sale_order_total:
                self.down_payment = self.sale_order_total
                return {
                    'warning': {
                        'title': 'Invalid Down Payment',
                        'message': 'The down payment cannot exceed the total sale amount. Please enter a valid down payment amount.'
                    }
                }

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
            if record.down_payment and record.sale_order_total:
                if record.down_payment > record.sale_order_total:
                    raise ValidationError('The down payment amount cannot exceed the total sale amount. Please enter a smaller down payment.')
                if record.down_payment < 0:
                    raise ValidationError('The down payment amount must be positive.')

    @api.depends('partner_id.name', 'sale_order_id.order_line.product_id.name')
    def _compute_display_name(self):
        super(LoanApplication, self)._compute_display_name()
        for property in self:
            partner_name = property.partner_id.name or "No customer"
            if property.sale_order_id and property.sale_order_id.order_line:
                product_names = property.sale_order_id.order_line.mapped('product_id.name')
                products_str = ', '.join(product_names)
            else:
                products_str = "No product"
            property.display_name = f"{partner_name} - {products_str}"

    @api.model_create_multi
    def create(self, vals_list):
        loans = super(LoanApplication, self).create(vals_list)

        # Obtengo documentos activos
        document_types = self.env['loan.application.document.type'].search([('active', '=', True)])

        # Creo documentos asociados para cada aplicación
        for loan in loans:
            documents = []
            for doc_type in document_types:
                documents.append({
                    'name': doc_type.name,
                    'application_id': loan.id,
                    'type': doc_type.name,
                    'state': 'new',
                })
            if documents:
                self.env['loan.document'].create(documents)

        return loans
    