# -*- coding: utf-8 -*-

import base64
import hashlib
import io
import logging

from odoo import _, api, fields, models

_logger = logging.getLogger(__name__)


class RefugeeProfile(models.Model):
    _name = "refugee.profile"
    _description = "Refugee Profile"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "refugee_id, name"

    name = fields.Char(string="Full Name", required=True, tracking=True)
    family_name = fields.Char(string="Family Surname", tracking=True, index=True)
    refugee_id = fields.Char(
        string="Refugee ID",
        copy=False,
        readonly=True,
        index=True,
    )
    id_card_photo = fields.Image(string="ID Photo", max_width=1920, max_height=1920)
    qr_code = fields.Binary(string="QR Code", compute="_compute_qr_code", attachment=False)
    fingerprint_hash = fields.Char(
        string="Biometric Hash (simulated)",
        compute="_compute_fingerprint_hash",
        store=True,
        readonly=True,
    )

    gender = fields.Selection(
        selection=[("male", "Male"), ("female", "Female"), ("other", "Other / Unspecified")],
        tracking=True,
    )
    date_of_birth = fields.Date(string="Date of Birth", tracking=True)
    age = fields.Integer(compute="_compute_age", store=True)
    nationality_id = fields.Many2one("res.country", string="Nationality")
    languages_spoken_ids = fields.Many2many("res.lang", string="Languages Spoken")

    family_id = fields.Many2one("refugee.family", string="Family", ondelete="set null", tracking=True)
    is_head_of_household = fields.Boolean(string="Head of Household")
    is_head_of_family = fields.Boolean(string="Head of Family")
    camp_id = fields.Many2one(
        "refugee.camp.management",
        string="Current Camp / Shelter",
        tracking=True,
        index=True,
    )

    skill_ids = fields.Many2many("refugee.skill", string="Skills")
    assigned_role_id = fields.Many2one(
        "refugee.camp.role",
        string="Assigned Role",
        domain="[('camp_id', '=', camp_id)]",
        tracking=True,
    )

    id_number = fields.Char(string="Legacy ID / Paper ID")
    journey_stage = fields.Selection(
        selection=[
            ("draft", "Draft — Border intake"),
            ("vetting", "Vetting"),
            ("medical", "Medical"),
            ("assigned", "Assigned"),
            ("integrated", "Relocated / Integrated"),
        ],
        default="draft",
        tracking=True,
        group_expand=True,
    )
    registration_status = fields.Selection(
        selection=[
            ("registered", "Registered"),
            ("assigned", "Assigned"),
            ("relocated", "Relocated"),
        ],
        default="registered",
        tracking=True,
    )

    vulnerability_level = fields.Selection(
        selection=[
            ("low", "Low"),
            ("medium", "Medium"),
            ("high", "High"),
            ("critical", "Critical"),
        ],
        default="low",
        tracking=True,
    )
    kanban_color = fields.Integer(
        string="Color Index",
        compute="_compute_kanban_color",
    )

    is_unaccompanied_minor = fields.Boolean()
    medical_conditions = fields.Text()
    requires_urgent_care = fields.Boolean(tracking=True)
    health_status = fields.Selection(
        selection=[
            ("unknown", "Unknown"),
            ("stable", "Stable"),
            ("needs_followup", "Needs Follow-up"),
            ("critical", "Critical"),
        ],
        default="unknown",
    )

    active = fields.Boolean(default=True)

    aid_line_ids = fields.One2many("refugee.aid.distribution", "refugee_id", string="Aid Lines")
    aid_count = fields.Integer(compute="_compute_counts")
    family_member_count = fields.Integer(compute="_compute_counts")
    task_ids = fields.One2many("refugee.logistics.task", "assigned_to", string="Logistics Tasks")
    task_count = fields.Integer(compute="_compute_counts")

    @api.depends("date_of_birth")
    def _compute_age(self):
        today = fields.Date.today()
        for rec in self:
            if not rec.date_of_birth:
                rec.age = 0
                continue
            born = rec.date_of_birth
            rec.age = today.year - born.year - ((today.month, today.day) < (born.month, born.day))

    @api.depends("refugee_id", "name")
    def _compute_fingerprint_hash(self):
        for rec in self:
            raw = f"{rec.refugee_id or ''}|{rec.name or ''}".encode("utf-8")
            rec.fingerprint_hash = hashlib.sha256(raw).hexdigest()

    def _get_public_form_url(self):
        self.ensure_one()
        base = self.env["ir.config_parameter"].sudo().get_param("web.base.url", "").rstrip("/")
        if not base:
            base = "http://localhost:8069"
        return f"{base}/web#id={self.id}&model=refugee.profile&view_type=form"

    @api.depends("refugee_id", "name")
    def _compute_qr_code(self):
        try:
            import qrcode
        except ImportError:
            _logger.warning("python qrcode package not installed; QR codes will be empty.")
            for rec in self:
                rec.qr_code = False
            return
        for rec in self:
            if not rec.id:
                rec.qr_code = False
                continue
            url = rec._get_public_form_url()
            img = qrcode.make(url)
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            rec.qr_code = base64.b64encode(buf.getvalue())

    @api.depends("vulnerability_level")
    def _compute_kanban_color(self):
        color_map = {"low": 0, "medium": 2, "high": 8, "critical": 9}
        for rec in self:
            rec.kanban_color = color_map.get(rec.vulnerability_level, 0)

    @api.depends("family_id", "aid_line_ids", "task_ids")
    def _compute_counts(self):
        for rec in self:
            rec.aid_count = len(rec.aid_line_ids)
            rec.task_count = len(rec.task_ids)
            if rec.family_id:
                rec.family_member_count = self.search_count(
                    [("family_id", "=", rec.family_id.id), ("active", "=", True)]
                )
            else:
                rec.family_member_count = 0

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("family_name") and not vals.get("family_id"):
                Family = self.env["refugee.family"]
                family = Family.search([("name", "=", vals["family_name"])], limit=1)
                if not family:
                    family = Family.create({"name": vals["family_name"]})
                vals["family_id"] = family.id
            if not vals.get("refugee_id"):
                vals["refugee_id"] = self.env["ir.sequence"].next_by_code("refugee.profile.id")
        records = super().create(vals_list)
        records._sync_family_head()
        for rec in records:
            if rec.requires_urgent_care:
                rec._notify_medical_coordinators()
        return records

    def write(self, vals):
        notify_candidates = self.env["refugee.profile"]
        if vals.get("requires_urgent_care"):
            notify_candidates = self.filtered(lambda r: not r.requires_urgent_care)
        res = super().write(vals)
        if any(k in vals for k in ("is_head_of_family", "family_id", "is_head_of_household")):
            self._sync_family_head()
        if vals.get("requires_urgent_care"):
            for rec in notify_candidates:
                if rec.requires_urgent_care:
                    rec._notify_medical_coordinators()
        return res

    def _notify_medical_coordinators(self):
        self.ensure_one()
        group = self.env.ref("refugee_crisis_erp.group_refugee_medical", raise_if_not_found=False)
        if not group or not group.user_ids:
            return
        body = _("Refugee %s (%s) requires urgent medical attention.") % (
            self.name,
            self.refugee_id or "",
        )
        Mail = self.env["mail.mail"].sudo()
        company = self.env.company
        email_from = company.email_formatted or company.email or self.env.user.email
        for user in group.user_ids:
            email = user.partner_id.email
            if not email:
                continue
            Mail.create(
                {
                    "subject": _("Urgent care: %s") % self.name,
                    "body_html": f"<p>{body}</p>",
                    "email_to": email,
                    "email_from": email_from,
                }
            ).send()

    def _sync_family_head(self):
        for rec in self:
            if not rec.family_id:
                continue
            if rec.is_head_of_family or rec.is_head_of_household:
                rec.family_id.head_id = rec

    def action_open_family_members(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Family Members",
            "res_model": "refugee.profile",
            "view_mode": "list,form",
            "domain": [("family_id", "=", self.family_id.id)] if self.family_id else [("id", "=", False)],
        }

    def action_open_aid(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Aid Received",
            "res_model": "refugee.aid.distribution",
            "view_mode": "list,form",
            "domain": [("refugee_id", "=", self.id)],
            "context": {"default_refugee_id": self.id},
        }

    def action_open_tasks(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Tasks",
            "res_model": "refugee.logistics.task",
            "view_mode": "list,form,kanban",
            "domain": [("assigned_to", "=", self.id)],
            "context": {"default_assigned_to": self.id},
        }

    def action_auto_assign_roles(self):
        """Match skills to camp roles with free capacity."""
        Role = self.env["refugee.camp.role"]
        assigned = 0
        for refugee in self:
            if not refugee.camp_id or refugee.assigned_role_id:
                continue
            roles = Role.search([("camp_id", "=", refugee.camp_id.id)])
            for role in roles:
                if role.capacity and role.assigned_count >= role.capacity:
                    continue
                if not role.required_skill_ids:
                    continue
                needed = set(role.required_skill_ids.ids)
                have = set(refugee.skill_ids.ids)
                if needed.issubset(have):
                    refugee.assigned_role_id = role
                    assigned += 1
                    break
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": "Role assignment",
                "message": f"Assigned roles for {assigned} profile(s).",
                "type": "success",
                "sticky": False,
            },
        }

    @api.onchange("skill_ids", "camp_id")
    def _onchange_suggest_role(self):
        if not self.camp_id or not self.skill_ids:
            return
        roles = self.env["refugee.camp.role"].search(
            [("camp_id", "=", self.camp_id.id)]
        )
        have = set(self.skill_ids.ids)
        for role in roles:
            needed = set(role.required_skill_ids.ids)
            if needed and needed.issubset(have) and (
                not role.capacity or role.assigned_count < role.capacity
            ):
                self.assigned_role_id = role
                break
