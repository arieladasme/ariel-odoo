from odoo import fields, models


class LoanAplication(models.Model):
    _name = "loan.application"
    _description = "Loan Application"

    client = fields.Char(string="Cliente")
    seller = fields.Char(string="Vendedor")
    # sale_order = fields.Many2one("sale.order", string="Orden de Venta")
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('submitted', 'Presentado'),
        ('approved', 'Aprobado'),
        ('rejected', 'Rechazado')
    ], string='Estado', default='draft')
    request_date = fields.Date(string="Fecha de Solicitud")
    approval_date = fields.Date(string="Fecha de Aprobación")

    # TODO: agregar campo etiqueta y documentos justificativos
