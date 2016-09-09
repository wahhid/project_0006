# -*- coding: utf-8 -*-
#################################################################################
#
#    Copyright (c) 2016-Present Jakc Labs. (<http://www.jakc-labs.com/>)
#
#################################################################################
{
    'name': 'POS: Coupon ',
    'summary': 'Enable POS Transaction using Coupon',
    'version': '1.0',
    'category': 'Point Of Sale',
    "sequence": 1,
    'description': """
Point Of Sale - Coupon
=====================================

Features:
----------------
    * Add ability to using Coupon for Payment in POS.
    * For Odoo 9

""",
    "author": "Wahyu Hidayat - Jakc Labs.",
    'website': 'http://www.jakc-labs.com',
    'depends': [
        'point_of_sale',
        ],
    'data': [
        'views/jakc_pos_coupon_view.xml',
        'views/templates.xml',
    ],
    'qweb': [
        'static/src/xml/pos_coupon.xml',
             
    ],    
    "installable": True,
    "application": True,
    "auto_install": False,        
}