from odoo import fields, models

class LoanTag(models.Model):
    _name = 'loan.tag'
    _description = 'Loan Tag'
    _order = "name"


    name = fields.Char(string='Name', required=True)
    color = fields.Integer(string='Color')

    _sql_constraints = [('unique_tag_name', 'UNIQUE(name)', 'Tag name must be unique!')]