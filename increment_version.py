import toml

def increment_version(version):
    major, minor, patch = map(int, version.split('.'))
    patch += 1
    return f"{major}.{minor}.{patch}"

# Load pyproject.toml
with open('pyproject.toml', 'r') as file:
    pyproject = toml.load(file)

# Increment the version
current_version = pyproject['tool']['poetry']['version']
new_version = increment_version(current_version)
pyproject['tool']['poetry']['version'] = new_version

# Save the updated pyproject.toml
with open('pyproject.toml', 'w') as file:
    toml.dump(pyproject, file)

print(f"Version updated from {current_version} to {new_version}")
