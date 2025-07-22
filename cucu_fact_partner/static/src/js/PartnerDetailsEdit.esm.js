/** @odoo-module **/
import {PartnerDetailsEdit} from "@point_of_sale/app/screens/partner_list/partner_editor/partner_editor";
import {patch} from "@web/core/utils/patch";
import {ErrorPopup} from "@point_of_sale/app/errors/popups/error_popup";
import {_t} from "@web/core/l10n/translation";

patch(PartnerDetailsEdit.prototype, {
    setup() {
        super.setup(...arguments);
        this.intFields = ["country_id", "state_id", "property_product_pricelist", 'doc_id'];
        this.changes.nit_client = this.props.partner.nit_client || null;
        this.changes.client_code = this.props.partner.client_code || null;
        this.changes.reason_social = this.props.partner.reason_social || null;
        this.changes.complement = this.props.partner.complement || null;
        this.changes.cucu_email = this.props.partner.cucu_email || this.pos.company.email;
        this.changes.doc_id = this.props?.partner?.doc_id && this.props?.partner?.doc_id[0];
    },
    saveChanges() {
        if (!this.changes?.doc_id || this.changes?.doc_id === "") {
            return this.popup.add(ErrorPopup, {
                title: _t('ERROR'),
                body: _t('SELECCIONE EL TIPO DOCUMENTO'),
            });
        }
        if (!this.changes?.reason_social || this.changes?.reason_social === "") {
            return this.popup.add(ErrorPopup, {
                title: _t('ERROR'),
                body: _t('RAZON SOCIAL NO VALIDO'),
            });
        }
        if (!this.changes?.nit_client || this.changes?.nit_client === "") {
            return this.popup.add(ErrorPopup, {
                title: _t('ERROR'),
                body: _t('NIT NO VALIDO'),
            });
        }
        if (!this.changes?.cucu_email || this.changes?.cucu_email === "") {
            return this.popup.add(ErrorPopup, {
                title: _t('ERROR'),
                body: _t('EMAIL NO VALIDO'),
            });
        }

        const processedChanges = {};
        for (const [key, value] of Object.entries(this.changes)) {
            if (this.intFields.includes(key)) {
                processedChanges[key] = parseInt(value) || false;
            } else {
                processedChanges[key] = value;
            }
        }
        if (
            processedChanges.state_id &&
            this.pos.states.find((state) => state.id === processedChanges.state_id)
                .country_id[0] !== processedChanges.country_id
        ) {
            processedChanges.state_id = false;
        }

        if ((!this.props.partner.name && !processedChanges.name) || processedChanges.name === "") {
            return this.popup.add(ErrorPopup, {
                title: _t("A Customer Name Is Required"),
            });
        }
        processedChanges.id = this.props.partner.id || false;
        this.props.saveChanges(processedChanges);
    }
});