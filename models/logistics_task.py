# -*- coding: utf-8 -*-

from odoo import fields, models


class RefugeeLogisticsTask(models.Model):
    _name = "refugee.logistics.task"
    _description = "Logistics Task"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "priority desc, id desc"

    name = fields.Char(required=True, tracking=True)
    task_type = fields.Selection(
        selection=[
            ("delivery", "Delivery"),
            ("transport", "Transport"),
            ("setup", "Setup"),
        ],
        default="delivery",
        required=True,
    )
    volunteer_ids = fields.Many2many(
        "refugee.volunteer",
        string="Assigned Volunteers",
    )
    status = fields.Selection(
        selection=[
            ("todo", "To Do"),
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
    resource_id = fields.Many2one("refugee.resource.inventory", ondelete="set null")
    source_location = fields.Char()
    destination = fields.Char()

    def action_tick(self):
        for rec in self:
            if rec.status == 'todo':
                rec.status = 'in_progress'
            elif rec.status == 'in_progress':
                rec.status = 'done'
        return True

    def action_cross(self):
        for rec in self:
            if rec.status == 'todo':
                rec.status = 'cancelled'
            elif rec.status == 'in_progress':
                rec.status = 'stopped'
        return True
