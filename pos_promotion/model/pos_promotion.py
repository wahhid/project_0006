from openerp import fields, api, models, _
from openerp.exceptions import UserError

import logging

class promotion(models.Model):

    _name = "pos.promotion"
    __logger = logging.getLogger(_name)


    sequence = fields.Integer('Sequence', required=True)
    name = fields.Char('Name', required=True)
    type = fields.Selection([
        ('total_order', 'Total Order'),
        ('product_detail', 'Product by Product'),
        ('product_category', 'Product Category'),
    ], string='Type', required=True)
    method = fields.Selection([
        ('percent', 'Percent (%)'),
        ('discount', 'Discount Money')
    ], 'Method', required=True, default='percent')
    product_id = fields.Many2one('product.product', 'Product use Promotion', domain=[('type', '=', 'service')])
    product_ids = fields.Many2many('product.product', 'product_promotion_rel', 'promotion_id', 'product_id', 'Products', domain=[('available_in_pos', '=', True)])
    categ_ids = fields.Many2many('pos.category', 'pos_category_promotion_rel', 'categ_id', 'promotion_id', 'Categories')
    promotion_line_ids = fields.One2many('pos.promotion.line', 'promotion_id', 'Rule Line Products')
    percent_total = fields.Float('Percent Total (%)', help='Percent % Total Order you want down')
    discount_total = fields.Float('Discount Total', help='Example: 1000 USD you want discount 20 USD, input 20 USD here.')
    min_total_order = fields.Float('Min Order', default=0)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('pending', 'Pending'),
        ('active', 'Active'),
        ('reject', 'Reject'),
    ], string='State', default='active')
    multi_discount_thesame_product = fields.Boolean('Multi Discount the same Product', help='Set true if you want set multi product the same have discount, example: Product A sale quantity 10 free Product B (1) quantity 30 free product C (2) sequence (2) > sequence (1) auto get discount free Product C', default=False)

    @api.multi
    def read(self, fields=None, load='_classic_read'):
        datas = super(promotion, self).read(fields=fields, load=load)
        return datas

    @api.model
    def create(self, vals):
        if vals['percent_total'] > 100 or vals['percent_total'] < 0:
            raise UserError(_('Error, Percent total can not > 100 or < 0'))
        if vals['min_total_order'] < 0:
            raise UserError(_('Error, Min Order can not < 0'))
        return super(promotion, self).create(vals)

    @api.multi
    def write(self, vals):
        if vals.has_key('percent_total') and vals['percent_total'] and (vals['percent_total'] > 100 or vals['percent_total'] < 0):
            raise UserError(_('Error, Percent total can not > 100 or < 0'))
        if vals.has_key('min_total_order') and vals['min_total_order'] and vals['min_total_order'] < 0:
            raise UserError(_('Error, Min Order can not < 0'))
        return super(promotion, self).write(vals)



class promotion_line(models.Model):

    _name = "pos.promotion.line"

    sequence = fields.Integer('Sequence')
    product_from_id = fields.Many2one('product.product', 'Product', domain=[('available_in_pos', '=', True)], required=True)
    product_to_id = fields.Many2one('product.product', 'Gift', domain=[('available_in_pos', '=', True)], required=True)
    min_qty = fields.Integer('Min Qty', required=True)
    gift_qty = fields.Integer('Gift Qty', required=True)
    promotion_id = fields.Many2one('pos.promotion', 'Promotion')

    _sql_constraints = [
        ('product_sequence', 'unique (product_from_id,sequence)', 'Can not the same Product and Sequence! Please try again')
    ]

