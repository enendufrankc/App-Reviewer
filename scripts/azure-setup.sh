#!/bin/bash

# Azure Container Apps setup script
RESOURCE_GROUP="rg-app-reviewer"
LOCATION="East US"
CONTAINER_APP_NAME="app-reviewer"
CONTAINER_REGISTRY_NAME="crapprevieweracr"
CONTAINER_APP_ENV="env-app-reviewer"

echo "Creating Azure resources..."

# Create resource group
az group create --name $RESOURCE_GROUP --location "$LOCATION"

# Create Azure Container Registry
az acr create \
  --resource-group $RESOURCE_GROUP \
  --name $CONTAINER_REGISTRY_NAME \
  --sku Basic \
  --admin-enabled true

# Create Container Apps environment
az containerapp env create \
  --name $CONTAINER_APP_ENV \
  --resource-group $RESOURCE_GROUP \
  --location "$LOCATION"

# Create PostgreSQL database
az postgres flexible-server create \
  --resource-group $RESOURCE_GROUP \
  --name "postgres-app-reviewer" \
  --location "$LOCATION" \
  --admin-user "appadmin" \
  --admin-password "YourSecurePassword123!" \
  --sku-name "Standard_B1ms" \
  --version "13"

# Create the database
az postgres flexible-server db create \
  --resource-group $RESOURCE_GROUP \
  --server-name "postgres-app-reviewer" \
  --database-name "app_reviewer"

# Create Container App
az containerapp create \
  --name $CONTAINER_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --environment $CONTAINER_APP_ENV \
  --image "mcr.microsoft.com/azuredocs/containerapps-helloworld:latest" \
  --target-port 8000 \
  --ingress 'external' \
  --min-replicas 1 \
  --max-replicas 3

echo "Azure resources created successfully!"
