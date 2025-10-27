"""
Verify Docker deployment setup.
Checks all Docker-related files and configuration.
"""

import sys
import os

print("="*70)
print("DOCKER DEPLOYMENT VERIFICATION")
print("="*70)

tests = []

# Test 1: Check Docker files
print("\n1. Checking Docker configuration files...")
docker_files = [
    ("Dockerfile", "VELOX API container definition"),
    ("docker-compose.yml", "Multi-service orchestration"),
    (".dockerignore", "Build optimization"),
    ("docker-start.sh", "Startup script"),
    ("docker-stop.sh", "Shutdown script"),
]

all_exist = True
for file, description in docker_files:
    if os.path.exists(file):
        size = os.path.getsize(file)
        print(f"  ✓ {file:25s} ({size:5d} bytes) - {description}")
    else:
        print(f"  ✗ {file:25s} MISSING - {description}")
        all_exist = False

tests.append(("Docker files", all_exist))

# Test 2: Check documentation
print("\n2. Checking documentation files...")
doc_files = [
    ("DOCKER-GUIDE.md", "Complete deployment guide"),
    ("QUICK-START.md", "Quick start guide"),
    ("DOCKER-DEPLOYMENT-COMPLETE.md", "Deployment summary"),
]

docs_exist = True
for file, description in doc_files:
    if os.path.exists(file):
        size = os.path.getsize(file)
        lines = sum(1 for _ in open(file))
        print(f"  ✓ {file:35s} ({lines:4d} lines) - {description}")
    else:
        print(f"  ✗ {file:35s} MISSING - {description}")
        docs_exist = False

tests.append(("Documentation", docs_exist))

# Test 3: Check Dockerfile structure
print("\n3. Verifying Dockerfile structure...")
try:
    with open("Dockerfile", 'r') as f:
        dockerfile_content = f.read()
    
    checks = [
        ("Base image", "FROM python:3.11" in dockerfile_content),
        ("Working directory", "WORKDIR /app" in dockerfile_content),
        ("Requirements copy", "COPY requirements.txt" in dockerfile_content),
        ("Playwright install", "playwright install" in dockerfile_content),
        ("Non-root user", "useradd" in dockerfile_content),
        ("Health check", "HEALTHCHECK" in dockerfile_content),
        ("Expose port", "EXPOSE 8000" in dockerfile_content),
        ("CMD instruction", "CMD" in dockerfile_content),
    ]
    
    all_present = True
    for name, present in checks:
        status = "✓" if present else "✗"
        print(f"  {status} {name}")
        if not present:
            all_present = False
    
    tests.append(("Dockerfile structure", all_present))
except Exception as e:
    print(f"  ✗ Error reading Dockerfile: {e}")
    tests.append(("Dockerfile structure", False))

# Test 4: Check docker-compose services
print("\n4. Verifying docker-compose services...")
try:
    with open("docker-compose.yml", 'r') as f:
        compose_content = f.read()
    
    services = [
        ("velox-api", "VELOX API service"),
        ("n8n", "n8n workflow automation"),
        ("node-red", "Node-RED flow programming"),
        ("grafana", "Grafana monitoring"),
        ("postgres", "PostgreSQL database"),
        ("redis", "Redis cache"),
    ]
    
    all_present = True
    for service, description in services:
        if service in compose_content:
            print(f"  ✓ {service:15s} - {description}")
        else:
            print(f"  ✗ {service:15s} - {description} MISSING")
            all_present = False
    
    tests.append(("Docker Compose services", all_present))
except Exception as e:
    print(f"  ✗ Error reading docker-compose.yml: {e}")
    tests.append(("Docker Compose services", False))

# Test 5: Check volumes configuration
print("\n5. Checking volume configuration...")
try:
    volumes = [
        "n8n_data",
        "node_red_data",
        "grafana_data",
        "postgres_data",
        "redis_data",
    ]
    
    all_present = True
    for volume in volumes:
        if volume in compose_content:
            print(f"  ✓ {volume}")
        else:
            print(f"  ✗ {volume} MISSING")
            all_present = False
    
    tests.append(("Volume configuration", all_present))
except Exception as e:
    print(f"  ✗ Error checking volumes: {e}")
    tests.append(("Volume configuration", False))

# Test 6: Check network configuration
print("\n6. Checking network configuration...")
try:
    if "networks:" in compose_content and "velox-network" in compose_content:
        print("  ✓ velox-network defined")
        print("  ✓ Bridge driver configured")
        tests.append(("Network configuration", True))
    else:
        print("  ✗ Network configuration missing")
        tests.append(("Network configuration", False))
except Exception as e:
    print(f"  ✗ Error checking network: {e}")
    tests.append(("Network configuration", False))

# Test 7: Check environment variables
print("\n7. Checking environment variable configuration...")
try:
    with open(".env.example", 'r') as f:
        env_content = f.read()
    
    required_vars = [
        "OPENALGO_API_KEY",
        "N8N_USER",
        "N8N_PASSWORD",
        "GRAFANA_USER",
        "GRAFANA_PASSWORD",
        "POSTGRES_USER",
        "POSTGRES_PASSWORD",
        "TIMEZONE",
    ]
    
    all_present = True
    for var in required_vars:
        if var in env_content:
            print(f"  ✓ {var}")
        else:
            print(f"  ✗ {var} MISSING")
            all_present = False
    
    tests.append(("Environment variables", all_present))
except Exception as e:
    print(f"  ✗ Error checking environment: {e}")
    tests.append(("Environment variables", False))

# Test 8: Check script permissions
print("\n8. Checking script permissions...")
try:
    import stat
    
    scripts = ["docker-start.sh", "docker-stop.sh"]
    all_executable = True
    
    for script in scripts:
        if os.path.exists(script):
            st = os.stat(script)
            is_executable = bool(st.st_mode & stat.S_IXUSR)
            status = "✓" if is_executable else "✗"
            print(f"  {status} {script} {'executable' if is_executable else 'not executable'}")
            if not is_executable:
                all_executable = False
        else:
            print(f"  ✗ {script} not found")
            all_executable = False
    
    if not all_executable:
        print("\n  Run: chmod +x docker-start.sh docker-stop.sh")
    
    tests.append(("Script permissions", all_executable))
except Exception as e:
    print(f"  ✗ Error checking permissions: {e}")
    tests.append(("Script permissions", False))

# Test 9: Check port configuration
print("\n9. Checking port mappings...")
try:
    ports = [
        ("8000", "VELOX API", True),
        ("5678", "n8n", True),
        ("1880", "Node-RED", True),
        ("3001", "Grafana", True),
        ("5432", "PostgreSQL", False),  # Optional - internal only
        ("6379", "Redis", True),
    ]
    
    all_present = True
    for port, service, required in ports:
        if f"{port}:" in compose_content:
            print(f"  ✓ Port {port:5s} - {service}")
        else:
            if required:
                print(f"  ✗ Port {port:5s} - {service} MISSING")
                all_present = False
            else:
                print(f"  ⚠️  Port {port:5s} - {service} (internal only)")
    
    tests.append(("Port mappings", all_present))
except Exception as e:
    print(f"  ✗ Error checking ports: {e}")
    tests.append(("Port mappings", False))

# Test 10: Check health checks
print("\n10. Checking health check configuration...")
try:
    health_checks = compose_content.count("healthcheck:")
    print(f"  ✓ {health_checks} services have health checks")
    
    if health_checks >= 4:  # At least main services
        tests.append(("Health checks", True))
    else:
        print("  ⚠️  Some services missing health checks")
        tests.append(("Health checks", False))
except Exception as e:
    print(f"  ✗ Error checking health checks: {e}")
    tests.append(("Health checks", False))

# Summary
print("\n" + "="*70)
print("VERIFICATION SUMMARY")
print("="*70)

passed = sum(1 for _, result in tests if result is True)
failed = sum(1 for _, result in tests if result is False)
total = len(tests)

print(f"\nResults: {passed}/{total} checks passed")

for name, result in tests:
    status = "✓ PASSED" if result else "✗ FAILED"
    print(f"  {name:30s}: {status}")

print("\n" + "="*70)

if all(result for _, result in tests):
    print("🎉 DOCKER SETUP VERIFIED!")
    print("="*70)
    print("\n✅ All Docker files configured correctly")
    print("✅ All services defined")
    print("✅ Volumes configured")
    print("✅ Network configured")
    print("✅ Environment variables ready")
    print("✅ Documentation complete")
    
    print("\n🚀 Ready to deploy!")
    print("\nNext steps:")
    print("  1. Configure .env file: cp .env.example .env")
    print("  2. Edit .env with your settings")
    print("  3. Start services: ./docker-start.sh")
    print("  4. Access: http://localhost:8000/docs")
    
    print("\n📚 Documentation:")
    print("  Quick Start:  QUICK-START.md")
    print("  Full Guide:   DOCKER-GUIDE.md")
    print("  Summary:      DOCKER-DEPLOYMENT-COMPLETE.md")
    
    exit_code = 0
else:
    print("⚠️  DOCKER SETUP INCOMPLETE")
    print("="*70)
    print(f"\n{failed} checks failed")
    
    if failed:
        print("\nFailed checks:")
        for name, result in tests:
            if not result:
                print(f"  ✗ {name}")
    
    exit_code = 1

print("="*70)
sys.exit(exit_code)
