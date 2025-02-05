"""
Helper script to set up configuration files
"""
import os
import shutil
from getpass import getpass

def setup_config():
    # Check if config_sensitive.py already exists
    if os.path.exists('config_sensitive.py'):
        overwrite = input("config_sensitive.py already exists. Overwrite? (yes/no): ")
        if overwrite.lower() != 'yes':
            print("Setup cancelled.")
            return

    # Copy template
    shutil.copy2('config_sensitive_template.py', 'config_sensitive.py')
    
    # Get proxy configuration
    use_proxy = input("Do you want to use proxies? (yes/no): ").lower() == 'yes'
    
    if use_proxy:
        proxy_url = input("Enter proxy URL (format: http://host:port): ")
        username = input("Proxy username: ")
        password = getpass("Proxy password: ")
        
        # Create proxy string
        proxy = f"http://{username}:{password}@{proxy_url.split('//')[1]}"
        
        # Update config file
        with open('config_sensitive.py', 'r') as f:
            content = f.read()
        
        content = content.replace(
            '"http://your-username:your-password@your-proxy-host:port"',
            f'"{proxy}"'
        )
        
        with open('config_sensitive.py', 'w') as f:
            f.write(content)
    
    print("\nConfiguration file created successfully!")
    print("Remember to add config_sensitive.py to .gitignore")

if __name__ == "__main__":
    setup_config() 