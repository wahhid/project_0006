# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import datetime
import pytz
import time
from openerp import tools
from openerp.osv import osv
from openerp.report import report_sxw


class pos_details(report_sxw.rml_parse):

    def _get_invoice(self, inv_id):
        res={}
        if inv_id:
            self.cr.execute("select number from account_invoice as ac where id = %s", (inv_id,))
            res = self.cr.fetchone()
            return res[0] or 'Draft'
        else:
            return  ''

    def _get_all_users(self):
        user_obj = self.pool.get('res.users')
        return user_obj.search(self.cr, self.uid, [])

    def _get_selected_products(self, form):
        product_obj = self.pool.get('product.product')
        product_args = [('product_tmpl_id','in',form['product_ids'])]
        product_ids = product_obj.search(self.cr, self.uid, product_args) 
        return product_obj.browse(self.cr, self.uid, product_ids, [])
    
    def _get_product_mrp_bom_lines(self, product_id):
        product_product_obj = self.pool.get('product.product')
        data = []
        result = {}
        product_product_ids = product_product_obj.search(self.cr, self.uid, [('product_tmpl_id','=',product_id)])
        mrp_bom_obj = self.pool.get('mrp.bom')
        mrp_bom = mrp_bom_obj.read(self.cr, self.uid, ['product_id','=',product_product_ids[0]])
        bom_line_ids = mrp_bom.bom_line_ids
        for bom_line_id in bom_line_ids:
            result = {
                'name': bom_line_id.product_id.name,
                'qty': bom_line_id.qty,
            }
            data.append(result)
        if data:
            return data
        else:
            return {}     
    
    def _pos_sales_details(self,product_id,form):
        pos_obj = self.pool.get('pos.order')
        user_obj = self.pool.get('res.users')
        product_ids = []
        product_ids.append(product_id)
        product_ids.append(0)
        
        #user_ids = form['user_ids'] or self._get_all_users()
        company_id = user_obj.browse(self.cr, self.uid, self.uid).company_id.id
        user = self.pool['res.users'].browse(self.cr, self.uid, self.uid)
        tz_name = user.tz or self.localcontext.get('tz') or 'UTC'
        user_tz = pytz.timezone(tz_name)
        between_dates = {}
        for date_field, delta in {'date_start': {'days': 0}, 'date_end': {'days': 1}}.items():
            timestamp = datetime.datetime.strptime(form[date_field] + ' 00:00:00', tools.DEFAULT_SERVER_DATETIME_FORMAT) + datetime.timedelta(**delta)
            timestamp = user_tz.localize(timestamp).astimezone(pytz.utc)
            between_dates[date_field] = timestamp.strftime(tools.DEFAULT_SERVER_DATETIME_FORMAT)

        pos_ids = pos_obj.search(self.cr, self.uid, [
            ('date_order', '>=', between_dates['date_start']),
            ('date_order', '<', between_dates['date_end']),
            ('state', 'in', ['done', 'paid', 'invoiced']),
            ('company_id', '=', company_id)
        ])
        
        query  = """SELECT 
              pos_order.id,
              pos_order.date_order,
              pos_order.name,
              pos_order_line.product_id,
              product_product.default_code, 
              product_product.name_template as product_product_name_template,
              product_bom_line.name_template,
              pos_order_line.qty as pos_order_line_qty,
              product_uom.name as product_uom_name,
              mrp_bom_line.product_qty as mrp_bom_line_product_qty,
              mrp_bom_line.product_qty * pos_order_line.qty as total_qty
            FROM pos_order
            LEFT JOIN pos_order_line ON pos_order.id = pos_order_line.order_id 
            LEFT JOIN product_product ON pos_order_line.product_id = product_product.id
            LEFT JOIN product_template ON product_template.id = product_product.product_tmpl_id
            LEFT JOIN product_uom ON product_uom.id = product_template.uom_id
            LEFT JOIN mrp_bom ON product_template.id = mrp_bom.product_tmpl_id
            LEFT JOIN mrp_bom_line ON mrp_bom.id = mrp_bom_line.bom_id
            LEFT JOIN product_product as product_bom_line ON mrp_bom_line.product_id = product_bom_line.id
            WHERE 
              pos_order.id IN {} AND pos_order_line.product_id IN {}
            ORDER BY id;""".format(tuple(pos_ids),tuple(product_ids))
        self.cr.execute(query)
        data = self.cr.dictfetchall()
        return data
        

    def _get_per_product_bom_summary(self, product_id, form):
        pos_obj = self.pool.get('pos.order')
        user_obj = self.pool.get('res.users')
        product_ids = []
        product_ids.append(product_id)
        product_ids.append(0)
        company_id = user_obj.browse(self.cr, self.uid, self.uid).company_id.id
        user = self.pool['res.users'].browse(self.cr, self.uid, self.uid)
        tz_name = user.tz or self.localcontext.get('tz') or 'UTC'
        user_tz = pytz.timezone(tz_name)
        
        between_dates = {}
        for date_field, delta in {'date_start': {'days': 0}, 'date_end': {'days': 1}}.items():
            timestamp = datetime.datetime.strptime(form[date_field] + ' 00:00:00', tools.DEFAULT_SERVER_DATETIME_FORMAT) + datetime.timedelta(**delta)
            timestamp = user_tz.localize(timestamp).astimezone(pytz.utc)
            between_dates[date_field] = timestamp.strftime(tools.DEFAULT_SERVER_DATETIME_FORMAT)

        pos_ids = pos_obj.search(self.cr, self.uid, [
            ('date_order', '>=', between_dates['date_start']),
            ('date_order', '<', between_dates['date_end']),
            ('state', 'in', ['done', 'paid', 'invoiced']),
            ('company_id', '=', company_id)
        ])
            
        query = """SELECT  
                  product_bom_line.name_template,
                  sum(mrp_bom_line.product_qty * pos_order_line.qty) as total_qty,
                  product_uom.name as product_uom_name
                FROM pos_order
                LEFT JOIN pos_order_line ON pos_order.id = pos_order_line.order_id 
                LEFT JOIN product_product ON pos_order_line.product_id = product_product.id
                LEFT JOIN product_template on product_template.id = product_product.product_tmpl_id
                LEFT JOIN product_uom ON product_uom.id = product_template.uom_id
                LEFT JOIN mrp_bom ON product_template.id = mrp_bom.product_tmpl_id
                LEFT JOIN mrp_bom_line ON mrp_bom.id = mrp_bom_line.bom_id
                LEFT JOIN product_product as product_bom_line ON mrp_bom_line.product_id = product_bom_line.id
                WHERE 
                  pos_order.id IN {} AND pos_order_line.product_id IN {}
                GROUP BY
                  product_bom_line.name_template, product_uom.name;""".format(tuple(pos_ids),tuple(product_ids))
            
        self.cr.execute(query)
        data = self.cr.dictfetchall()
        return data
    
    def _get_bom_summary(self, form):
        pos_obj = self.pool.get('pos.order')
        user_obj = self.pool.get('res.users')
        product_obj = self.pool.get('product.product')
        
        product_args = [('product_tmpl_id','in',form['product_ids'])]
        product_ids = product_obj.search(self.cr, self.uid, product_args) 
        if len(product_ids) == 1:
            product_ids.append(0)
                    
        company_id = user_obj.browse(self.cr, self.uid, self.uid).company_id.id
        user = self.pool['res.users'].browse(self.cr, self.uid, self.uid)
        tz_name = user.tz or self.localcontext.get('tz') or 'UTC'
        user_tz = pytz.timezone(tz_name)
        
        between_dates = {}
        for date_field, delta in {'date_start': {'days': 0}, 'date_end': {'days': 1}}.items():
            timestamp = datetime.datetime.strptime(form[date_field] + ' 00:00:00', tools.DEFAULT_SERVER_DATETIME_FORMAT) + datetime.timedelta(**delta)
            timestamp = user_tz.localize(timestamp).astimezone(pytz.utc)
            between_dates[date_field] = timestamp.strftime(tools.DEFAULT_SERVER_DATETIME_FORMAT)

        pos_ids = pos_obj.search(self.cr, self.uid, [
            ('date_order', '>=', between_dates['date_start']),
            ('date_order', '<', between_dates['date_end']),
            ('state', 'in', ['done', 'paid', 'invoiced']),
            ('company_id', '=', company_id)
        ])
        
        
        query = """SELECT  
                      product_bom_line.name_template,
                      sum(mrp_bom_line.product_qty * pos_order_line.qty) as total_qty,
                      product_uom.name as product_uom_name
                    FROM pos_order
                    LEFT JOIN pos_order_line ON pos_order.id = pos_order_line.order_id 
                    LEFT JOIN product_product ON pos_order_line.product_id = product_product.id
                    LEFT JOIN product_template on product_template.id = product_product.product_tmpl_id
                    LEFT JOIN product_uom ON product_uom.id = product_template.uom_id
                    LEFT JOIN mrp_bom ON product_template.id = mrp_bom.product_tmpl_id
                    LEFT JOIN mrp_bom_line ON mrp_bom.id = mrp_bom_line.bom_id
                    LEFT JOIN product_product as product_bom_line ON mrp_bom_line.product_id = product_bom_line.id
                    WHERE 
                      pos_order.id IN {} AND pos_order_line.product_id IN {} 
                    GROUP BY
                      product_bom_line.name_template, product_uom.name;""".format(tuple(pos_ids),tuple(product_ids))
        
        self.cr.execute(query)
        data = self.cr.dictfetchall()
        return data
        
    def _get_product_final_total(self):
        return self.product_final_total
    
    def _get_qty_total_2(self):
        return self.qty

    def _get_sales_total_2(self):
        return self.total

    def _get_sum_invoice_2(self, form):
        pos_obj = self.pool.get('pos.order')
        user_obj = self.pool.get('res.users')
        user_ids = form['user_ids'] or self._get_all_users()
        company_id = user_obj.browse(self.cr, self.uid, self.uid).company_id.id
        pos_ids = pos_obj.search(self.cr, self.uid, [('date_order','>=',form['date_start'] + ' 00:00:00'),('date_order','<=',form['date_end'] + ' 23:59:59'),('user_id','in',user_ids),('company_id','=',company_id),('invoice_id','<>',False)])
        for pos in pos_obj.browse(self.cr, self.uid, pos_ids):
            for pol in pos.lines:
                self.total_invoiced += (pol.price_unit * pol.qty * (1 - (pol.discount) / 100.0))
        return self.total_invoiced or False

    def _paid_total_2(self):
        return self.total or 0.0

    def _get_sum_dis_2(self):
        return self.discount or 0.0

    def _get_sum_discount(self, form):
        #code for the sum of discount value
        pos_obj = self.pool.get('pos.order')
        user_obj = self.pool.get('res.users')
        user_ids = form['user_ids'] or self._get_all_users()
        company_id = user_obj.browse(self.cr, self.uid, self.uid).company_id.id
        pos_ids = pos_obj.search(self.cr, self.uid, [('date_order','>=',form['date_start'] + ' 00:00:00'),('date_order','<=',form['date_end'] + ' 23:59:59'),('user_id','in',user_ids),('company_id','=',company_id)])
        for pos in pos_obj.browse(self.cr, self.uid, pos_ids):
            for pol in pos.lines:
                self.total_discount += ((pol.price_unit * pol.qty) * (pol.discount / 100))
        return self.total_discount or False

    def _get_payments(self, form):
        statement_line_obj = self.pool.get("account.bank.statement.line")
        pos_order_obj = self.pool.get("pos.order")
        user_ids = form['user_ids'] or self._get_all_users()
        company_id = self.pool['res.users'].browse(self.cr, self.uid, self.uid).company_id.id
        pos_ids = pos_order_obj.search(self.cr, self.uid, [('date_order','>=',form['date_start'] + ' 00:00:00'),('date_order','<=',form['date_end'] + ' 23:59:59'),('state','in',['paid','invoiced','done']),('user_id','in',user_ids), ('company_id', '=', company_id)])
        data={}
        if pos_ids:
            st_line_ids = statement_line_obj.search(self.cr, self.uid, [('pos_statement_id', 'in', pos_ids)])
            if st_line_ids:
                st_id = statement_line_obj.browse(self.cr, self.uid, st_line_ids)
                a_l=[]
                for r in st_id:
                    a_l.append(r['id'])
                self.cr.execute("select aj.name,sum(amount) from account_bank_statement_line as absl,account_bank_statement as abs,account_journal as aj " \
                                "where absl.statement_id = abs.id and abs.journal_id = aj.id  and absl.id IN %s " \
                                "group by aj.name ",(tuple(a_l),))

                data = self.cr.dictfetchall()
                return data
        else:
            return {}

    def _total_of_the_day(self, objects):
        return self.total or 0.00

    def _sum_invoice(self, objects):
        return reduce(lambda acc, obj:
                        acc + obj.invoice_id.amount_total,
                        [o for o in objects if o.invoice_id and o.invoice_id.number],
                        0.0)

    def _ellipsis(self, orig_str, maxlen=100, ellipsis='...'):
        maxlen = maxlen - len(ellipsis)
        if maxlen <= 0:
            maxlen = 1
        new_str = orig_str[:maxlen]
        return new_str

    def _strip_name(self, name, maxlen=50):
        return self._ellipsis(name, maxlen, ' ...')

    def _get_tax_amount(self, form):
        taxes = {}
        account_tax_obj = self.pool.get('account.tax')
        user_ids = form['user_ids'] or self._get_all_users()
        pos_order_obj = self.pool.get('pos.order')
        company_id = self.pool['res.users'].browse(self.cr, self.uid, self.uid).company_id.id
        pos_ids = pos_order_obj.search(self.cr, self.uid, [('date_order','>=',form['date_start'] + ' 00:00:00'),('date_order','<=',form['date_end'] + ' 23:59:59'),('state','in',['paid','invoiced','done']),('user_id','in',user_ids), ('company_id', '=', company_id)])
        for order in pos_order_obj.browse(self.cr, self.uid, pos_ids):
            currency = order.session_id.currency_id
            for line in order.lines:
                if line.product_id.taxes_id:
                    line_taxes = line.product_id.taxes_id.compute_all(line.price_unit * (1-(line.discount or 0.0)/100.0), currency, line.qty, product=line.product_id, partner=line.order_id.partner_id or False)
                    for tax in line_taxes['taxes']:
                        taxes.setdefault(tax['id'], {'name': tax['name'], 'amount':0.0})
                        taxes[tax['id']]['amount'] += tax['amount']
        return taxes.values()

    def _get_user_names(self, user_ids):
        user_obj = self.pool.get('res.users')
        return ', '.join(map(lambda x: x.name, user_obj.browse(self.cr, self.uid, user_ids)))

    def __init__(self, cr, uid, name, context):
        super(pos_details, self).__init__(cr, uid, name, context=context)
        self.total = 0.0
        self.qty = 0.0
        self.total_invoiced = 0.0
        self.discount = 0.0
        self.total_discount = 0.0
        self.product_final_total = []
        self.localcontext.update({
            'time': time,
            'selected_products': self._get_selected_products,
            'pos_sales_details': self._pos_sales_details,
            'per_product_bom_summary': self._get_per_product_bom_summary,
            'bom_summary': self._get_bom_summary,
        })


class report_pos_order_products(osv.AbstractModel):
    _name = 'report.jakc_pos_report.report_orderproducts'
    _inherit = 'report.abstract_report'
    _template = 'jakc_pos_report.report_orderproducts'
    _wrapped_report_class = pos_details
