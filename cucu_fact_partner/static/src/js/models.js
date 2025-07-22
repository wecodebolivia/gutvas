/** @odoo-module */

import {PosStore} from "@point_of_sale/app/store/pos_store";
import {PosDB} from "@point_of_sale/app/store/db";
import {patch} from "@web/core/utils/patch";
import { unaccent } from "@web/core/utils/strings";

patch(PosStore.prototype, {
    async setup() {
        await super.setup(...arguments);
    },
    async _load_documents_ids() {
        return await this.env.services.rpc('/web/dataset/call_kw/pos.session/get_pos_ui_documents', {
            model: 'pos.session',
            method: 'get_pos_ui_documents',
            args: [[]],
            kwargs: {}
        });
    },
    async _processData(loadedData) {
        await super._processData(loadedData);
        this.documents_id = await this._load_documents_ids()
    }
})

patch(PosDB.prototype, {
    add_partners(partners) {
        var updated = {};
        var new_write_date = "";
        var partner;
        for (var i = 0, len = partners.length; i < len; i++) {
            partner = partners[i];

            var local_partner_date = (this.partner_write_date || "").replace(
                /^(\d{4}-\d{2}-\d{2}) ((\d{2}:?){3})$/,
                "$1T$2Z"
            );
            var dist_partner_date = (partner.write_date || "").replace(
                /^(\d{4}-\d{2}-\d{2}) ((\d{2}:?){3})$/,
                "$1T$2Z"
            );
            if (
                this.partner_write_date &&
                this.partner_by_id[partner.id] &&
                new Date(local_partner_date).getTime() + 1000 >=
                    new Date(dist_partner_date).getTime()
            ) {
                // FIXME: The write_date is stored with milisec precision in the database
                // but the dates we get back are only precise to the second. This means when
                // you read partners modified strictly after time X, you get back partners that were
                // modified X - 1 sec ago.
                continue;
            } else if (new_write_date < partner.write_date) {
                new_write_date = partner.write_date;
            }
            if (!this.partner_by_id[partner.id]) {
                this.partner_sorted.push(partner.id);
            } else {
                const oldPartner = this.partner_by_id[partner.id];
                if (oldPartner.barcode) {
                    delete this.partner_by_barcode[oldPartner.barcode];
                }
            }
            if (partner.barcode) {
                this.partner_by_barcode[partner.barcode] = partner;
            }
            updated[partner.id] = partner;
            this.partner_by_id[partner.id] = partner;
        }

        this.partner_write_date = new_write_date || this.partner_write_date;

        const updatedChunks = new Set();
        const CHUNK_SIZE = 100;
        for (const id in updated) {
            const chunkId = Math.floor(id / CHUNK_SIZE);
            if (updatedChunks.has(chunkId)) {
                // another partner in this chunk was updated and we already rebuild the chunk
                continue;
            }
            updatedChunks.add(chunkId);
            // If there were updates, we need to rebuild the search string for this chunk
            let searchString = "";

            for (let id = chunkId * CHUNK_SIZE; id < (chunkId + 1) * CHUNK_SIZE; id++) {
                if (!(id in this.partner_by_id)) {
                    continue;
                }
                const partner = this.partner_by_id[id];
                partner.address =
                    (partner.street ? partner.street + ", " : "") +
                    (partner.country_id ? partner.country_id[1] : "");
                searchString += this._partner_search_string(partner);
            }
            this.partner_search_strings[chunkId] = unaccent(searchString);
        }
        return Object.keys(updated).length;
    },
    _partner_search_string(partner) {
        var str = partner.name || "";
        if (partner.parent_name) {
            str += "|" + partner.parent_name;
        }
        if (partner.nit_client) {
            str += "|" + partner.nit_client;
        }
        str = "" + partner.id + ":" + str.replace(":", "").replace(/\n/g, " ") + "\n";
        return str;
    }
})