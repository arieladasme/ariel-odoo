from odoo import fields, models


class LoanApplication(models.Model):
    _name = "loan.application"
    _description = "Loan Application"

    name = fields.Char(string="Name")
    client = fields.Char(string="Client")
    seller = fields.Char(string="Seller")
    # sale_order = fields.Many2one("sale.order", string="Orden de Venta")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ], string='Estado', default='draft')
    request_date = fields.Date(string="Request Date")
    approval_date = fields.Date(string="Approval Date")

    # TODO: agregar campo etiqueta y documentos justificativos
