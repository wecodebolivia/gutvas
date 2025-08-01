/** @odoo-module */
import {ListController} from "@web/views/list/list_controller";
import {registry} from '@web/core/registry';
import {listView} from '@web/views/list/list_view';

export class CoreBranchController extends ListController {
    setup() {
        super.setup();
    }

    async action_sync_branch() {
        debugger;
        try {
            await this.env.services.rpc('/web/dataset/call_kw/cucu.branch.office/action_sync_branch_office', {
                model: 'cucu.branch.office',
                method: 'action_sync_branch_office',
                args: [[]],
                kwargs: {}
            });
            await this.actionService.loadState();
        } catch (err) {
            console.error(err)
        }
    }
}

registry.category("views").add("button_in_tree_branch", {
    ...listView,
    Controller: CoreBranchController,
    buttonTemplate: "cucu_fact_core.buttons",
});