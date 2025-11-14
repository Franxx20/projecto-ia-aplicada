# Script para configurar variables de entorno del backend en Azure
# Este script evita problemas con caracteres especiales en PowerShell

Write-Host "🔧 Configurando variables de entorno del Backend..." -ForegroundColor Cyan

# Leer valores almacenados
$DB_PASSWORD = (Get-Content "db_password_demo.txt").Split(": ")[1]
$STORAGE_CONN = az storage account show-connection-string --name plantitasdemostorage --resource-group rg-plantitas-demo-academica --output tsv
$JWT_SECRET = -join ((65..90) + (97..122) + (48..57) | Get-Random -Count 64 | ForEach-Object {[char]$_})

Write-Host "✅ Valores obtenidos/generados" -ForegroundColor Green
Write-Host "   - DB Password: $($DB_PASSWORD.Substring(0,5))..." -ForegroundColor Gray
Write-Host "   - JWT Secret: $($JWT_SECRET.Substring(0,10))..." -ForegroundColor Gray
Write-Host "   - Storage Conn: Obtenido" -ForegroundColor Gray

# Construir DATABASE_URL (sin SSL en el string, se manejará en la app)
$DATABASE_URL = "mysql+pymysql://plantitasadmin:$DB_PASSWORD@plantitas-mysql-server.mysql.database.azure.com:3306/plantitas_db"

Write-Host ""
Write-Host "📝 Configurando App Settings..." -ForegroundColor Cyan

# Configurar cada variable individualmente para evitar problemas de parsing
Write-Host "   → DATABASE_URL..." -ForegroundColor Gray
az webapp config appsettings set --name plantitas-demo-backend --resource-group rg-plantitas-demo-academica --settings "DATABASE_URL=$DATABASE_URL" --output none

Write-Host "   → JWT_SECRET_KEY..." -ForegroundColor Gray
az webapp config appsettings set --name plantitas-demo-backend --resource-group rg-plantitas-demo-academica --settings "JWT_SECRET_KEY=$JWT_SECRET" --output none

Write-Host "   → JWT_ALGORITHM..." -ForegroundColor Gray
az webapp config appsettings set --name plantitas-demo-backend --resource-group rg-plantitas-demo-academica --settings "JWT_ALGORITHM=HS256" --output none

Write-Host "   → ACCESS_TOKEN_EXPIRE_MINUTES..." -ForegroundColor Gray
az webapp config appsettings set --name plantitas-demo-backend --resource-group rg-plantitas-demo-academica --settings "ACCESS_TOKEN_EXPIRE_MINUTES=30" --output none

Write-Host "   → REFRESH_TOKEN_EXPIRE_DAYS..." -ForegroundColor Gray
az webapp config appsettings set --name plantitas-demo-backend --resource-group rg-plantitas-demo-academica --settings "REFRESH_TOKEN_EXPIRE_DAYS=7" --output none

Write-Host "   → AZURE_STORAGE_CONNECTION_STRING..." -ForegroundColor Gray
az webapp config appsettings set --name plantitas-demo-backend --resource-group rg-plantitas-demo-academica --settings "AZURE_STORAGE_CONNECTION_STRING=$STORAGE_CONN" --output none

Write-Host "   → AZURE_STORAGE_CONTAINER_NAME..." -ForegroundColor Gray
az webapp config appsettings set --name plantitas-demo-backend --resource-group rg-plantitas-demo-academica --settings "AZURE_STORAGE_CONTAINER_NAME=plantitas-imagenes" --output none

Write-Host "   → AZURE_STORAGE_USE_EMULATOR..." -ForegroundColor Gray
az webapp config appsettings set --name plantitas-demo-backend --resource-group rg-plantitas-demo-academica --settings "AZURE_STORAGE_USE_EMULATOR=false" --output none

Write-Host "   → ENVIRONMENT..." -ForegroundColor Gray
az webapp config appsettings set --name plantitas-demo-backend --resource-group rg-plantitas-demo-academica --settings "ENVIRONMENT=production" --output none

Write-Host "   → DEBUG..." -ForegroundColor Gray
az webapp config appsettings set --name plantitas-demo-backend --resource-group rg-plantitas-demo-academica --settings "DEBUG=false" --output none

Write-Host "   → CORS_ORIGINS..." -ForegroundColor Gray
az webapp config appsettings set --name plantitas-demo-backend --resource-group rg-plantitas-demo-academica --settings "CORS_ORIGINS=https://plantitas-frontend-app.azurewebsites.net" --output none

Write-Host ""
Write-Host "✅ Variables de entorno configuradas exitosamente" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Verificando configuración..." -ForegroundColor Cyan
az webapp config appsettings list --name plantitas-demo-backend --resource-group rg-plantitas-demo-academica --query "[?name=='DATABASE_URL' || name=='JWT_SECRET_KEY' || name=='AZURE_STORAGE_CONNECTION_STRING'].{Name:name, Value:value}" --output table

Write-Host ""
Write-Host "🎉 Configuración completa. El backend reiniciará automáticamente." -ForegroundColor Green
