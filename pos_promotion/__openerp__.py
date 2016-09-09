# -*- coding: utf-8 -*-
{
    'name': 'POS Promotions',
    'version': '1.0',
    'category': 'Point of Sale',
    'sequence': 2,
    'summary': 'Promotion for POS',
    'description': """
    Promotion for POS Odoo
    """,
    'author': 'Bruce',
    'price': '50',
    'currency': 'USD',
    'depends': ['point_of_sale'],
    'data': [

        'security/ir.model.access.csv',
        'template/template.xml',
        'view/pos_promotion_view.xml',
        'view/pos_config_view.xml',
    ],
    'images': ['images/pos.png'],
    'qweb': ['static/src/xml/*.xml'],
    'application': True,
}
