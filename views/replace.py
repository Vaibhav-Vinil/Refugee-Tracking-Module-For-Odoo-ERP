import os

def replace_in_file(path, old, new):
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    content = content.replace(old, new)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

# For refugee_profile_views.xml
path = r'c:\Users\Vaibhav\Desktop\Odoo_Software\server\Workshop\refugee_crisis_erp\views\refugee_profile_views.xml'
replace_in_file(path, 'group_refugee_medical,refugee_crisis_erp.group_refugee_field_worker', 'group_refugee_volunteer')
replace_in_file(path, 'group_refugee_medical', 'group_refugee_volunteer')
replace_in_file(path, 'group_refugee_field_worker', 'group_refugee_volunteer')

# For volunteer_views.xml
path2 = r'c:\Users\Vaibhav\Desktop\Odoo_Software\server\Workshop\refugee_crisis_erp\views\volunteer_views.xml'
replace_in_file(path2, 'group_refugee_field_worker', 'group_refugee_volunteer')

print("Replaced successfully.")
