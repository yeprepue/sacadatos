import sys
import traceback

print("=" * 60)
print("Prueba de importaciones")
print("=" * 60)

# Test 1: GitHubClientPort
print("\n1. Importando GitHubClientPort...")
try:
    from src.domain.ports.github_client import GitHubClientPort
    print("   ✓ GitHubClientPort importado correctamente")
except Exception as e:
    print(f"   ✗ Error: {e}")
    traceback.print_exc()

# Test 2: GitHubAdapter
print("\n2. Importando GitHubAdapter...")
try:
    from src.infrastructure.adapters.github_adapter import GitHubAdapter, GitHubAPIError
    print("   ✓ GitHubAdapter y GitHubAPIError importados correctamente")
except Exception as e:
    print(f"   ✗ Error: {e}")
    traceback.print_exc()

# Test 3: DatabaseAdapter
print("\n3. Importando DatabaseAdapter...")
try:
    from src.infrastructure.adapters.database_adapter import DatabaseAdapter
    print("   ✓ DatabaseAdapter importado correctamente")
except Exception as e:
    print(f"   ✗ Error: {e}")
    traceback.print_exc()

# Test 4: DriveAdapter
print("\n4. Importando DriveAdapter...")
try:
    from src.infrastructure.adapters.drive_adapter import DriveAdapter
    print("   ✓ DriveAdapter importado correctamente")
except Exception as e:
    print(f"   ✗ Error: {e}")
    traceback.print_exc()

# Test 5: Adaptadores desde __init__
print("\n5. Importando desde adapters __init__...")
try:
    from src.infrastructure.adapters import GitHubAdapter, DatabaseAdapter, DriveAdapter
    print("   ✓ Todos los adaptadores importados desde __init__")
except Exception as e:
    print(f"   ✗ Error: {e}")
    traceback.print_exc()

print("\n" + "=" * 60)
print("Prueba completada")
print("=" * 60)
