# -*- coding: utf-8 -*-
import sys
import random
from datetime import timedelta, date, datetime
from odoo import api, SUPERUSER_ID

def generate_comprehensive_data(env):
    print("Initializing comprehensive data generation...")
    Camp = env['refugee.camp.management']
    Skill = env['refugee.skill']
    Role = env['refugee.camp.role']
    Resource = env['refugee.resource.inventory']
    Family = env['refugee.family']
    Profile = env['refugee.profile']
    Aid = env['refugee.aid.distribution']
    Task = env['refugee.logistics.task']

    # 1. Provide variation in Camps
    camps_data = [
        {'name': 'Camp North - Point Alpha', 'total_capacity': 2000, 'location_label': 'Northern Sector'},
        {'name': 'Camp East - Transit', 'total_capacity': 500, 'location_label': 'Eastern Border'},
        {'name': 'Regional Medical Hub', 'total_capacity': 200, 'location_label': 'Central Valley'},
    ]
    camps = []
    print("Creating Camps...")
    for cd in camps_data:
        c = Camp.search([('name', '=', cd['name'])], limit=1)
        if not c:
            c = Camp.create(cd)
        camps.append(c)

    # 2. Skills
    skill_names = ['Medical First Aid', 'Translation & Interp', 'Plumbing', 'Carpentry', 'Teaching & Childcare', 'Logistics & Driving']
    skills = []
    print("Creating Skills...")
    for s in skill_names:
        sk = Skill.search([('name', '=', s)], limit=1)
        if not sk:
            sk = Skill.create({'name': s})
        skills.append(sk)

    # 3. Resources (distributed among camps)
    resource_types = ['food', 'medical', 'water', 'other']
    items = ['Rice Sacks', 'Blankets', 'First Aid Kits', 'Bottled Water', 'Tents', 'Antibiotics']
    resources = []
    print("Creating Resources...")
    for camp in camps:
        for _ in range(4):
            res = Resource.create({
                'name': f"{random.choice(items)} Batch {random.randint(100, 999)}",
                'resource_type': random.choice(resource_types),
                'quantity_available': random.uniform(50, 1000),
                'camp_id': camp.id,
            })
            resources.append(res)

    # 4. Roles
    print("Creating Camp Roles...")
    roles = []
    for camp in camps:
        for _ in range(3):
            sk = random.sample(skills, k=random.randint(1, 2))
            role = Role.create({
                'name': f"{sk[0].name} Lead",
                'camp_id': camp.id,
                'capacity': random.randint(1, 5),
                'required_skill_ids': [(6, 0, [x.id for x in sk])]
            })
            roles.append(role)

    # 5. Families and Profiles
    print("Creating Families and Refugees with varying states...")
    first_names = ['Alina', 'Tariq', 'Mona', 'Karim', 'Sami', 'Leila', 'Youssef', 'Nour', 'Omar', 'Reem']
    last_names = ['Zaid', 'Mahmoud', 'Fouad', 'Rahman', 'Saleh', 'Haddad', 'Nassar']
    
    profiles = []
    for i in range(15):
        fam_name = random.choice(last_names)
        camp = random.choice(camps)
        family = Family.create({
            'name': f"{fam_name} Family (Reg: {i})",
            'camp_id': camp.id,
            'status': random.choice(['complete', 'separated', 'partial'])
        })
        
        member_count = random.randint(1, 6)
        for j in range(member_count):
            age_days = random.randint(100, 25000)
            prof = Profile.create({
                'name': f"{random.choice(first_names)} {fam_name}",
                'family_name': fam_name,
                'family_id': family.id,
                'is_head_of_family': (j == 0), # first one is head
                'gender': random.choice(['male', 'female', 'other']),
                'vulnerability_level': random.choice(['low', 'medium', 'high', 'critical']),
                'health_status': random.choice(['unknown', 'stable', 'needs_followup', 'critical']),
                'journey_stage': random.choice(['draft', 'vetting', 'medical', 'assigned', 'integrated']),
                'registration_status': random.choice(['registered', 'assigned', 'relocated']),
                'date_of_birth': str(date.today() - timedelta(days=age_days)),
                'camp_id': camp.id,
                'skill_ids': [(6, 0, [sk.id for sk in random.sample(skills, k=random.randint(0, 2))])] if age_days > 5000 else [],
                'requires_urgent_care': True if random.random() < 0.1 else False,
            })
            profiles.append(prof)
            
            # 6. Aid Distribution lines for profiles
            if random.random() > 0.4:
                Aid.create({
                    'refugee_id': prof.id,
                    'resource_id': random.choice(resources).id,
                    'quantity': random.choice([1.0, 2.0, 3.0]),
                    'status': random.choice(['pending', 'delivered']),
                    'date': datetime.now() - timedelta(days=random.randint(1, 10))
                })

    # Auto assign roles where possible
    Profile.search([]).action_auto_assign_roles()

    # 7. Logistics Tasks
    print("Creating Logistics Tasks...")
    for _ in range(20):
        worker = random.choice(profiles)
        Task.create({
            'name': f"Run {random.choice(['Delivery', 'Setup Pickup', 'Transport Move'])} - Task {random.randint(1000, 9999)}",
            'task_type': random.choice(['delivery', 'transport', 'setup']),
            'assigned_to': worker.id if worker.age > 16 else False,
            'status': random.choice(['todo', 'in_progress', 'done']),
            'priority': random.choice(["0", "1", "2", "3"]),
            'resource_id': random.choice(resources).id,
            'source_location': random.choice(camps).name,
            'destination': random.choice(camps).name,
        })
        
    print("Done! Extensive varied data populated across 8 tables.")

if __name__ == '__main__':
    if 'env' in locals() or 'env' in globals():
        generate_comprehensive_data(env)
        env.cr.commit()
    else:
        print("Please run inside Odoo shell")
