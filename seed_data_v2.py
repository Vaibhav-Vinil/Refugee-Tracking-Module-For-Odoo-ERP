# -*- coding: utf-8 -*-
"""
RefugeeConnect - Comprehensive Seed Data Script
Run inside Odoo shell: exec(open('Workshop/refugee_crisis_erp/seed_data_v2.py').read())
"""
import random
from datetime import timedelta, date, datetime


def wipe_existing_data(env):
    """Delete all existing refugee module records to start fresh."""
    print("Wiping existing data...")
    models_to_clear = [
        'refugee.aid.distribution',
        'refugee.logistics.task',
        'refugee.profile',
        'refugee.family',
        'refugee.camp.role',
        'refugee.resource.inventory',
        'refugee.volunteer',
        'refugee.volunteer.group',
        'refugee.skill',
        'refugee.camp.management',
    ]
    for model in models_to_clear:
        try:
            records = env[model].search([])
            records.unlink()
            print(f"  Cleared {model}")
        except Exception as e:
            print(f"  Warning clearing {model}: {e}")
    env.cr.commit()
    print("Wipe complete.\n")


def generate_comprehensive_data(env):
    print("=" * 50)
    print("REFUGEECONNECT - COMPREHENSIVE DATA SEEDING")
    print("=" * 50)

    wipe_existing_data(env)

    Camp = env['refugee.camp.management']
    Skill = env['refugee.skill']
    Role = env['refugee.camp.role']
    Resource = env['refugee.resource.inventory']
    Family = env['refugee.family']
    Profile = env['refugee.profile']
    Aid = env['refugee.aid.distribution']
    Task = env['refugee.logistics.task']
    Volunteer = env['refugee.volunteer']
    VolGroup = env['refugee.volunteer.group']

    # ── 1. CAMPS ─────────────────────────────────────────────────────────────
    print("\n[1/8] Creating Camps...")
    camps_data = [
        {'name': 'Alpha North Station',    'total_capacity': 3000, 'location_label': 'Northern Border Zone'},
        {'name': 'Beta Transit Hub',       'total_capacity': 800,  'location_label': 'Eastern Corridor'},
        {'name': 'Gamma Medical Centre',   'total_capacity': 350,  'location_label': 'Central Valley'},
        {'name': 'Delta Family Camp',      'total_capacity': 1500, 'location_label': 'Southern Plains'},
        {'name': 'Epsilon Relief Point',   'total_capacity': 600,  'location_label': 'Western Highlands'},
    ]
    camps = [Camp.create(d) for d in camps_data]
    print(f"  Created {len(camps)} camps.")

    # ── 2. SKILLS ─────────────────────────────────────────────────────────────
    print("\n[2/8] Creating Skills...")
    skill_data = [
        'Medical First Aid', 'Trauma Counselling', 'Arabic Translation',
        'French Interpretation', 'Swahili Interpretation', 'Carpentry & Construction',
        'Electrical Maintenance', 'Plumbing & Sanitation', 'Teaching & Childcare',
        'Logistics & Driving', 'IT & Communications', 'Food Preparation',
        'Legal Aid Awareness', 'Security & Protection',
    ]
    skills = [Skill.create({'name': s}) for s in skill_data]
    print(f"  Created {len(skills)} skills.")

    # ── 3. VOLUNTEER GROUPS & VOLUNTEERS ──────────────────────────────────────
    print("\n[3/8] Creating Volunteer Groups & Volunteers...")
    groups_data = [
        {'name': 'Medical Response Team Alpha',  'description': 'First-line medical support volunteers.'},
        {'name': 'Logistics & Transport Beta',   'description': 'Coordinates supply delivery and transport.'},
        {'name': 'Child & Family Support Gamma', 'description': 'Focused on minors and family reunification.'},
        {'name': 'Infrastructure Delta',         'description': 'Construction, sanitation, and maintenance.'},
        {'name': 'Legal & Admin Epsilon',        'description': 'Documentation, legal advice, registration.'},
    ]
    vol_groups = [VolGroup.create(d) for d in groups_data]

    volunteer_roster = [
        ('Dr. Sarah Mensah',    '+44 7700 900001', 'sarah.mensah@ngo.org',    0),
        ('Ibrahim Al-Rashid',   '+49 151 0000001', 'ibrahim.r@aid.org',       1),
        ('Amara Diallo',        '+33 6 00000001',  'amara.d@relief.org',      2),
        ('Priya Nair',          '+91 98000 00001', 'priya.n@helpnow.org',     3),
        ('Carlos Romero',       '+34 600 000001',  'carlos.r@volunteer.org',  4),
        ('Fatima Ouedraogo',    '+226 70 000001',  'fatima.o@care.org',       2),
        ('James Osei',          '+233 24 000001',  'james.o@ngo.org',         1),
        ('Elena Petrov',        '+7 900 000 0001', 'elena.p@aid.org',         0),
        ('Yusuf Hassan',        '+252 61 000001',  'yusuf.h@relief.org',      3),
        ('Maria Santos',        '+55 11 00000001', 'maria.s@helpnow.org',     4),
        ('Kwame Asante',        '+233 20 000001',  'kwame.a@ngo.org',         1),
        ('Nadia Ben Ammar',     '+216 20 000001',  'nadia.b@aid.org',         0),
        ('Ravi Shankar',        '+91 99000 00001', 'ravi.s@volunteer.org',    3),
        ('Lucie Fontaine',      '+33 6 00000002',  'lucie.f@care.org',        4),
        ('Ahmed Khalil',        '+20 100 0000001', 'ahmed.k@relief.org',      2),
    ]
    volunteers = []
    for name, phone, email, grp_idx in volunteer_roster:
        volunteers.append(Volunteer.create({
            'name': name,
            'phone': phone,
            'email': email,
            'group_id': vol_groups[grp_idx].id,
        }))
    print(f"  Created {len(volunteers)} volunteers in {len(vol_groups)} groups.")

    # ── 4. CAMP ROLES ─────────────────────────────────────────────────────────
    print("\n[4/8] Creating Camp Roles...")
    role_definitions = [
        ('Head Nurse',              [0,1],  4),
        ('Field Medic',             [0],    6),
        ('Arabic Translator',       [2],    5),
        ('French Interpreter',      [3],    3),
        ('Logistics Coordinator',   [9],    4),
        ('Supply Driver',           [9],    8),
        ('Primary School Teacher',  [8],    4),
        ('Childcare Worker',        [8],    6),
        ('Carpenter',               [5],    5),
        ('Electrician',             [6],    3),
        ('Plumber',                 [7],    4),
        ('Food Service Lead',       [11],   6),
        ('IT Support Technician',   [10],   3),
        ('Security Officer',        [13],   8),
        ('Legal Advisor',           [12],   2),
    ]
    roles = []
    for i, (role_name, skill_idxs, capacity) in enumerate(role_definitions):
        camp = camps[i % len(camps)]
        role = Role.create({
            'name': role_name,
            'camp_id': camp.id,
            'capacity': capacity,
            'required_skill_ids': [(6, 0, [skills[idx].id for idx in skill_idxs])]
        })
        roles.append(role)
    print(f"  Created {len(roles)} camp roles.")

    # ── 5. RESOURCES ─────────────────────────────────────────────────────────
    print("\n[5/8] Creating Resources...")
    resource_catalog = {
        'food': [
            ('Rice (50kg Sacks)', 320, 1000),
            ('High-Energy Biscuits', 150, 800),
            ('Cooking Oil (5L)',  80,  500),
            ('Canned Corn & Beans', 95, 600),
            ('Infant Formula',   18,  200),   # deliberately low → triggers task
        ],
        'medical': [
            ('Basic First Aid Kits', 75, 400),
            ('Oral Rehydration Salts', 200, 600),
            ('Antibiotics (Amoxicillin)', 15, 300),  # low
            ('Surgical Dressings', 110, 500),
            ('Malaria Test Kits', 12, 250),           # low
        ],
        'water': [
            ('Bottled Water (1.5L)', 500, 2000),
            ('Water Purification Tablets', 40, 400),  # low 10%
            ('Jerry Cans (10L)', 60, 200),
        ],
        'other': [
            ('Emergency Blankets', 230, 800),
            ('Family Tents (4-person)', 25, 120),
            ('Solar Lanterns', 10, 100),              # low 10%
            ('Hygiene Kits', 80, 500),
            ('Children School Kits', 35, 300),
        ],
    }
    resources = []
    for camp in camps:
        for r_type, items in resource_catalog.items():
            for item_name, qty_avail, qty_req in items:
                res = Resource.create({
                    'name': f"{item_name} – {camp.name[:10]}",
                    'resource_type': r_type,
                    'quantity_available': qty_avail,
                    'quantity_required': qty_req,
                    'camp_id': camp.id,
                    'expiry_date': str(date.today() + timedelta(days=random.randint(30, 365))),
                })
                resources.append(res)
    print(f"  Created {len(resources)} resource entries.")
    print("  * Low-stock resources will auto-trigger logistics tasks via write().")

    # Force low-stock trigger: update some qty_available to below 20%
    # This happens via the write() override in resource_inventory.py
    print("  Triggering low-stock automation on selected resources...")
    low_stock_items = ['Antibiotics (Amoxicillin)', 'Water Purification Tablets', 'Solar Lanterns',
                       'Malaria Test Kits', 'Infant Formula']
    for res in resources:
        base_name = res.name.split(' – ')[0]
        if base_name in low_stock_items:
            # Write triggers the auto-task creation
            res.write({'quantity_available': round(res.quantity_required * 0.08, 1)})

    # ── 6. FAMILIES & REFUGEE PROFILES ────────────────────────────────────────
    print("\n[6/8] Creating Families & Refugee Profiles...")

    country_ids = env['res.country'].search([])
    lang_ids = env['res.lang'].search([('active', '=', True)])

    # Map nationality to language for realism
    nationality_language_pairs = [
        ('Syria',           'Arabic / العربية'),
        ('Afghanistan',     'Dari / دری'),
        ('South Sudan',     'English'),
        ('Myanmar',         'Burmese / ဗမာစာ'),
        ('Somalia',         'Somali'),
        ('Venezuela',       'Spanish / Español'),
        ('Ethiopia',        'Amharic / አማርኛ'),
        ('Democratic Republic of the Congo', 'French / Français'),
        ('Sudan',           'Arabic / العربية'),
        ('Eritrea',         'Tigrinya'),
    ]

    # Get real country records for the ones we want
    def get_country(name):
        return env['res.country'].search([('name', 'like', name)], limit=1)

    def get_lang(code_or_name):
        lang = env['res.lang'].search([('name', 'like', code_or_name)], limit=1)
        if not lang:
            lang = env['res.lang'].search([('active', '=', True)], limit=1)
        return lang

    families_data = [
        # (family_name, camp_idx, status, member_count)
        ('Al-Rashidi',   0, 'complete',  4),
        ('Mensah',       1, 'complete',  3),
        ('Diallo',       2, 'partial',   5),
        ('Kovačević',    3, 'separated', 2),
        ('Osei',         4, 'complete',  6),
        ('Hassan',       0, 'partial',   3),
        ('Nkosi',        1, 'complete',  4),
        ('Petrov',       2, 'complete',  2),
        ('Ouedraogo',    3, 'location_unknown', 1),
        ('Santos',       4, 'complete',  5),
        ('Khalil',       0, 'complete',  3),
        ('Asante',       1, 'partial',   4),
        ('Ben Ammar',    2, 'complete',  2),
        ('Shankar',      3, 'complete',  3),
        ('Fontaine',     4, 'separated', 2),
        ('Mwangi',       0, 'complete',  4),
        ('Saleh',        1, 'complete',  5),
        ('Yilmaz',       2, 'partial',   3),
        ('Abubakar',     3, 'complete',  6),
        ('Nguyen',       4, 'complete',  3),
    ]

    first_names_m = ['Ahmed', 'Mohamed', 'Yusuf', 'Ibrahim', 'Kwame', 'James', 'Carlos',
                     'Tariq', 'Omar', 'Ravi', 'Samuel', 'David', 'Ali', 'Hassan', 'Kofi']
    first_names_f = ['Fatima', 'Amara', 'Nadia', 'Priya', 'Maria', 'Aisha', 'Leila',
                     'Nour', 'Sarah', 'Elena', 'Grace', 'Miriam', 'Hana', 'Zara', 'Lucy']

    medical_conditions_pool = [
        'Hypertension, managed with medication',
        'Diabetes Type 2, requires insulin',
        'PTSD, receiving counselling',
        'Malnutrition, on supplementary feeding',
        'Tuberculosis, undergoing treatment',
        'Asthma, has inhaler',
        'Fracture (left leg), recovering',
        'Severe anaemia, iron supplements',
        'No known conditions',
        'Chronic back pain',
        'Hepatitis B, monitored',
    ]

    all_profiles = []
    profile_idx = 0

    for fam_name, camp_idx, status, member_count in families_data:
        camp = camps[camp_idx]
        nat_lang = nationality_language_pairs[profile_idx % len(nationality_language_pairs)]
        country = get_country(nat_lang[0])
        lang = get_lang(nat_lang[1].split('/')[0].strip())

        family = Family.create({
            'name': f"{fam_name} Family",
            'camp_id': camp.id,
            'status': status,
        })

        for j in range(member_count):
            gender = 'male' if j % 2 == 0 else 'female'
            first_name = random.choice(first_names_m if gender == 'male' else first_names_f)
            age_days = random.randint(3650, 22000) if j > 0 else random.randint(10950, 22000)  # head is adult
            is_head = (j == 0)
            vuln = random.choices(
                ['low', 'medium', 'high', 'critical'],
                weights=[30, 40, 20, 10]
            )[0]
            health = random.choices(
                ['stable', 'needs_followup', 'critical', 'unknown'],
                weights=[50, 30, 10, 10]
            )[0]
            requires_urgent = health == 'critical'
            prof_skills = random.sample(skills, k=random.randint(1, 3)) if age_days > 6000 else []

            prof = Profile.create({
                'name': f"{first_name} {fam_name}",
                'family_name': fam_name,
                'family_id': family.id,
                'is_head_of_family': is_head,
                'gender': gender,
                'date_of_birth': str(date.today() - timedelta(days=age_days)),
                'nationality_id': country.id if country else False,
                'languages_spoken_ids': [(6, 0, [lang.id])] if lang else [],
                'vulnerability_level': vuln,
                'health_status': health,
                'medical_conditions': random.choice(medical_conditions_pool),
                'requires_urgent_care': requires_urgent,
                'journey_stage': random.choice(['draft', 'vetting', 'medical', 'assigned', 'integrated']),
                'registration_status': random.choice(['registered', 'assigned', 'relocated']),
                'camp_id': camp.id,
                'skill_ids': [(6, 0, [s.id for s in prof_skills])],
                'deceased': False,
            })
            all_profiles.append(prof)

        profile_idx += 1

    print(f"  Created {len(families_data)} families with {len(all_profiles)} refugee profiles.")
    print("  * Family status is auto-computed from profile camp distribution.")

    # Auto-assign roles based on skills
    print("  Running skill-based role auto-assignment...")
    try:
        Profile.search([]).action_auto_assign_roles()
    except Exception as e:
        print(f"  Note: auto-assign partial ({e})")

    # ── 7. AID DISTRIBUTION ───────────────────────────────────────────────────
    print("\n[7/8] Creating Aid Distribution records...")
    # Delivering aid to the first ~60% of profiles
    delivered_count = 0
    pending_count = 0
    for i, prof in enumerate(all_profiles):
        # Give multiple aid items per person for variety
        num_aid_items = random.randint(1, 3)
        for _ in range(num_aid_items):
            # Pick resource from same camp
            camp_resources = [r for r in resources if r.camp_id.id == prof.camp_id.id]
            if not camp_resources:
                camp_resources = resources
            chosen_resource = random.choice(camp_resources)
            status = 'delivered' if i < int(len(all_profiles) * 0.65) else 'pending'
            qty = round(random.uniform(1.0, 5.0), 1)

            Aid.create({
                'refugee_id': prof.id,
                'resource_id': chosen_resource.id,
                'distributed_by_id': random.choice(volunteers).id,
                'quantity': qty,
                'status': status,
                'date': datetime.now() - timedelta(days=random.randint(0, 30)),
            })
            # NOTE: 'delivered' status triggers inventory deduction via write() in aid_distribution.py
            if status == 'delivered':
                delivered_count += 1
            else:
                pending_count += 1

    print(f"  Created {delivered_count + pending_count} aid records "
          f"({delivered_count} delivered -> auto-deducted inventory, {pending_count} pending).")
    print("  * Inventory deductions may trigger additional low-stock logistics tasks.")

    # ── 8. MANUAL LOGISTICS TASKS (non-auto-triggered ones) ───────────────────
    print("\n[8/8] Creating manual Logistics Tasks...")
    task_templates = [
        ('Medical supply convoy to Alpha North',   'delivery',   '3', 0, 4),
        ('Tent installation – Delta Family Camp',  'setup',      '2', 3, 3),
        ('Food distribution run – Gamma Centre',   'delivery',   '2', 2, 2),
        ('Generator maintenance – Beta Hub',       'setup',      '1', 1, 1),
        ('Blanket transport – Epsilon Relief',     'transport',  '2', 4, 4),
        ('Water jerrycan pickup – Alpha North',    'transport',  '3', 0, 3),
        ('School kit delivery – Delta Camp',       'delivery',   '1', 3, 1),
        ('Solar lantern installation – Gamma',     'setup',      '1', 2, 2),
        ('Family reunification transport run',     'transport',  '3', 1, 4),
        ('Medical waste disposal – Alpha North',   'transport',  '2', 0, 0),
    ]

    status_options = ['todo', 'in_progress', 'done']
    manual_tasks = []
    for task_name, t_type, priority, camp_idx, volunteer_offset in task_templates:
        camp_res = [r for r in resources if r.camp_id.id == camps[camp_idx].id]
        chosen_res = random.choice(camp_res) if camp_res else random.choice(resources)
        num_vols = random.randint(1, 3)
        assigned_vols = volunteers[volunteer_offset:volunteer_offset + num_vols]

        t = Task.create({
            'name': task_name,
            'task_type': t_type,
            'priority': priority,
            'status': random.choice(status_options),
            'resource_id': chosen_res.id,
            'source_location': camps[(camp_idx + 1) % len(camps)].name,
            'destination': camps[camp_idx].name,
            'volunteer_ids': [(6, 0, [v.id for v in assigned_vols])],
        })
        manual_tasks.append(t)

    # Count auto-created tasks from low stock
    auto_tasks = Task.search([('name', 'like', 'Emergency Resupply')])
    print(f"  Created {len(manual_tasks)} manual logistics tasks.")
    print(f"  * {len(auto_tasks)} emergency resupply tasks were AUTO-CREATED by low-stock triggers.")

    env.cr.commit()
    print("\n" + "=" * 50)
    print("SEEDING COMPLETE!")
    print("=" * 50)
    print(f"  Camps:                {len(camps)}")
    print(f"  Skills:               {len(skills)}")
    print(f"  Volunteer Groups:     {len(vol_groups)}")
    print(f"  Volunteers:           {len(volunteers)}")
    print(f"  Camp Roles:           {len(roles)}")
    print(f"  Resources:            {len(resources)}")
    print(f"  Families:             {len(families_data)}")
    print(f"  Refugee Profiles:     {len(all_profiles)}")
    print(f"  Aid Distribution:     {delivered_count + pending_count}")
    print(f"  Manual Tasks:         {len(manual_tasks)}")
    print(f"  Auto-Triggered Tasks: {len(auto_tasks)} (emergency resupply)")
    print("=" * 50)


if __name__ == '__main__':
    if 'env' in locals() or 'env' in globals():
        generate_comprehensive_data(env)
    else:
        print("Run inside Odoo shell: exec(open('Workshop/refugee_crisis_erp/seed_data_v2.py').read())")
