# Script para probar la API del servicio user-plant-management-backend
$BaseUrl = "http://localhost:8003"

Write-Host "🧪 Testing User Plant Management Backend API" -ForegroundColor Blue
Write-Host "==============================================" -ForegroundColor Blue

# Función para hacer requests y mostrar resultados
function Test-Endpoint {
    param(
        [string]$Method,
        [string]$Endpoint,
        [string]$Data = $null,
        [string]$Description
    )
    
    Write-Host "`n🔍 Testing: $Description" -ForegroundColor Cyan
    Write-Host "Request: $Method $Endpoint" -ForegroundColor Gray
    
    try {
        $headers = @{
            "Content-Type" = "application/json"
        }
        
        if ($Data) {
            $response = Invoke-RestMethod -Uri "$BaseUrl$Endpoint" -Method $Method -Body $Data -Headers $headers
        } else {
            $response = Invoke-RestMethod -Uri "$BaseUrl$Endpoint" -Method $Method -Headers $headers
        }
        
        Write-Host "✅ SUCCESS" -ForegroundColor Green
        $response | ConvertTo-Json -Depth 3 | Write-Host -ForegroundColor White
    }
    catch {
        Write-Host "❌ ERROR: $($_.Exception.Message)" -ForegroundColor Red
        if ($_.Exception.Response) {
            $statusCode = $_.Exception.Response.StatusCode.value__
            Write-Host "Status Code: $statusCode" -ForegroundColor Red
        }
    }
}

# Verificar que el servicio esté corriendo
Write-Host "`n🔍 Checking if service is running..." -ForegroundColor Cyan
try {
    $healthResponse = Invoke-RestMethod -Uri "$BaseUrl/health" -Method GET
    Write-Host "✅ Service is running!" -ForegroundColor Green
} catch {
    Write-Host "❌ Service is not running. Please start it first." -ForegroundColor Red
    exit 1
}

# Generar UUIDs para las pruebas
$UserId = "123e4567-e89b-12d3-a456-426614174000"
$UserId2 = "987fcdeb-51a2-43d1-b456-426614174111"

Write-Host "`n🚀 Starting API Tests" -ForegroundColor Blue

# 1. Health Check
Test-Endpoint -Method "GET" -Endpoint "/health" -Description "Health Check"

# 2. Crear una planta
$plantData = @{
    user_id = $UserId
    name = "Tomate Cherry"
    species = "Solanum lycopersicum"
    description = "Planta de tomate en invernadero"
} | ConvertTo-Json

Test-Endpoint -Method "POST" -Endpoint "/api/v1/plants/" -Data $plantData -Description "Create Plant"

# 3. Crear un dispositivo
$deviceData = @{
    user_id = $UserId
    name = "ESP32 Sensor"
    description = "Microcontrolador para monitoreo"
    version = "1.0"
    category = "microcontroller"
} | ConvertTo-Json

Test-Endpoint -Method "POST" -Endpoint "/api/v1/devices/" -Data $deviceData -Description "Create Device"

# 4. Obtener plantas del usuario
Test-Endpoint -Method "GET" -Endpoint "/api/v1/plants/users/$UserId" -Description "Get User Plants"

# 5. Obtener dispositivos del usuario
Test-Endpoint -Method "GET" -Endpoint "/api/v1/devices/users/$UserId" -Description "Get User Devices"

# 6. Crear dispositivo para otro usuario
$deviceData2 = @{
    user_id = $UserId2
    name = "Arduino Uno"
    description = "Microcontrolador básico"
    category = "microcontroller"
} | ConvertTo-Json

Test-Endpoint -Method "POST" -Endpoint "/api/v1/devices/" -Data $deviceData2 -Description "Create Device for User 2"

# 7. Verificar aislamiento - User 1 no debe ver dispositivos de User 2
Test-Endpoint -Method "GET" -Endpoint "/api/v1/devices/users/$UserId2" -Description "Get User 2 Devices (should be isolated)"

# 8. Obtener todos los dispositivos (admin endpoint)
Test-Endpoint -Method "GET" -Endpoint "/api/v1/devices/" -Description "Get All Devices (Admin)"

# 9. Obtener todas las plantas (admin endpoint)
Test-Endpoint -Method "GET" -Endpoint "/api/v1/plants/" -Description "Get All Plants (Admin)"

Write-Host "`n🎉 API Tests Completed!" -ForegroundColor Green
Write-Host "`n📚 API Documentation available at: $BaseUrl/docs" -ForegroundColor Blue
Write-Host "`n🔧 You can also test manually with:" -ForegroundColor Blue
Write-Host "Invoke-RestMethod -Uri '$BaseUrl/api/v1/devices/users/$UserId' -Method GET" -ForegroundColor Gray
Write-Host "Invoke-RestMethod -Uri '$BaseUrl/api/v1/plants/users/$UserId' -Method GET" -ForegroundColor Gray
