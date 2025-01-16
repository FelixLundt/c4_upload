import secrets
import string

def generate_password(length=12):
    """Generate a secure random password"""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def generate_group():
    group_id = input("Enter group ID (e.g., team1): ").strip()
    group_name = input("Enter group name [optional]: ").strip()
    if not group_name:
        group_name = group_id.title()
    
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