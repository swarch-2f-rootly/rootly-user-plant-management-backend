#!/bin/bash

# Script para probar la API del servicio user-plant-management-backend
BASE_URL="http://localhost:8003"

echo "🧪 Testing User Plant Management Backend API"
echo "=============================================="

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para hacer requests y mostrar resultados
test_endpoint() {
    local method=$1
    local endpoint=$2
    local data=$3
    local description=$4
    
    echo -e "\n${BLUE}Testing: $description${NC}"
    echo "Request: $method $endpoint"
    
    if [ -n "$data" ]; then
        response=$(curl -s -w "\n%{http_code}" -X $method "$BASE_URL$endpoint" \
            -H "Content-Type: application/json" \
            -d "$data")
    else
        response=$(curl -s -w "\n%{http_code}" -X $method "$BASE_URL$endpoint")
    fi
    
    # Separar respuesta y código HTTP
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n -1)
    
    if [ "$http_code" -ge 200 ] && [ "$http_code" -lt 300 ]; then
        echo -e "${GREEN}✅ SUCCESS ($http_code)${NC}"
        echo "Response: $body"
    else
        echo -e "${RED}❌ ERROR ($http_code)${NC}"
        echo "Response: $body"
    fi
}

# Verificar que el servicio esté corriendo
echo -e "\n${BLUE}Checking if service is running...${NC}"
health_response=$(curl -s -w "%{http_code}" -o /dev/null "$BASE_URL/health")
if [ "$health_response" = "200" ]; then
    echo -e "${GREEN}✅ Service is running!${NC}"
else
    echo -e "${RED}❌ Service is not running. Please start it first.${NC}"
    exit 1
fi

# Generar UUIDs para las pruebas
USER_ID="123e4567-e89b-12d3-a456-426614174000"
USER_ID_2="987fcdeb-51a2-43d1-b456-426614174111"
PLANT_ID=""
DEVICE_ID=""

echo -e "\n${BLUE}🚀 Starting API Tests${NC}"

# 1. Health Check
test_endpoint "GET" "/health" "" "Health Check"

# 2. Crear una planta
plant_data='{
    "user_id": "'$USER_ID'",
    "name": "Tomate Cherry",
    "species": "Solanum lycopersicum",
    "description": "Planta de tomate en invernadero"
}'
test_endpoint "POST" "/api/v1/plants/" "$plant_data" "Create Plant"

# 3. Crear un dispositivo
device_data='{
    "user_id": "'$USER_ID'",
    "name": "ESP32 Sensor",
    "description": "Microcontrolador para monitoreo",
    "version": "1.0",
    "category": "microcontroller"
}'
test_endpoint "POST" "/api/v1/devices/" "$device_data" "Create Device"

# 4. Obtener plantas del usuario
test_endpoint "GET" "/api/v1/plants/users/$USER_ID" "" "Get User Plants"

# 5. Obtener dispositivos del usuario
test_endpoint "GET" "/api/v1/devices/users/$USER_ID" "" "Get User Devices"

# 6. Crear dispositivo para otro usuario
device_data_2='{
    "user_id": "'$USER_ID_2'",
    "name": "Arduino Uno",
    "description": "Microcontrolador básico",
    "category": "microcontroller"
}'
test_endpoint "POST" "/api/v1/devices/" "$device_data_2" "Create Device for User 2"

# 7. Verificar aislamiento - User 1 no debe ver dispositivos de User 2
test_endpoint "GET" "/api/v1/devices/users/$USER_ID_2" "" "Get User 2 Devices (should be isolated)"

# 8. Obtener todos los dispositivos (admin endpoint)
test_endpoint "GET" "/api/v1/devices/" "" "Get All Devices (Admin)"

# 9. Obtener todas las plantas (admin endpoint)
test_endpoint "GET" "/api/v1/plants/" "" "Get All Plants (Admin)"

echo -e "\n${BLUE}🎉 API Tests Completed!${NC}"
echo -e "\n${BLUE}📚 API Documentation available at: $BASE_URL/docs${NC}"
echo -e "\n${BLUE}🔧 You can also test manually with:${NC}"
echo "curl -X GET '$BASE_URL/api/v1/devices/users/$USER_ID'"
echo "curl -X GET '$BASE_URL/api/v1/plants/users/$USER_ID'"
