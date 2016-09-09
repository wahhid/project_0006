from openerp import fields, models, _, api
from openerp.exceptions import UserError
import logging


_logger = logging.getLogger(__name__)

AVAILABLE_STATES = [
    ('draft', 'New'),
    ('open', 'Open'),
    ('done', 'Close'),
    ('cancel', 'Cancel'),                    
]

class account_bank_statement_line(models.Model):
    _inherit = "account.bank.statement.line"
    coupon_number = fields.Char(string='Coupon Number', size=50)
    
class account_journal(models.Model):
    _inherit = "account.journal"
    iface_coupon = fields.Boolean(string='Coupon', default=False)
    
class pos_order_card(models.Model):
    _inherit = "pos.order"

    @api.model
    def _payment_fields(self, ui_paymentline):
        fields = super(pos_order_card, self)._payment_fields(ui_paymentline)
        fields.update({
            'coupon_number': ui_paymentline.get('couponnumber'),
        })
        return fields

    @api.model
    def add_payment(self, order_id, data):
        statement_id = super(pos_order_card, self).add_payment(order_id, data)
        statement_lines = self.env['account.bank.statement.line'].search([('statement_id', '=', statement_id),
                                                                         ('pos_statement_id', '=', order_id),
                                                                         ('journal_id', '=', data['journal']),
                                                                         ('amount', '=', data['amount'])])

        # we can get multiple statement_lines when there are >1 credit
        # card payments with the same amount. In that case it doesn't
        # matter which statement line we pick, just pick one that
        # isn't already used.
        print data
        for line in statement_lines:
            line.couponnumber = data.get('coupon_number')
            #line.cardnumber = "1111"
            #line.cardowner = "Wahyu"
            
        return statement_id
    
class pos_coupon(models.Model):
    _name = "pos.coupon"
    name= fields.Char("Description", size=100, required=True)
    start_date = fields.Date("Start Date")
    end_date = fields.Date("End Date")
    coupon_qty = fields.Integer('Coupon QTY', default=0, help="Set QTY to 0 if manual input of coupon")
    amount = fields.Float('Amount')
    line_ids = fields.One2many("pos.coupon.line","coupon_id", "Lines")
    state = fields.Selection(AVAILABLE_STATES,'States',size=16, readonly=True, default='draft')

    @api.multi
    def trans_open(self):
        values = {}
        values.update({'state':'open'})
        self.write(values)
        
    @api.multi
    def trans_generate(self):
        coupon_line_obj = self.env['pos.coupon.line']
        coupon_qty = self.coupon_qty
        if coupon_qty == 0:
            raise UserError(_('Coupon Generate not Allowed'))
    
class pos_coupon_line(models.Model):
    _name = "pos.coupon.line"
    coupon_id = fields.Many2one("pos.coupon","Coupon ID")
    coupon_number = fields.Char("Coupon #", size=20, required=True)
    usage_date = fields.Date("Usage Date", readonly=True)
    state = fields.Selection(AVAILABLE_STATES,'States', size=16, readonly=True, default='draft')
    
    
    