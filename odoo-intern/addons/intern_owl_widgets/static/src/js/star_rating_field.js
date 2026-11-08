/** @odoo-module **/
import { Component, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { standardFieldProps } from "@web/views/fields/standard_field_props";

/**
 * Widget "intern_star_rating": hiển thị điểm 1-5 dạng sao, bấm vào sao để chấm điểm.
 * Dùng được cho field Selection (giá trị '1'..'5') và field Integer.
 */
export class StarRatingField extends Component {
    static template = "intern_owl_widgets.StarRatingField";
    static props = { ...standardFieldProps };

    setup() {
        this.state = useState({ hover: 0 });
        this.stars = [1, 2, 3, 4, 5];
    }

    get value() {
        return parseInt(this.props.record.data[this.props.name] || 0, 10);
    }

    get displayValue() {
        return this.state.hover || this.value;
    }

    starClass(star) {
        const icon = star <= this.displayValue ? "fa-star" : "fa-star-o";
        const clickable = this.props.readonly ? "" : " o_intern_star_clickable";
        return `fa ${icon} o_intern_star${clickable}`;
    }

    onClick(star) {
        if (this.props.readonly) {
            return;
        }
        const type = this.props.record.fields[this.props.name].type;
        // Selection lưu chuỗi '1'..'5', Integer lưu số
        this.props.record.update({ [this.props.name]: type === "selection" ? String(star) : star });
    }

    onEnter(star) {
        if (!this.props.readonly) {
            this.state.hover = star;
        }
    }

    onLeave() {
        this.state.hover = 0;
    }
}

export const starRatingField = {
    component: StarRatingField,
    displayName: "Star Rating",
    supportedTypes: ["selection", "integer"],
};

registry.category("fields").add("intern_star_rating", starRatingField);
