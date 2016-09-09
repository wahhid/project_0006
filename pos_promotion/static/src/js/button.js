odoo.define('pos_promotion.widget', function (require) {
    "use strict";
    var screens = require('point_of_sale.screens');

    var PromotionButton = screens.ActionButtonWidget.extend({
        template: 'PromotionButton',
        button_click: function () {
            this.promotion_ids = this.pos.promotion_ids;
            this.promotion_line_ids = this.pos.promotion_line_ids;
            this.order = this.pos.get_order();
            this.remove_line('percent');
            this.remove_line('discount');
            this.remove_line('free_gift');
            this.order.percent_category = [];
            this.order.discount_category = [];
            this.amount_total = this.order.get_total_with_tax();
            for (var i = 0; i < this.promotion_ids.length; i++) {
                var $promotion = this.promotion_ids[i];
                if ($promotion.type == 'total_order') {
                    this.validate_total_order($promotion);
                }
                if ($promotion.type == 'product_detail' && this.promotion_line_ids) {
                    for (var j = 0; j < this.promotion_line_ids.length; j++) {
                        if (this.promotion_line_ids[j].promotion_id[0] == this.promotion_ids[i].id) {
                            this.validate_product(this.promotion_line_ids[j]);
                        }
                    }
                }
                if ($promotion.type == 'product_category') {
                    this.validate_product_categ($promotion);
                }
            }
        },



        remove_line: function (param) {
            var lines = this.order.get_orderlines()
            for (var i = 0; i < lines.length; i++) {
                if (lines[i] && lines[i][param]) {
                    this.order.remove_orderline(lines[i]);
                }
            }
        },

        // when we're have promotion total order, we're need chosen one promotions and apply for order
        // example: promotion 1 persent 10% with total oder is 100, persent 20% with total order is 200, will apply only option 2
        check_promtion_percent_total_order: function(percent) {
            if (this.order && this.order.percent > percent) {
                this.remove_line('percent')
            }
        },

        // when we're have promotion persent total order, we're need chosen one promotions and apply for order
        // example: promotion 1 discount 10 with total oder is 100, discount 20 with total order is 200, will apply only option 2
        check_promtion_discount_total_order: function(discount) {
            if (this.order && this.order.discount > discount) {
                this.remove_line('discount')
            }
        },

        validate_total_order: function (promotion, discount) {
            var min_order = promotion.min_total_order;
            if (this.amount_total >= min_order) {
                if (promotion.method == 'percent') {
                    if (!this.pos.db.get_product_by_id(promotion.product_id[0])) {
                            alert('You need set All Product use Pormotion is :Available in the Point of Sale! ')
                    }
                    else {

                        // get discount from promotion config 
                        var discount = -(this.amount_total * promotion.percent_total / 100);
                        // check promotion
                        this.check_promtion_percent_total_order(discount)
                        // add product
                        this.order.add_product(this.pos.db.get_product_by_id(promotion.product_id[0]), {price: discount});
                        var selectedLine = this.order.get_selected_orderline();
                        selectedLine.percent = true;
                        selectedLine.reason = ' Percent ' +promotion.percent_total+' % when total order Great or equal ' + min_order;
                        selectedLine.promotion = true;
                        // show promotion to screen
                        this.show_promotions(selectedLine);
                        this.order.percent = discount;
                    }
                }
                if (promotion.method == 'discount') {
                    if (!this.pos.db.get_product_by_id(promotion.product_id[0])) {
                            alert('You need set All Product use Pormotion is :Available in the Point of Sale! ')
                    }
                    else {
                        // get discount from promotion config 
                        var discount = -(promotion.discount_total);
                        // check promotion
                        this.check_promtion_discount_total_order(discount)
                        // add product
                        this.order.add_product(this.pos.db.get_product_by_id(promotion.product_id[0]), {price: discount});
                        var selectedLine = this.order.get_selected_orderline();
                        selectedLine.discount = true;
                        selectedLine.reason = ' Discount ' + promotion.discount_total + ' when total order Great or equal :' + min_order;
                        selectedLine.promotion = true;
                        // show promotion to screen
                        this.show_promotions(selectedLine);
                        this.order.discount = discount;
                    }
                }
            }
        },

        show_promotions: function(line) {
            $('#' + line.id).html('<i class="fa fa-gift promotion">' +line.reason+ '</i>');
        },

        validate_product: function (promotion_line) {
            var product_from_id = promotion_line.product_from_id[0];
            var minn_qty = promotion_line.min_qty;
            var lines = this.order.get_orderlines()
            for (var i = 0; i < lines.length; i++) {
                if (lines[i].product.id == product_from_id && lines[i].quantity >= minn_qty) {
                    this.order.add_product(this.pos.db.get_product_by_id(promotion_line.product_to_id[0]), {
                        price: 0,
                        quantity: promotion_line.gift_qty
                    });
                    var selectedLine = this.order.get_selected_orderline();
                    selectedLine.reason = ' Sale ' + lines[i].product.display_name+ ' Free ' + promotion_line.gift_qty +' '+ selectedLine.product.display_name;
                    selectedLine.free_gift = true;
                    selectedLine.selected = true;
                    selectedLine.promotion = true;
                    this.show_promotions(selectedLine);
                }
            }
        },


        check_promtion_percent_category: function(category_id, persent) {
            for (var i=0; i < this.order.percent_category.length; i++) {
                if (this.order.percent_category[i].category_id == category_id && this.order.percent_category[i].percent > persent) {
                    // remove line 
                    var lines = this.order.get_orderlines()
                    for (var i = 0; i < lines.length; i++) {
                        if (lines[i].category_id == category_id && lines[i].percent) {
                            this.order.remove_orderline(lines[i]);
                        }
                    }
                }
            }
        },

        check_promtion_discount_category: function(category_id, discount) {
            for (var i=0; i < this.order.discount_category.length; i++) {
                if (this.order.discount_category[i].category_id == category_id && this.order.discount_category[i].discount > discount) {
                    // remove line 
                    var lines = this.order.get_orderlines();
                    for (var j = 0; j < lines.length; j++) {
                        if (lines[j].category_id == category_id && lines[j].discount) {
                            this.order.remove_orderline(lines[j]);
                        }
                    }
                }
            }
        },



        validate_product_categ: function (promotion) {
            var method = promotion.method;
            var min_order = promotion.min_total_order;
            var lines = this.order.get_orderlines()
            var categ_ids = promotion.categ_ids;
            for (var j = 0; j < categ_ids.length; j++) {
                if (this.amount_total >= min_order) {
                    if (method == 'percent') {
                        var discount = -(this.amount_total * promotion.percent_total / 100);
                        this.check_promtion_percent_category(categ_ids[j], discount)
                        if (!this.pos.db.get_product_by_id(promotion.product_id[0])) {
                            alert('You need set All Product use Pormotion is :Available in the Point of Sale! ')
                        }
                        else {
                            this.order.add_product(this.pos.db.get_product_by_id(promotion.product_id[0]), {price: discount});
                            var selectedLine = this.order.get_selected_orderline();
                            selectedLine.percent = true;
                            selectedLine.reason = ' Percent ' +promotion.percent_total + '% for category ' + this.pos.db.get_category_by_id(categ_ids[j]).name;
                            selectedLine.promotion = true;
                            selectedLine.category_id = categ_ids[j];
                            this.show_promotions(selectedLine);
                            this.order.percent_category.push({
                                'category_id': categ_ids[j],
                                'percent': discount
                            });
                        }
                        
                    }
                    if (method == 'discount') {
                        var discount = -(promotion.discount_total);
                        this.check_promtion_discount_category(categ_ids[j], discount)
                        if (!this.pos.db.get_product_by_id(promotion.product_id[0])) {
                            alert('You need set All Product use Pormotion is :Available in the Point of Sale! ')
                        } else {
                            this.order.add_product(this.pos.db.get_product_by_id(promotion.product_id[0]), {price: discount});
                            var selectedLine = this.order.get_selected_orderline();
                            selectedLine.discount = true;
                            selectedLine.reason = ' Discount ' +promotion.discount_total+ ' for category ' + this.pos.db.get_category_by_id(categ_ids[j]).name;
                            selectedLine.promotion = true;
                            selectedLine.category_id = categ_ids[j];
                            this.show_promotions(selectedLine);
                            this.order.discount_category.push({
                                'category_id': categ_ids[j],
                                'discount': discount
                            });
                        }
                        
                    }
                }
            }

        },
    });
    screens.define_action_button({
        'name': 'promotion',
        'widget': PromotionButton,
        'condition': function () {
            var res = this.pos.promotion_ids;
            return res
        },
    });
})
