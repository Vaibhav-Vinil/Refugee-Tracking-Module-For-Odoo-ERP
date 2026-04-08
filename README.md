# Onwards - Refugee Crisis Management ERP

<p align="center">
  <a href="https://www.youtube.com/watch?v=vHOM0tKLPxs" target="_blank">
    <img src="https://img.youtube.com/vi/vHOM0tKLPxs/maxresdefault.jpg" alt="Onwards Demo Video" style="width:100%;">
  </a>
  <br>
  <b>Click the image above to watch the demonstration.</b>
</p>

---

Onwards is an Odoo 19 module for managing refugee operations across profiles, families, camps, resources, logistics, volunteers, and reporting in one coordinated workflow.

An enterprise-grade humanitarian management system built on Odoo ERP, designed to coordinate refugee identities, camp operations, automated logistics, and continuous resource distribution during crisis situations.

This module provides a centralized, scalable, and real-time platform for NGOs, governments, and relief organizations to efficiently manage large-scale humanitarian efforts, bypassing traditional paperwork and manual coordination.

## Overview

During humanitarian crises, administrating complex refugee populations, managing rapid resource consumption, and distributing aid effectively is critical.

Onwards addresses these operational hurdles by integrating:

- Deep Demographic and Family Management
- Physical Infrastructure and Camp Control
- Automated Supply Chain and Resource Inventory
- Workforce and Logistics Synchronization

into a single unified ERP ecosystem.


## Current Scope (Up to Date)

The current module version (`19.0.1.0.1`) includes:

- Refugee profiles with identity, journey stage, medical/vulnerability details, QR/ID card support.
- Family management with head-of-family constraints and family status tracking.
- Camp management with geolocation, occupancy, and "Location Unknown" support.
- Resource inventory with stock progress and low-stock automation.
- Logistics task workflows and delivery-driven stock updates.
- Resource request approvals that can generate logistics deliveries.
- Volunteer operations and user-linked volunteer profile helpers.
- Skill and camp-role matching for workforce allocation.
- Aid distribution tracking for direct beneficiary delivery.
- Dashboard entries (graph, pivot, camp map) and a translator client action.

## Comprehensive Feature List

### Refugee Profiles and Advanced Demographics

- **Basic Registration:** Track names, gender, nationalities (linked to `res.country`), and languages spoken (`res.lang`).
- **Biometric Simulation:** Simulated fingerprint hashing (SHA-256 via ID + Name) for unique identification and duplicate prevention.
- **Medical and Vulnerability Tracking:**
  - Track medical conditions and flag profiles requiring urgent care.
  - Handle deceased statuses dynamically, including family-head reassignment where applicable.
- **Journey Stage Lifecycle:** Monitor intake statuses from `Border intake` -> `Vetting` -> `Medical` -> `Assigned` to `Relocated / Integrated`.

### Family Unit Management

- **Intelligent Family Grouping:** Bind refugee profiles into synchronized family units with strict 1:1 head-of-family constraints.
- **Geographic Status Syncing:** Real-time family integrity computation:
  - `Reunited`: All family members reside in the same camp.
  - `Separated`: Members are split across multiple known camps.
  - `Location Unknown`: One or more members are missing or placed in the specialized "Location Unknown" camp.

### Camp Infrastructure Control

- **Physical Locations:** Coordinate shelters with geolocation data (latitude/longitude).
- **Occupancy Automation:** Track active occupancy against camp capacity and raise overcrowding indicators when limits are exceeded.
- **Sentinel Location Support:** Built-in handling for "Location Unknown" refugee status routing.

### Automated Resource Inventory

- **Granular Categories:** Monitor `Food`, `Water`, `Medical`, and `Other`.
- **Dynamic Stock Fill Percentages:** Compute real-time `Quantity Available` versus `Quantity Required`.
- **Automated Emergency Resupply:** Low stock threshold checks can automatically create high-priority logistics delivery tasks.

### Logistics and Auto-Supply Chain

- **Task Types:** `Delivery`, `Transport`, and `Setup`, with prioritization from `Low` to `Very High`.
- **Workflow State Machine:** `To Do` -> `Accepted` -> `Authorized` -> `In Progress` -> `Done` (or `Cancelled` / `Stopped Abruptly`).
- **Strict Authorization:** Authorization flow is restricted to appropriate administrative roles.
- **Inventory Injection:** Completing `Delivery` tasks updates target camp resource quantities.

### Resource Requests

- Capture inter-camp/personnel critical supply requests.
- Admin approval can forward requests into structured logistics delivery tasks.

### Volunteer Management

- Assign volunteers to operations and track availability.
- Infer volunteer duty status from active logistics assignments.
- Allow eligible volunteers to self-enroll into open logistics tasks.

### Operational Role Assignments and Skill Matrix

- Compare refugee skills with camp role requirements.
- Enforce role capacity constraints.
- Support algorithmic and assisted role allocation workflows.

### Direct Aid Distribution Log

- Track direct beneficiary allocations with auditable entries (date, volunteer, recipient).

## Functional Areas

### 1) Core Models

- `refugee.profile`
- `refugee.family`
- `refugee.camp`
- `refugee.resource.inventory`
- `refugee.logistics.task`
- `refugee.resource.request`
- `refugee.volunteer`
- `refugee.skill`
- `refugee.camp.role`
- `refugee.aid.distribution`
- `res.users` extension hooks for refugee/volunteer flows

### 2) Security and Roles

Defined in `security/refugee_security.xml` and `security/ir.model.access.csv`:

- `Admin`
- `Volunteer`
- `Camp In Charge`
- `Refugee`

Includes record rules for camp-scoped access (profiles/resources/logistics/requests) and open visibility where needed (for example, family tracking).

### 3) Menus and UI

Main app menu: `Onwards`

Current menu items include:

- Refugees
- Families
- Camps
- Camp Roles
- Skills
- Resources
- Resource Requests
- Logistics
- Dashboard (Population Graph, Pivot, Camp Map)
- Translator

### 4) Reports

- Refugee ID Card PDF report (`report/refugee_reports.xml`)
- Includes QR code rendering and compact card layout for print/export.

### 5) Automation/Data

- Sequence generation: `data/refugee_sequence.xml`
- Location Unknown seed record: `data/refugee_location_unknown.xml`
- Scheduled low-stock check cron: `data/refugee_cron.xml`
- Optional demo records: `demo/demo_data.xml`

### 6) Frontend Assets

Loaded through `web.assets_backend`:

- `static/src/camp_map/camp_map.js`
- `static/src/fields/family_head_boolean_field.js`
- `static/src/fields/stock_progress_bar_field.js`
- `static/src/translator/translator.js`

## Installation

### Prerequisites

- Odoo `19.0`
- Python 3.x
- PostgreSQL
- Python dependency: `qrcode`

Install dependency:

```bash
pip install qrcode
```

### Setup

1. Place this addon in your Odoo addons path (for this repo, under `Workshop/`).
2. Restart Odoo server.
3. In Apps, click `Update Apps List`.
4. Search and install `Onwards` (`refugee_crisis_erp`).

## Repository Notes

- Manifest: `__manifest__.py`
- Model imports: `models/__init__.py`
- Seed utility script: `seed_data_v2.py`
- Demo video: [`Demonstration.mp4`](./Demonstration.mp4)

## Technical Architecture Overview

Developed for Odoo 19 using native ORM models, computed fields, onchange/constraint validations, record rules, scheduled jobs, QWeb reporting, and web client assets.

Key architecture references:

- Access controls: `security/ir.model.access.csv`
- Role groups and record rules: `security/refugee_security.xml`
- Scheduled automation: `data/refugee_cron.xml`
- Sequence and base records: `data/refugee_sequence.xml`, `data/refugee_location_unknown.xml`
- Report template: `report/refugee_reports.xml`
- UI assets: `static/src/camp_map/camp_map.js`, `static/src/fields/family_head_boolean_field.js`, `static/src/fields/stock_progress_bar_field.js`, `static/src/translator/translator.js`
