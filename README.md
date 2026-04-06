# Onwards – Refugee Crisis Management ERP

An **enterprise-grade humanitarian management system** built on Odoo ERP, designed to coordinate refugee data, camp operations, logistics, and aid distribution during crisis situations.

This module provides a **centralized, scalable, and real-time platform** for NGOs, governments, and relief organizations to efficiently manage large-scale humanitarian efforts.

## Overview

During humanitarian crises, managing refugee populations, resources, and logistics becomes extremely complex.

**Onwards** addresses this challenge by integrating:

- Refugee data management  
- Camp coordination  
- Resource tracking  
- Workforce allocation  
- Logistics planning  

into a **single unified ERP system**.

## Features

### Refugee Profiles & Family Management

- Store personal details (name, age, gender, nationality, ID)  
- Maintain family relationships (dependents, guardians)  
- Track vulnerabilities (children, elderly, disabled)  
- Record health conditions and medical flags  
- Manage registration lifecycle (unregistered → verified → settled)

### Camp Management System

- Manage multiple camps and sub-sectors  
- Define capacity limits  
- Track real-time occupancy  
- Automatically flag overcrowded areas  
- Organize locations hierarchically (region → camp → sector)

### Humanitarian Skills & Role Assignment

- Maintain skill registry (languages, medical, technical skills)  
- Assign refugees to operational roles  
- Match skills with required camp responsibilities  
- Improve workforce utilization inside camps

### Resource Inventory Control

- Track essential supplies:  
  - Food  
  - Water  
  - Medical supplies  
  - Shelter materials  

- Monitor stock levels per camp  
- Generate low-stock alerts  
- Track resource consumption

### Aid Distribution Tracking & Audit Logs

- Record:  
  - Beneficiary (individual/family)  
  - Aid type  
  - Quantity  
  - Date & time  

- Maintain full audit logs  
- Ensure transparency and accountability

### Logistics & Task Management

- Create and assign tasks:  
  - Deliveries  
  - Transport  
  - Camp setup  
  - Emergency response  

- Track task lifecycle:  
  - Pending → In Progress → Completed  

- Assign tasks to field workers

### Camp Map Visualization

- Visual map interface for camps  
- Display occupancy levels  
- Highlight overcrowded or critical zones

## Installation

### Prerequisites

- Odoo (v19 recommended)  
- Python 3.x  
- PostgreSQL  

### Steps

1. Clone the repository:

```bash
git clone https://github.com/Vaibhav-Vinil/Refugee-Tracking-Module-For-Odoo-ERP.git

## Technical Details
Compatible with **Odoo 19** (uses `user_ids` on `res.groups` internally). Relies natively on `base`, `mail`, `portal`, and `web`. Includes its own custom UI elements like a Camp Map visualization.
