odoo.define('cucu_fact_config.kanban_branch_button', function (require) {
    "use strict";
    const KanbanController = require('web.KanbanController');
    const KanbanView = require('web.KanbanView');
    const viewRegistry = require('web.view_registry');
    
    const KanbanButton = KanbanController.include({
        buttons_template: 'cucu_fact_core.button',
        events: _.extend({}, KanbanController.prototype.events, {
            'click .cucu_branch_open': '_action_sync_branch',
        }),
        _action_sync_branch: function () {
            const self = this;
            this._rpc({
                model: "cucu.branch.office",
                method: "action_sync_branch_office",
                args: [{data: "1"}],
            }).then(res => {
                
            }).catch(err => {

            })
        }
    });
    const CucuKanbanView = KanbanView.extend({
        config: _.extend({}, KanbanView.prototype.config, {
            Controller: KanbanButton
        }),
    });
    viewRegistry.add('button_in_kanban_branch', CucuKanbanView);
});
