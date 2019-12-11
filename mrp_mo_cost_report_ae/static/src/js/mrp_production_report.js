odoo.define('mrp_mo_cost_report_ae.mrp_production_report_ae', function (require) {
'use strict';

var core = require('web.core');
var framework = require('web.framework');
var stock_report_generic = require('stock.stock_report_generic');

var QWeb = core.qweb;
var _t = core._t;


var MrpBomReport = stock_report_generic.extend({
    events: {
        'click .o_mrp_mo_unfoldable': '_onClickUnfold',
        'click .o_mrp_mo_foldable': '_onClickFold',
        'click .o_mrp_bom_action': '_onClickAction',
        'click .o_mrp_show_attachment_action': '_onClickShowAttachment',
        'click .o_collapseme': '_onClickCollapse',
    },
    get_html: function() {
        var self = this;
        var t = new Date();
        var y = t.getFullYear();
        var m = t.getMonth() + 1;
        var lastDayOfMonth = new Date(y, m, 0).getDate();
        var formattedMonth = ("0" + m).slice(-2);
        var dateFrom = y + '-' + formattedMonth + '-' + '01';
        var dateTo = y + '-' + formattedMonth + '-' + lastDayOfMonth;
        var args = [
            this.given_context.active_id || 1,
            this.given_context.searchQty || 1,
            this.given_context.searchVariant,
            this.given_context.lotId,
            this.given_context.productID,
            this.given_context.product,
            this.given_context.dateFrom || dateFrom,
            this.given_context.dateTo || dateTo,
        ];
        return this._rpc({
                model: 'report.mrp_mo_cost_report_ae.report_mo_structure',
                method: 'get_html',
                args: args,
                context: this.given_context,
            })
            .then(function (result) {
                self.data = result;
            });
    },
    set_html: function() {
        var self = this;
        return this._super().then(function () {
            self.$el.html(self.data.lines);
            self.renderSearch();
            self.update_cp();
        });
    },
    render_html: function(event, $el, result){
        // if (result.indexOf('mrp.document') > 0) {
        //     if (this.$('.o_mrp_has_attachments').length === 0) {
        //         var column = $('<th/>', {
        //             class: 'o_mrp_has_attachments',
        //             title: 'Files attached to the product Attachments',
        //             text: 'Attachments',
        //         });
        //         this.$('table thead th:last-child').after(column);
        //     }
        // }
        $el.after(result);
        $(event.currentTarget).toggleClass('o_mrp_mo_foldable o_mrp_mo_unfoldable fa-caret-right fa-caret-down');
        this._reload_report_type();
    },
    get_bom: function(event) {
      var self = this;
      var $parent = $(event.currentTarget).closest('tr');
      var activeID = $parent.data('id');
      var product_ID = $parent.data('product_id');
      var lineID = $parent.data('line');
      var qty = $parent.data('qty');
      var level = $parent.data('level') || 0;
      var mo = $parent.data('mo') || 1;
      return this._rpc({
              model: 'report.mrp_mo_cost_report_ae.report_mo_structure',
              method: 'get_bom',
              args: [
                  activeID,
                  mo,
                  product_ID,
                  parseFloat(qty),
                  lineID,
                  level + 1,
              ]
          })
          .then(function (result) {
              self.render_html(event, $parent, result);
          });
    },
    get_child_mo: function(event) {
        var self = this;
        var $parent = $(event.currentTarget).closest('tr');
        var moId = $parent.data('id');
        var level = $parent.data('level');
        var dateFrom = $('.o_from_date').val();
        var dateTo = $('.o_to_date').val();
        return this._rpc({
            model: 'report.mrp_mo_cost_report_ae.report_mo_structure',
            method: 'get_child_mo',
            args: [
                false,
                moId,
                dateFrom,
                dateTo,
                level + 1,
            ]
        })
        .then(function (result) {
            self.render_html(event, $parent, result);
        });
    },
    get_ops:  function(event) {
        var self = this;
        var $parent = $(event.currentTarget).closest('tr');
        var moId = $parent.data('id');
        return this._rpc({
            model: 'report.mrp_mo_cost_report_ae.report_mo_structure',
            method: 'get_ops',
            args: [
                false,
                moId,
            ]
        })
        .then(function (result) {
            self.render_html(event, $parent, result);
        });
    },
    get_operations: function(event) {
      var self = this;
      var $parent = $(event.currentTarget).closest('tr');
      var activeID = $parent.data('bom-id');
      var qty = $parent.data('qty');
      var level = $parent.data('level') || 0;
      return this._rpc({
              model: 'report.mrp_mo_cost_report_ae.report_mo_structure',
              method: 'get_operations',
              args: [
                  activeID,
                  parseFloat(qty),
                  level + 1
              ]
          })
          .then(function (result) {
              self.render_html(event, $parent, result);
          });
    },
    get_components: function(event) {
        var self = this;
        var $parent = $(event.currentTarget).closest('tr');
        var moId = $parent.data('id');
        var level = $parent.data('level');
        return this._rpc({
            model: 'report.mrp_mo_cost_report_ae.report_mo_structure',
            method: 'get_components',
            args: [
                false,
                moId,
            ]
        })
        .then(function (result) {
            self.render_html(event, $parent, result);
        });
    },
    update_cp: function () {
        var status = {
            cp_content: {
                $buttons: this.$buttonPrint,
                $searchview_buttons: this.$searchView
            },
        };
        return this.update_control_panel(status);
    },
    renderSearch: function () {
        var t = new Date();
        var y = t.getFullYear();
        var m = t.getMonth() + 1;
        var lastDayOfMonth = new Date(y, m, 0).getDate();
        var formattedMonth = ("0" + m).slice(-2);
        var dateFrom = y + '-' + formattedMonth + '-' + '01';
        var dateTo = y + '-' + formattedMonth + '-' + lastDayOfMonth;
        this.$buttonPrint = $(QWeb.render('mrp_mo_cost_report_ae.button', {date_from: dateFrom, date_to: dateTo}));
        this.$buttonPrint.filter('.o_mrp_bom_print').on('click', this._onClickPrint.bind(this));
        this.$buttonPrint.filter('.o_mrp_producttion_xls_print').on('click', this._onClickXLSPrint.bind(this));
        // this.$buttonPrint.filter('.o_mrp_bom_print_unfolded').on('click', this._onClickPrint.bind(this));
        this.$searchView = $(QWeb.render('mrp_mo_cost_report_ae.report_bom_search', _.omit(this.data, 'lines')));
        this.$searchView.find('.o_mrp_bom_report_qty').on('change', this._onChangeQty.bind(this));
        this.$searchView.find('.o_mrp_bom_report_variants').on('change', this._onChangeVariants.bind(this));
        this.$searchView.find('.o_mrp_bom_report_lots').on('change', this._onChangeLots.bind(this));
        this.$searchView.find('.o_mrp_production_report_product').select2({
                                                                    placeholder: "Choose Products",
                                                                });

        this.$searchView.find('.o_mrp_production_report_product').on('change', this._onChangeProduct.bind(this));
        // this.$searchView.find('.o_mrp_mo_product').on('change', this._onChangeProductName.bind(this));
        this.$searchView.find('.o_mrp_bom_report_type').on('change', this._onChangeType.bind(this));
        this.$buttonPrint.filter('.o_from_date').on('change', this._onChangeFromDate.bind(this));
        this.$buttonPrint.filter('.o_to_date').on('change', this._onChangeToDate.bind(this));
    },
    _onClickPrint: function (ev) {
        var childBomIDs = _.map(this.$el.find('.o_mrp_mo_foldable').closest('tr'), function (el) {
            return $(el).data('id');
        });
        var from_dt = $('.o_from_date').val();
        var to_dt = $('.o_to_date').val();
        var o_product_id = $('select.o_mrp_production_report_product').val();
        var o_product_name = $('.o_mrp_mo_product').val();
        var o_lot_id = $('.o_mrp_bom_report_lots').val();
        if (!o_product_id) {
            return;
        }
        framework.blockUI();

        var reportname = 'mrp_mo_cost_report_ae.report_mo_structure?docids=1&report_type=' + this.given_context.report_type + '&date_from=' + from_dt + '&date_to=' + to_dt;
        if (! $(ev.currentTarget).hasClass('o_mrp_bom_print_unfolded')) {
            reportname += '&quantity=' + (this.given_context.searchQty || 1) +
                          '&childs=' + JSON.stringify(childBomIDs);
        }
        if (this.given_context.searchVariant) {
            reportname += '&variant=' + this.given_context.searchVariant;
        }
        if (o_product_id && o_product_id !== "---") {
            reportname += '&product_id=' + o_product_id;
        }
        if (o_product_name) {
            reportname += '&product_name=' + o_product_name;
        }
        if (o_lot_id && o_lot_id !== "---") {
            reportname += '&lot_id=' + o_lot_id;
        }
        var action = {
            'type': 'ir.actions.report',
            'report_type': 'qweb-pdf',
            'report_name': reportname,                                
            'report_file': 'mrp_mo_cost_report_ae.report_mo_structure',
        };
        return this.do_action(action).then(function (){
            framework.unblockUI();
        });
    },
    _onClickXLSPrint: function (ev) {
        var from_dt = $('.o_from_date').val();
        var to_dt = $('.o_to_date').val();
        var o_product_id = $('select.o_mrp_production_report_product').val();
        var o_product_name = $('.o_mrp_mo_product').val();
        var o_lot_id = $('.o_mrp_bom_report_lots').val();
        if (!o_product_id) {
            return;
        }

        var reportname = 'mrp_mo_cost_report_ae.mo_cost_xlsx?docids=1&date_from=' + from_dt + '&date_to=' + to_dt;
        if (this.given_context.searchVariant) {
            reportname += '&variant=' + this.given_context.searchVariant;
        }
        if (o_product_id && o_product_id !== "---") {
            reportname += '&product_ids=' + o_product_id;
        }
        if (o_lot_id && o_lot_id !== "---") {
            reportname += '&lot_ids=' + o_lot_id;
        }

        framework.blockUI();
        var action = {
            'id': o_product_id,
            'type': 'ir.actions.report',
            'report_type': 'xlsx',
            'report_name': reportname,
            'report_file': 'mo_cost_xlsx.xlsx',
        };
        return this.do_action(action).then(function (){
            framework.unblockUI();
        });
    },
    _onChangeQty: function (ev) {
        var qty = $(ev.currentTarget).val().trim();
        if (qty) {
            this.given_context.searchQty = parseFloat(qty);
            this._reload();
        }
    },
    _onChangeType: function (ev) {
        var report_type = $("option:selected", $(ev.currentTarget)).data('type');
        this.given_context.report_type = report_type;
        this._reload_report_type();
    },
    _onChangeVariants: function (ev) {
        var productId = $(ev.currentTarget).val();
        if (productId === "---") {
            delete this.given_context.searchVariant;
        } else {
            this.given_context.searchVariant = productId;
        }
        this._reload();
    },
    _onChangeLots: function (ev) {
        var lotId = $(ev.currentTarget).val();
        if (lotId === "---") {
            delete this.given_context.lotId;
        } else {
            this.given_context.lotId = lotId;
        }
        this._reload();
    },
    _onChangeProduct: function (ev) {
        var productID = $(ev.currentTarget).val();
        if (productID === "---") {
            // delete this.given_context.productID;
            this.given_context.productID = "0";
        } else {
            this.given_context.productID = productID;
        }
        this._reload();
    },
    _onChangeProductName: function (ev) {
        var product = $(ev.currentTarget).val();
        product = product && product.trim()
        this.given_context.product = product;
        this._reload();
    },
    _onChangeFromDate: function (ev) {
        this.given_context.dateFrom = $(ev.currentTarget).val();
        this._reload();
    },
    _onChangeToDate:  function (ev) {
        this.given_context.dateTo = $(ev.currentTarget).val();
        this._reload();
    },
    _onClickUnfold: function (ev) {
        var redirect_function = $(ev.currentTarget).data('function');
        this[redirect_function](ev);
    },
    _onClickFold: function (ev) {
        this._removeLines($(ev.currentTarget).closest('tr'));
        $(ev.currentTarget).toggleClass('o_mrp_mo_foldable o_mrp_mo_unfoldable fa-caret-right fa-caret-down');
    },
    _onClickAction: function (ev) {
        ev.preventDefault();
        return this.do_action({
            type: 'ir.actions.act_window',
            res_model: $(ev.currentTarget).data('model'),
            res_id: $(ev.currentTarget).data('res-id'),
            views: [[false, 'form']],
            target: 'current'
        });
    },
    _onClickShowAttachment: function (ev) {
        ev.preventDefault();
        var ids = $(ev.currentTarget).data('res-id');
        return this.do_action({
            name: _t('Attachments'),
            type: 'ir.actions.act_window',
            res_model: $(ev.currentTarget).data('model'),
            domain: [['id', 'in', ids]],
            views: [[false, 'kanban'], [false, 'list'], [false, 'form']],
            view_mode: 'kanban,list,form',
            target: 'current',
        });
    },
    _onClickCollapse:  function (ev) {
        ev.preventDefault();
        var $el = $(ev.currentTarget);
        $el.toggleClass('fa-caret-right fa-caret-down');
        var trId = $el.data('tr_id');
        var opId = $el.data('op_id');
        // var moTrId = $el.data('mo_tr_id');
        var moId = $el.data('id');
        // var moLevel = parseInt($el.data('level')) + 1;
        this.$('.' + trId).toggleClass('o_hidden');
        this.$('.' + opId).toggleClass('o_hidden');
        this.$('.parent_id_' + moId).toggleClass('o_hidden');
    },
    _reload: function () {
        var self = this;
        return this.get_html().then(function () {
            self.$el.html(self.data.lines);
            self._reload_report_type();
        });
    },
    _reload_report_type: function () {
        this.$('.o_mrp_bom_cost.o_hidden, .o_mrp_prod_cost.o_hidden').toggleClass('o_hidden');
        if (this.given_context.report_type === 'bom_structure') {
            this.$('.o_mrp_bom_cost').toggleClass('o_hidden');
        }
        if (this.given_context.report_type === 'bom_cost') {
            this.$('.o_mrp_prod_cost').toggleClass('o_hidden');
        }
    },
    _removeLines: function ($el) {
        var self = this;
        var activeID = $el.data('id');
        _.each(this.$('tr[parent_id='+ activeID +']'), function (parent) {
            var $parent = self.$(parent);
            var $el = self.$('tr[parent_id='+ $parent.data('id') +']');
            if ($el.length && activeID != $parent.data('id')) {
                self._removeLines($parent);
            }
            $parent.remove();
        });
    },
});

core.action_registry.add('mrp_production_report_ae', MrpBomReport);
return MrpBomReport;

});
