from odoo import models, fields, _
from odoo.exceptions import ValidationError, UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    loan_application_ids = fields.One2many('loan.application', 'sale_order_id', string='Loan Applications')
    state = fields.Selection(selection_add=[('loan_applied', 'Applied for Loan')], ondelete={'loan_applied': 'set default'})

    def action_apply_loan(self):
        self.ensure_one()

        motorcycle_product = self._get_motorcycle_product()

        if self.loan_application_ids:
            raise ValidationError(_('A loan application already exists for this sale order.'))

        ctx = {
            'default_sale_order_id': self.id,
            'default_product_id': motorcycle_product.product_id.id,
            'default_partner_id': self.partner_id.id,
            'default_sale_order_total': self.amount_total,
            'default_currency_id': self.currency_id.id,
            'default_user_id': self.user_id.id,
            'default_name': f'{self.partner_id.name} {motorcycle_product.product_id.name}',
            'default_state': 'draft'
        }

        self.write({'state': 'loan_applied'})

        return {
            'type': 'ir.actions.act_window',
            'name': _('New Loan Application'),
            'res_model': 'loan.application',
            'view_mode': 'form',
            'target': 'current',
            'context': ctx
        }

    def _get_motorcycle_product(self):
        self.ensure_one()
        motorcycle_category = self.env.ref('loan_application.product_category_motorcycle', raise_if_not_found=False)
        motorcycle_products = self.order_line.filtered(lambda line: line.product_id.categ_id == motorcycle_category)

        if not motorcycle_products:
            raise UserError(_('Cannot create loan application: No motorcycle products found in the order.'))

        if len(motorcycle_products) > 1:
            raise UserError(_('Cannot create loan application: Only one motorcycle per order is allowed.'))
        
        return motorcycle_products
