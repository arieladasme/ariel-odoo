{
    "name": "Solicitud de Préstamo",
    "summary": "Streamline the loan application process for dealerships working with third-party financing companies.",
    "version": "18.0.0.1.3",
    "category": "Kawiil/Custom Modules",
    "license": "OPL-1",
    "depends": ["base"],
    "data": [
        'security/loan_application_groups.xml',
        'security/ir.model.access.csv',
        'views/loan_application_views.xml',
        'views/motorcycle_financing_menu.xml',
     ],
    "demo": [
        'demo/loan_demo.xml',
    ],
    "author": "arieladasme",
    "website": "github.com/arieladasme",
    "application": True,
}