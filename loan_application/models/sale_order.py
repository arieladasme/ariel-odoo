from odoo import models, fields, _

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    loan_application_ids = fields.One2many(
        'loan.application',
        'sale_order_id',
        string='Loan Applications'
    )

    state = fields.Selection(
        selection_add=[('loan_applied', 'Applied for Loan')],
        ondelete={'loan_applied': 'set default'}
    )

    def action_create_loan_application(self):
        """Create a new loan application from sale order"""
        self.ensure_one()
        
        # Prepare context with default values from sale order
        ctx = {
            'default_sale_order_id': self.id,
            'default_partner_id': self.partner_id.id,
            'default_sale_order_total': self.amount_total,
            'default_currency_id': self.currency_id.id,
            'default_user_id': self.user_id.id,
            'default_name': f'Loan/{self.name}',
            'default_state': 'draft'
        }

        # Update sale order state
        self.write({'state': 'loan_applied'})

        # Return action to open loan application form
        return {
            'type': 'ir.actions.act_window',
            'name': _('New Loan Application'),
            'res_model': 'loan.application',
            'view_mode': 'form',
            'target': 'current',
            'context': ctx
        }