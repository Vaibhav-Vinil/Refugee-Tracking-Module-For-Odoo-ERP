/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { registry } from "@web/core/registry";
import { ConfirmationDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { useService } from "@web/core/utils/hooks";
import { BooleanField } from "@web/views/fields/boolean/boolean_field";
import { booleanField } from "@web/views/fields/boolean/boolean_field";

/**
 * A custom boolean field widget that intercepts toggling the 'is_head_of_family' status.
 * If toggled TRUE on a profile, it issues an ORM call to check if a conflict exists 
 * (e.g. replacing an existing head). It prompts the user via a modal before succeeding.
 */
export class FamilyHeadBooleanField extends BooleanField {
    static template = "web.BooleanField";

    setup() {
        super.setup();
        this.dialog = useService("dialog");
        this.orm = useService("orm");
    }

    /**
     * Intercepts UI changes. Halts direct propagation if switching to TRUE, 
     * evaluating global family constraints iteratively via prompt checking function.
     */
    async onChange(newValue) {
        if (!newValue) {
            super.onChange(newValue);
            return;
        }
        const record = this.props.record;
        this.state.value = false;
        const resId = typeof record.resId === "number" ? record.resId : 0;
        const fam = record.data.family_id;
        const familyId = Array.isArray(fam) && fam[0] ? fam[0] : 0;
        const name = record.data.name || "";
        const prompt = await this.orm.call("refugee.profile", "get_family_head_change_prompt", [
            resId,
            familyId,
            name,
        ]);
        const apply = () => {
            this.state.value = true;
            record.update({ is_head_of_family: true });
        };
        if (!prompt.need_confirm) {
            apply();
            return;
        }
        this.dialog.add(ConfirmationDialog, {
            title: _t("Change head of family"),
            body: prompt.message,
            confirm: () => apply(),
            confirmLabel: _t("Proceed"),
            cancel: () => {},
        });
    }
}

registry.category("fields").add("family_head_boolean", {
    ...booleanField,
    component: FamilyHeadBooleanField,
    displayName: _t("Family head (confirm)"),
});
