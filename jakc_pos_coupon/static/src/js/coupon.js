odoo.define('pos_coupon.pos_coupon', function (require) {
"use strict";

var Class   = require('web.Class');
var Model   = require('web.Model');
var session = require('web.session');
var core    = require('web.core');
var screens = require('point_of_sale.screens');
var gui     = require('point_of_sale.gui');
var pos_model = require('point_of_sale.models');
var utils = require('web.utils');

var QWeb = core.qweb;
var _t   = core._t;


var BarcodeParser = require('barcodes.BarcodeParser');
var PopupWidget = require('point_of_sale.popups');
var ScreenWidget = screens.ScreenWidget;
var PaymentScreenWidget = screens.PaymentScreenWidget;
var round_pr = utils.round_precision;

//Load Field iface_card
pos_model.load_fields("account.journal", "iface_coupon");

var _paylineproto = pos_model.Paymentline.prototype;
pos_model.Paymentline = pos_model.Paymentline.extend({
    init_from_JSON: function (json) {
        _paylineproto.init_from_JSON.apply(this, arguments);

        this.paid = json.paid;
        this.couponnumber = json.couponnumber;
       
    },
    export_as_JSON: function () {
        return _.extend(_paylineproto.export_as_JSON.apply(this, arguments), {paid: this.paid,
                                                                              couponnumber: this.couponnumber,});
                                                                              
    },
   
});

//Popup to show all transaction state for the payment.
var CouponPopupWidget = PopupWidget.extend({
    template: 'CouponPopupWidget',
    show: function(options){
        options = options || {};
        this._super(options);
        this.el.querySelector('input').addEventListener('keypress',this.input_handler);
        this.renderElement();
        this.$('input').focus();
    },
    
    input_handler: function(event){
    	condole.log("Key Input");
    },
    
    click_confirm: function(){
        var value = this.$('input').val();
        this.gui.close_popup();
        if( this.options.confirm ){
            this.options.confirm.call(this,value);
        }
    },
});
gui.define_popup({name:'coupon', widget: CouponPopupWidget});



PaymentScreenWidget.include({
        	   
            click_coupon_paymentline: function(cid){
                var self = this;
                var order = this.pos.get_order();
            	var lines = order.get_paymentlines();
                for ( var i = 0; i < lines.length; i++ ) {
                    if (lines[i].cid === cid) {
        				self.gui.show_popup('textinput',{
        				    'title': _t('Coupon Number'),
        		            'value': order.selected_paymentline.couponnumber,
        		            'confirm': function(value) {
        		            	order.selected_paymentline.couponnumber = value;
        		                self.order_changes();
        		                self.render_paymentlines();
        		            }
        				});
                    }
                }	        
            },

            render_paymentlines: function() {
            	var self  = this;
                var order = this.pos.get_order();
                if (!order) {
                    return;
                }

                var lines = order.get_paymentlines();
                var due   = order.get_due();
                var extradue = 0;
                if (due && lines.length  && due !== order.get_due(lines[lines.length-1])) {
                    extradue = due;
                }

                this.$('.paymentlines-container').empty();
                var lines = $(QWeb.render('PaymentScreen-Paymentlines', { 
                    widget: this, 
                    order: order,
                    paymentlines: lines,
                    extradue: extradue,
                }));

                lines.on('click','.delete-button',function(){
                    self.click_delete_paymentline($(this).data('cid'));
                });

                lines.on('click','.coupon-button',function(){
                	console.log("Click Coupon Button");
                    self.click_coupon_paymentline($(this).data('cid'));
                });
                
                lines.on('click','.paymentline',function(){
                    self.click_paymentline($(this).data('cid'));
                });
                    
                lines.appendTo(this.$('.paymentlines-container'));
            	
            },    
});

})