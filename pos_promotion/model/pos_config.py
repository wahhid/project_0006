from openerp import fields, api, models, _

class pos_config(models.Model):

    _inherit = "pos.config"

    promotion_ids = fields.Many2many('pos.promotion', 'pos_promotion_rel', 'pos_config_id', 'promotion_id', 'Promotions', domain=[('state', '=', 'active')])

    @api.multi
    def read(self, fields=None, load='_classic_read'):
        self.check_access_rule('read')
        datas = super(pos_config, self).read(fields=fields, load=load)
        return datas
