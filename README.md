# Onwards – Refugee Crisis Management ERP

An **enterprise-grade humanitarian management system** built on Odoo ERP, designed to coordinate refugee identities, camp operations, automated logistics, and continuous resource distribution during crisis situations.

This module provides a **centralized, scalable, and real-time platform** for NGOs, governments, and relief organizations to efficiently manage large-scale humanitarian efforts, bypassing traditional paperwork and manual coordination.

## Overview

During humanitarian crises, administrating complex refugee populations, managing rapid resource consumption, and distributing aid effectively is critical.

**Onwards** addresses these operational hurdles by integrating:
- Deep Demographic & Family Management
- Physical Infrastructure & Camp Control
- Automated Supply Chain & Resource Inventory
- Workforce & Logistics Synchronization 

into a **single unified ERP ecosystem**.

## Comprehensive Feature List

### Refugee Profiles & Advanced Demographics
- **Basic Registration**: Track names, gender, nationalities (linked to `res.country`), and languages spoken (`res.lang`).
- **Biometric Simulation**: Includes simulated fingerprint hashing (SHA-256 via ID + Name) for unique identification and prevention of duplicate registrations.
- **Medical & Vulnerability Tracking**: 
  - Tracks specific medical conditions and flags profiles requiring **urgent care**.
  - Registers deceased statuses dynamically. Automatically demotes deceased family heads and promotes valid successors.
- **Journey Stage Lifecycle**: Monitor intake statuses from `Border intake` → `Vetting` → `Medical` → `Assigned` to `Relocated / Integrated`.

### Family Unit Management
- **Intelligent Family Grouping**: Binds refugee profiles into synchronized family units with strict, database-level 1:1 constraints to ensure only one Head of Household/Family exists at a time.
- **Geographic Status Syncing**: Real-time computation of structural integrity:
  - `Reunited`: All family members reside in identical camps.
  - `Separated`: Members are geographically split across multiple known camps (includes voluntary separation notes).
  - `Location Unknown`: One or more members are flagged as missing or placed in the specialized "Location Unknown" camp.

### Camp Infrastructure Control
- **Physical Locations**: Coordinate shelters utilizing geo-positioning (latitude, longitude) and specialized hierarchy tracking.
- **Occupancy Automation**: Defines total capacity per shelter. Automatically tracks the sum of all active, living refugees inside a camp and emits `overcrowded` warnings automatically if bounds are exceeded.
- **Sentinel Locations**: Utilizes specialized logic to identify unaccounted individuals through 'Location Unknown' mechanisms.

### Automated Resource Inventory
- **Granular Categories**: Monitors `Food`, `Water`, `Medical`, and `Other` utilities.
- **Dynamic Stock Fill Percentages**: Computes real-time `Quantity Available` vs `Quantity Required` to generate visual progress indicators. 
- **Automated Emergency Resupply**: If inventory dips drastically (below 20% of quota), the inventory kernel circumvents manual workflows and automatically spawns a Priority High delivery logistics task.

### Logistics & Auto-Supply Chain
- **Task Types**: Handles `Delivery`, `Transport`, and infrastructural `Setup`. Enforces prioritization scales (`Low` → `Very High`).
- **Workflow State Machine**: `To Do` → `Accepted` → `Authorized` → `In Progress` → `Done` (or `Cancelled`/`Stopped Abruptly`).
- **Strict Authorization**: Integrates deep validation rules to ensure only users with Administrative privileges can authorize accepted logistics tasks to prevent pipeline hijacking.
- **Inventory Injection**: Once a `Delivery` logictics task executes state `Done`, it automatically increments the target camp's native resource quantities directly.

### Resource Requests
- Inter-camp or personnel requests demanding critical supplies.
- **Automated Forwarding**: When an administrative user 'Approves' a resource request, it instantly proxies it into a structured logistics Delivery Task directed back at the source camp.

### Volunteer Management
- Assign personnel to groups and track personal availability.
- **State Inference**: System computes if a volunteer is `Available` or `On Duty` natively by scraping their concurrently assigned, in-progress logistics tasks.
- **Self-Enrollment**: Verified volunteers can organically add themselves into open operational logistics tasks seamlessly.

### Operational Role Assignments & Skill Matrix
- **Skill Compatibility**: Compare complex refugee capability intersections against physical camp workforce demands.
- **Dynamic Capacity Control**: Camp roles have designated utilization budgets. 
- **Algorithmic Selection**: One-click mass assignment algorithm iterates through hundreds of profiles, compares their registered skills against open roles, and automatically assigns logical, open operational positions.

### Direct Aid Distribution Log
- Decentralized logs providing accountability on the final mile metric (direct beneficiary allocations). Complete auditing on dates, assigned volunteer, and destination individual.

## Installation

### Prerequisites
- Odoo (v19.0 recommended)
- Python 3.x with the `qrcode` package installed (`pip install qrcode`)
- PostgreSQL

### Steps
1. Clone the repository into your Odoo Workshop directory:
```bash
git clone https://github.com/Vaibhav-Vinil/Refugee-Tracking-Module-For-Odoo-ERP.git
```
2. Update the app list internally within Odoo admin interfaces.
3. Install the module natively titled **Onwards** (`refugee_crisis_erp`).

## Technical Architecture Overview
Developed explicitly for Odoo 19 utilizing native web inheritances, complex computational triggers, robust record rules (`security/ir.model.access.csv` & `<record id="rule_camp_visibility">`), and a sprawling multi-file framework handling massive demo data seeding via built-in utility scripts (`seed_data_v2.py`). Included are dedicated JS UI augmentations mimicking geographic representations.
