/** @odoo-module **/

import { registry } from "@web/core/registry";
import {
    ProgressBarField,
    progressBarField,
} from "@web/views/fields/progress_bar/progress_bar_field";

export class StockProgressBarField extends ProgressBarField {
    get progressBarColorClass() {
        const maxV = this.maxValue;
        if (!maxV || maxV <= 0) {
            return this.currentValue > 0 ? "bg-success" : "bg-danger";
        }
        const pct = (this.currentValue / maxV) * 100;
        if (pct <= 25) {
            return "bg-danger";
        }
        if (pct <= 75) {
            return "bg-warning";
        }
        return "bg-success";
    }
}

registry.category("fields").add("stock_progressbar", {
    ...progressBarField,
    component: StockProgressBarField,
});
