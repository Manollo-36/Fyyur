#!/usr/bin/env python3
"""
Script to check latest versions of packages from requirements.txt
"""
import subprocess
import sys
import re

def get_package_from_line(line):
    """Extract package name from requirements line"""
    line = line.strip()
    if not line or line.startswith('#'):
        return None
    
    # Handle various requirement formats
    # package==1.0.0
    # package>=1.0.0
    # package~=1.0.0
    match = re.match(r'^([a-zA-Z0-9_-]+)', line)
    if match:
        return match.group(1)
    return None

def get_latest_version(package_name):
    """Get latest version of a package"""
    try:
        result = subprocess.run([
            sys.executable, '-m', 'pip', 'index', 'versions', package_name
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            # Parse output to get latest version
            lines = result.stdout.strip().split('\n')
            for line in lines:
                if 'LATEST:' in line:
                    return line.split('LATEST:')[1].strip()
                elif f'{package_name} (' in line:
                    # Extract version from first line
                    match = re.search(rf'{package_name} \(([^)]+)\)', line)
                    if match:
                        return match.group(1)
        return "Unknown"
    except:
        return "Error"

def read_requirements():
    """Read and parse requirements.txt"""
    try:
        with open('requirements.txt', 'r') as f:
            return f.readlines()
    except FileNotFoundError:
        print("❌ requirements.txt not found!")
        return []

def main():
    print("🔍 Checking latest versions for all packages in requirements.txt...\n")
    
    requirements = read_requirements()
    if not requirements:
        return
    
    print(f"{'Package':<25} {'Current':<15} {'Latest':<15} {'Status'}")
    print("-" * 70)
    
    updates_available = []
    
    for line in requirements:
        package_name = get_package_from_line(line)
        if not package_name:
            continue
            
        # Extract current version
        current_match = re.search(r'==([^,\s]+)', line.strip())
        current_version = current_match.group(1) if current_match else "Unknown"
        
        # Get latest version
        latest_version = get_latest_version(package_name)
        
        # Determine status
        if latest_version == "Unknown" or latest_version == "Error":
            status = "❓"
        elif current_version == latest_version:
            status = "✅"
        else:
            status = "🔄"
            updates_available.append(f"{package_name}=={latest_version}")
        
        print(f"{package_name:<25} {current_version:<15} {latest_version:<15} {status}")
    
    if updates_available:
        print(f"\n📋 Packages with updates available: {len(updates_available)}")
        print("\n🚀 To update all packages to latest versions:")
        print("pip install --upgrade " + " ".join(updates_available))
        
        print("\n📝 Updated requirements.txt content:")
        print("-" * 40)
        for req in updates_available:
            print(req)
    else:
        print("\n✅ All packages are up to date!")

if __name__ == "__main__":
    main()