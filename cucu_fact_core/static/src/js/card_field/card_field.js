import {_t} from "@web/core/l10n/translation";
import {registry} from "@web/core/registry";
import {useInputField} from "@web/views/fields/input_field_hook";
import {standardFieldProps} from "@web/views/fields/standard_field_props";
import {useRecordObserver} from "@web/model/relational_model/utils";
import {Component, useState} from "@odoo/owl";

export class CardField extends Component {
    static template = "cucu_fact_core.CardField";
    static props = {
        ...standardFieldProps,
        placeholder_left: {type: String, optional: true, default: false},
    };

    static defaultProps = {
        decorations: {},
    };

    setup() {
        const value = this.props.record.data[this.props.name] || ""
        this.state = useState({
            input_left: value.length > 0 ? value.slice(0, 4) : "",
            input_right: value.length > 0 ? value.slice(-4) : "",
            value
        });
        const fieldComplete = `${this.state.input_left}00000000${this.state.input_right}`
        useInputField({
            getValue: () => fieldComplete,
            refName: 'input'
        });
        useRecordObserver((record) => {
            const value = record.data[this.props.name] || "";
            this.state.input_left = value.length > 0 ? value.slice(0, 4) : ""
            this.state.input_right = value.length > 0 ? value.slice(-4) : ""
            this.state.value = `${this.state.input_left}00000000${this.state.input_right}`
        });
        this.selectionStart = this.props.record.data[this.props.name]?.length || 0;
    }

    get formattedValueCard() {
        return this.props.record.data[this.props.name] || ""
    }

    onChange(newValue) {
        const fieldComplete = `${this.state.input_left}00000000${this.state.input_right}`
        this.props.record.update({[this.props.name]: fieldComplete});
    }

    onBlur() {
        this.selectionStart = `${this.state.input_left}00000000${this.state.input_right}`;
    }
}

export const cardField = {
    component: CardField,
    displayName: _t("Card Mask"),
    supportedTypes: ["char"]
};

registry.category("fields").add("card", cardField);
