# Onwards 

An extensive, fully-featured custom Odoo module designed to facilitate and streamline the management of refugee camps, crises, and humanitarian efforts. 

## Features
- **Refugee Profiles & Families**: Comprehensive tracking of refugee demographics, familial ties, vulnerabilities, health conditions, and registration status.
- **Camp Management**: Map out and organize different refugee camps, monitor specific location capacities, and automatically flag overcrowded sectors.
- **Humanitarian Skills & Roles**: Catalog refugee skills and seamlessly assign them to required camp roles (e.g., translators, medical workers, logistics organizers).
- **Resource Inventory Control**: Track distribution of essential resources (food, water, medical supplies) in each sub-camp with automated low-stock warnings.
- **Aid Distribution history**: Audit logs on which refugees or families received what aid and when.
- **Logistics Task Tracking**: Manage delivery, transport, and setup tasks across border regions and camps.

## Installation
1. Clone this repository into your Odoo `addons` directory (or custom module directory like `/Workshop`).
2. Restart the Odoo instance.
3. Access the Apps menu in Odoo, remove the "Apps" filter, and search for `refugee_crisis_erp`.
4. Click **Install** or **Upgrade**.

## Access Rights
Four main customizable user groups exist:
1. **Onwards Manager**: Full global access.
2. **Medical Coordinator**: Specifically handles `critical` health states and urgency requests.
3. **Field Worker**: Limited read/edit scope scoped to day-to-day operations.
4. **Portal/Public**: Basic views for external reporting.

## Technical Details
Compatible with **Odoo 19** (uses `user_ids` on `res.groups` internally). Relies natively on `base`, `mail`, `portal`, and `web`. Includes its own custom UI elements like a Camp Map visualization.
