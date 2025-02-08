from odoo import models, fields, api

class ResPartner(models.Model):
    _inherit = 'res.partner'


    application_ids = fields.One2many('loan.application', 'partner_id', string="Loan Applications")
    application_count = fields.Integer(string="Loan Applications Count", compute="_compute_application_count")

    @api.depends('application_ids')
    def _compute_application_count(self):
        for partner in self:
            partner.application_count = len(partner.application_ids)

    def action_view_applications(self):
        self.ensure_one()
        action = self.env.ref('loan_application.action_loan_application').read()[0]
        action.update({
            'domain': [('partner_id', '=', self.id)],
            'context': {
                'default_partner_id': self.id,
                'search_default_partner_id': self.id
            },
            'views': [
                (self.env.ref('loan_application.loan_application_list_view').id, 'list'),
                (self.env.ref('loan_application.loan_application_form_view').id, 'form')
            ]
        })
        return action