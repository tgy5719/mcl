odoo.define('account_reports.ActionManagerTests', function (require) {
"use strict";

var testUtils = require('web.test_utils');

var createActionManager = testUtils.createActionManager;

QUnit.module('ActionManager', {
    beforeEach: function () {
        this.actions = [{
            id: 1,
            data: {
                model: 'some_model',
                options: {
                    someOption: true,
                },
                output_format: 'pdf',
            },
            type: 'ir_actions_account_report_download',
        }];
    },
}, function () {
    QUnit.module('Account Report Downloard actions');

    QUnit.test('can execute account report download actions', function (assert) {
        assert.expect(5);

        var actionManager = createActionManager({
            actions: this.actions,
            mockRPC: function (route, args) {
                assert.step(args.method || route);
                return this._super.apply(this, arguments);
            },
            session: {
                get_file: function (params) {
                    assert.step(params.url);
                    assert.deepEqual(params.data, {
                        model: 'some_model',
                        options: {
                            someOption: true,
                        },
                        output_format: 'pdf',
                    }, "should give the correct data");
                    params.complete();
                },
            },
        });
        actionManager.doAction(1);

        assert.verifySteps([
            '/web/action/load',
            '/web/static/src/img/spin.png', // block UI image
            '/account_reports',
        ]);

        actionManager.destroy();
    });
});

});
