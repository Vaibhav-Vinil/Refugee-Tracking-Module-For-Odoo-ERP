# -*- coding: utf-8 -*-

from odoo import api, fields, models


class RefugeeVolunteerGroup(models.Model):
    _name = "refugee.volunteer.group"
    _description = "Volunteer Group"

    name = fields.Char(string="Group Name", required=True)
    description = fields.Text(string="Description")
    volunteer_ids = fields.One2many("refugee.volunteer", "group_id", string="Volunteers")


class RefugeeVolunteer(models.Model):
    _name = "refugee.volunteer"
    _description = "Refugee Volunteer"

    name = fields.Char(string="Volunteer Name", required=True)
    phone = fields.Char(string="Phone Number")
    email = fields.Char(string="Email")
    group_id = fields.Many2one("refugee.volunteer.group", string="Volunteer Group")
    task_ids = fields.Many2many("refugee.logistics.task", string="Assigned Tasks")
    photo = fields.Image("Photo", max_width=1024, max_height=1024)
    status = fields.Selection([
        ('available', 'Available'),
        ('unavailable', 'Unavailable'),
        ('on_duty', 'On Duty')
    ], compute='_compute_status', store=True, string="Status")

    @api.depends('task_ids', 'task_ids.status')
    def _compute_status(self):
        for rec in self:
            if any(t.status == 'in_progress' for t in rec.task_ids):
                rec.status = 'on_duty'
            else:
                rec.status = 'available'
