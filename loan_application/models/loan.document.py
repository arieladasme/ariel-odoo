from odoo import fields, models, api

class LoanDocument(models.Model):
    _name = 'loan.document'
    _description = 'Loan Document'
    _order = "sequence, id"
    

    name = fields.Char(string='Name', required=True)
    application_id = fields.Many2one('loan.application', string='Application')
    attachment = fields.Binary(string='File')
    type = fields.Char(string='Type')
    state = fields.Selection([
        ('new', 'New'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ], string='State', required=True, default='new')
    sequence = fields.Integer(string='Sequence', default=10)

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