# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Point of Sale - Enchance Report',
    'version': '1.0.1',
    'category': 'Point Of Sale',
    'sequence': 20,
    'summary': 'Touchscreen Interface for Shops',
    'description': """
Point of Sale - Enchance Report
===============================

    """,
    'depends': ['point_of_sale'],
    'data': [
        'wizard/pos_order_products.xml',
        'views/report_order_products.xml',
        'point_of_sale_report.xml',
    ],
    'installable': True,
    'application': True,
    'website': 'https://www.jakc-labs.com',
    'auto_install': False,
}
