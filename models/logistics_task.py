# -*- coding: utf-8 -*-

from odoo import api, fields, models


class RefugeeLogisticsTask(models.Model):
    """
    Manages logistics operations, such as transporting resources between camps, 
    setting up infrastructure, or distributing large-scale aid. 
    Controls state transitions from 'todo' up to 'done', affecting the underlying inventory.
    """
    _name = "refugee.logistics.task"
    _description = "Logistics Task"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "priority desc, id desc"
    _rec_name = "resource_id"

    task_type = fields.Selection(
        selection=[
            ("delivery", "Delivery"),
            ("transport", "Transport"),
            ("setup", "Setup"),
        ],
        default="delivery",
        required=True,
    )
    resource_id = fields.Many2one(
        "refugee.resource.inventory",
        string="Resource",
        ondelete="restrict",
        required=True,
        tracking=True,
    )
    camp_id = fields.Many2one(
        "refugee.camp.management",
        string="Camp",
        tracking=True,
    )
    quantity = fields.Integer(string="Quantity", default=1, tracking=True)
    refugee_id = fields.Many2one(
        "refugee.profile",
        string="Beneficiary",
        ondelete="set null",
    )
    distributed_by_id = fields.Many2one(
        "refugee.volunteer",
        string="Distributed By",
        ondelete="set null",
    )
    request_id = fields.Many2one(
        "refugee.resource.request",
        string="Source Request",
        ondelete="set null",
        readonly=True,
    )
    volunteer_ids = fields.Many2many(
        "refugee.volunteer",
        string="Assigned Volunteers",
    )
    status = fields.Selection(
        selection=[
            ("todo", "To Do"),
            ("accepted", "Accepted"),
            ("authorized", "Authorized"),
            ("in_progress", "In Progress"),
            ("done", "Done"),
            ("cancelled", "Cancelled"),
            ("stopped", "Stopped Abruptly"),
        ],
        default="todo",
        tracking=True,
        group_expand=True,
    )
    priority = fields.Selection(
        selection=[("0", "Low"), ("1", "Normal"), ("2", "High"), ("3", "Very High")],
        default="1",
    )
    source_location = fields.Char()
    destination = fields.Char()
    date = fields.Datetime(default=fields.Datetime.now, string="Date")
    notes = fields.Text("Notes")

    def action_tick(self):
        """
        Progresses the logistics task state forward.
        Enforces that only administrators can authorize accepted tasks.
        Upon reaching the 'done' state for deliveries, it increments the destination 
        camp's resource inventory with the delivered quantity.
        """
        is_admin = self.env.user.has_group('refugee_crisis_erp.group_refugee_manager')
        for rec in self:
            if rec.status == 'todo':
                rec.status = 'accepted'
            elif rec.status == 'accepted':
                if not is_admin:
                    from odoo.exceptions import UserError
                    raise UserError("Only an Administrator can authorize accepted logistics tasks.")
                rec.status = 'authorized'
            elif rec.status == 'authorized':
                rec.status = 'in_progress'
            elif rec.status == 'in_progress':
                rec.status = 'done'
                # Delivery completed add quantity to camp's resource inventory
                if rec.resource_id and rec.quantity > 0 and rec.task_type == 'delivery':
                    rec.resource_id.sudo().write({
                        'quantity_available': rec.resource_id.quantity_available + rec.quantity
                    })
        return True

    def action_cross(self):
        """
        Cancels or abruptly stops a logistics task depending on its current state.
        Tasks in progress become 'stopped', while earlier states are marked as 'cancelled'.
        """
        for rec in self:
            if rec.status in ('todo', 'accepted', 'authorized'):
                rec.status = 'cancelled'
            elif rec.status == 'in_progress':
                rec.status = 'stopped'
        return True

    def action_enroll(self):
        """Let the current volunteer enroll themselves into this task."""
        volunteer = self.env.user.volunteer_id
        if not volunteer:
            from odoo.exceptions import UserError
            raise UserError("Your user account is not linked to a Volunteer profile. Please contact an administrator.")
        for rec in self:
            if volunteer not in rec.volunteer_ids:
                rec.volunteer_ids = [(4, volunteer.id)]
        return True
