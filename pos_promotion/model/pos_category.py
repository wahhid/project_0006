from openerp import fields, api, models, _

class PosCategory(models.Model):

    _inherit = "pos.category"

    def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
        res = super(PosCategory, self).search(cr, uid, args, offset=offset, limit=limit, order=order, context=context, count=count)
        if context and context.has_key('promotion_point'):
            cr.execute( "SELECT categ_id FROM pos_category_promotion_rel")
            categ_ids = [x[0] for x in cr.fetchall()]
            if categ_ids:
                for categ_id in categ_ids:
                    if categ_id in res:
                        res.remove(categ_id)
        return res
