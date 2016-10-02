# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import datetime
import pytz
import time
from openerp import tools
from openerp.osv import osv
from openerp.report import report_sxw


class pos_order_products(report_sxw.rml_parse):

    def _get_all_products(self):
        product_obj = self.pool.get('product.template')
        return product_obj.search(self.cr, self.uid, [])
            
    def _get_selected_products(self, form):
        product_ids = form['product_ids']
        product_obj = self.pool.get('product.template')
        return product_obj.search(self.cr, self.uid, product_ids)
            
        

    def _get_qty_total_2(self):
        return self.qty

    def _get_sales_total_2(self):
        return self.total

    def _ellipsis(self, orig_str, maxlen=100, ellipsis='...'):
        maxlen = maxlen - len(ellipsis)
        if maxlen <= 0:
            maxlen = 1
        new_str = orig_str[:maxlen]
        return new_str

    def _strip_name(self, name, maxlen=50):
        return self._ellipsis(name, maxlen, ' ...')

    def _get_user_names(self, user_ids):
        user_obj = self.pool.get('res.users')
        return ', '.join(map(lambda x: x.name, user_obj.browse(self.cr, self.uid, user_ids)))

    def __init__(self, cr, uid, name, context):
        super(pos_order_products, self).__init__(cr, uid, name, context=context)
        self.total = 0.0
        self.qty = 0.0
        self.total_invoiced = 0.0
        self.discount = 0.0
        self.total_discount = 0.0
        self.localcontext.update({
            'time': time,
            'selected_products':self._get_selected_products,
        })


class report_pos_details(osv.AbstractModel):
    _name = 'report.point_of_sale.report_orderproducts'
    _inherit = 'report.abstract_report'
    _template = 'point_of_sale.report_orderproducts'
    _wrapped_report_class = pos_order_products
