from odoo import fields, models


class EstateProperty(models.Model):
    _name = "estate.property"
    _description = "Estate Property"

    
    name = fields.Char()
    description = fields.Text()
    postcode = fields.Char()        
    date_availability = fields.Date()
    expected_price = fields.Float()
    selling_price = fields.Float()
    bedrooms = fields.Integer(default=2)
    living_area = fields.Integer()
    facades = fields.Integer()
    garage = fields.Boolean()
    garden = fields.Boolean()
    garden_area = fields.Integer()
    garden_orientation = fields.Selection(
        selection=[('north', 'North'),
                  ('south', 'South'),
                  ('east', 'East'),
                  ('west', 'West'),])
    # Reserved Fields
    active = fields.Boolean(default=True)
    state = fields.Selection(
        selection=[('new', 'New'),
                  ('received', 'Offer Received'),
                  ('accepted', 'Offer Accepted'),
                  ('sold', 'Sold'),
                  ('canceled', 'Canceled'),],
        default ="new")