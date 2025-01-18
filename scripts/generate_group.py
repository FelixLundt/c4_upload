import secrets
import string
import re
def generate_password(length=12):
    """Generate a secure random password"""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def generate_group():
    group_name = '/'
    while True:
        group_name = input("Enter group name (e.g., team1): ").strip()
        # Validate group name
        if not re.match(r'^[A-Za-z0-9-]+$', group_name):
            print("Group name can only contain letters, numbers, and hyphens")
            continue
        break
    
    password = generate_password()
    
    print("\nGroup Registration Info:")
    print("------------------------")
    print(f"Group ID: {group_id}")
    print(f"Group Name: {group_name}")
    print(f"Password: {password}")
    print("\nEnvironment Variable:")
    print(f"{group_id}_PASSWORD={password}")
    print("\nConfig Entry:")
    print(f"""    '{group_id}': {{
        'name': '{group_name}',
        'password': os.environ.get('{group_id}_PASSWORD')
    }},""")

if __name__ == '__main__':
    generate_group() 