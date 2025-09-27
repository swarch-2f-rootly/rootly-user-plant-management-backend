# Variables
PYTHON=python3
PYTEST=pytest

# Ejecutar todos los tests
test:
	$(PYTEST) -v

# Ejecutar con cobertura
coverage:
	$(PYTEST) --cov=app --cov-report=term-missing

# Verificación FR-D (ejecuta tests por requisito)
verify-frd:
	@echo "🔎 Verificando FR-D1 (relaciones usuario-dispositivo)..."
	@$(PYTEST) -q tests/test_permissions.py -k "permission_levels" || exit 1
	@echo "✅ FR-D1 OK"

	@echo "🔎 Verificando FR-D2 (editar y desasociar)..."
	@$(PYTEST) -q tests/test_devices_api.py -k "edit_device" || exit 1
	@$(PYTEST) -q tests/test_devices_api.py -k "unassociate_device" || exit 1
	@echo "✅ FR-D2 OK"

	@echo "🔎 Verificando FR-D3 (listado con filtros)..."
	@$(PYTEST) -q tests/test_devices_api.py -k "list_devices_filter" || exit 1
	@echo "✅ FR-D3 OK"

	@echo "🔎 Verificando FR-D4 (habilitar/deshabilitar captura)..."
	@$(PYTEST) -q tests/test_devices_api.py -k "enable_device" || exit 1
	@echo "✅ FR-D4 OK"

	@echo "🔎 Verificando FR-D5 (validaciones de integridad)..."
	@$(PYTEST) -q tests/test_devices_api.py -k "forbidden" || exit 1
	@echo "✅ FR-D5 OK"

	@echo "🎉 Todas las FR-D verificadas con éxito"
