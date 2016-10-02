# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import time
from openerp.osv import osv, fields


class pos_order_products(osv.osv_memory):
    _name = 'pos.order.products'
    _description = 'POS Order Products'

    _columns = {
        'date_start': fields.date('Date Start', required=True),
        'date_end': fields.date('Date End', required=True),
        'product_ids': fields.many2many('product.template', 'pos_order_products_report_product_rel', 'product_id', 'wizard_id', 'Products'),
    }
    _defaults = {
        'date_start': fields.date.context_today,
        'date_end': fields.date.context_today,
    }

    def print_report(self, cr, uid, ids, context=None):
        """
         To get the date and print the report
         @param self: The object pointer.
         @param cr: A database cursor
         @param uid: ID of the user currently logged in
         @param context: A standard dictionary
         @return : retrun report
        """
        if context is None:
            context = {}
        datas = {'ids': context.get('active_ids', [])}
        res = self.read(cr, uid, ids, ['date_start', 'date_end', 'product_ids'], context=context)
        res = res and res[0] or {}
        datas['form'] = res
        if res.get('id',False):
            datas['ids']=[res['id']]
        return self.pool['report'].get_action(cr, uid, [], 'jakc_pos_report.report_orderproducts', data=datas, context=context)
