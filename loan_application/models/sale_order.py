from odoo import models, fields, _
from odoo.exceptions import ValidationError

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

        # Verificar restricciones de motocicletas
        self._check_motorcycle_products()

        # Verificar si ya existe una aplicación de préstamo
        if self.loan_application_ids:
            raise ValidationError(_(
                'A loan application already exists for this sale order.'
            ))

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

    def _check_motorcycle_products(self):
        self.ensure_one()
        motorcycle_category = self.env.ref('loan_application.product_category_motorcycle', raise_if_not_found=False)

        if not motorcycle_category:
            raise ValidationError(_('Motorcycle category is not configured in the system.'))

        motorcycle_products = self.order_line.filtered(
            lambda line: line.product_id.categ_id == motorcycle_category
        )

        # Verificar si hay al menos una motocicleta
        if not motorcycle_products:
            raise ValidationError(_(
                'Cannot create loan application: No motorcycle products found in the order.'
            ))

        # Verificar si hay más de una motocicleta
        if len(motorcycle_products) > 1:
            raise ValidationError(_(
                'Cannot create loan application: Only one motorcycle per order is allowed.'
            ))

        return True