{
    "name": "Solicitud de Préstamo",
    "summary": "Streamline the loan application process for dealerships working with third-party financing companies.",
    "version": "18.0.0.5.5",
    "category": "Kawiil/Custom Modules",
    "license": "OPL-1",
    "depends": ["base", "sale", "mail"],
    "data": [
        'security/motorcycle_financing_groups.xml',
        'security/rules.xml',
        'security/ir.model.access.csv',
        'views/loan_application_views.xml',
        'views/motorcycle_financing_menu.xml',
        'views/sale_order_views.xml',
        'data/product_category_data.xml',
        'data/product_data.xml',
     ],
    "demo": [
        'demo/loan_demo.xml',
    ],
    "author": "arieladasme",
    "website": "github.com/arieladasme",
    "application": True,
}