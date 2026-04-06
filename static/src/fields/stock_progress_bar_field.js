/** @odoo-module **/

import { registry } from "@web/core/registry";
import {
    ProgressBarField,
    progressBarField,
} from "@web/views/fields/progress_bar/progress_bar_field";

/**
 * A custom progress bar widget designed specifically to color-code inventory thresholds dynamically.
 * Overrides the default progress bar field from the web core.
 */
export class StockProgressBarField extends ProgressBarField {
    /**
     * Determines the bootstrap bg-class color representation based on current value.
     * Evaluates danger for low stock, warning for medium bounds, and success when sufficiently filled.
     */
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
