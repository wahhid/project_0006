odoo.define('pos_promotion.models', function (require) {
    "use strict";

    var models = require('point_of_sale.models');
    var screens = require('point_of_sale.screens');

    screens.OrderWidget.include({
        click_line: function(orderline, event) {
            this._super(orderline, event);
            if (orderline.reason == undefined) {
                $('.numpad').show();
            } else {
                $('.numpad').hide();
            }
        }
    });

    var _super_orderline = models.Orderline;
    models.Orderline = models.Orderline.extend({
        get_all_prices: function(){
            var $res = _super_orderline.prototype.get_all_prices.apply(this,arguments);
            if (this.percent == true || this.discount == true) {
                return {
                    "priceWithTax": this.price,
                    "priceWithoutTax": this.price,
                    "tax": 0,
                    "taxDetails": {},
                };
            } else {
                return $res
            }
        },

        get_promotion: function() {
            console.log('++++ get promotion +++++');
            return this.reason;
        },
    });


    models.Order = models.Order.extend({

    });

    models.load_models([
        {
            model: 'pos.config',
            fields: ['promotion_ids'],
            domain: function(self) {return [['id','=', self.pos_session.config_id[0]]]},
            context:{ 'pos': true},
            loaded: function(self, results){
                self.set({'promotions': results});
                for (var i=0; i < results.length; i ++) {
                    self.promotion_config_ids = results[i].promotion_ids;
                }
            },
        },
        {
            model: 'pos.promotion',
            fields: [
                'id', 'sequence', 'name', 'type',
                'method', 'product_ids', 'categ_ids', 'percent_total',
                'discount_total', 'min_total_order', 'product_id',
            ],
            domain: function(self) {return [['state', '=', 'active']]},
            context:{ 'pos': true},
            loaded: function(self, results){
                self.set({'promotions': results});
                var promotion_ids = [];
                for (var i=0; i < results.length; i ++)
                    for ( var j=0; j < self.promotion_config_ids.length; j ++) {
                        if (results[i].id == self.promotion_config_ids[j]) {
                            promotion_ids.push(results[i])
                        }
                }
                self.promotion_ids =  promotion_ids;
            },
        },
        {
            model: 'pos.promotion.line',
            fields: [
                'sequence',
                'product_from_id',
                'product_to_id',
                'min_qty',
                'gift_qty',
                'promotion_id',
            ],
            domain: function(self) {return []},
            context:{ 'pos': true},
            loaded: function(self, lines){
                var $promotion_line_ids = [];
                for (var i=0; i < self.promotion_ids.length; i ++) {
                    for ( var j=0; j < lines.length; j ++) {
                        if (lines[j].promotion_id[0] == self.promotion_ids[i].id) {
                            $promotion_line_ids.push(lines[j])
                        }
                    }
                }
                self.promotion_line_ids =  $promotion_line_ids;
                console.log('++++ POS PROMOTION LOAD DONE ++++');
            },
        }
    ])
})
