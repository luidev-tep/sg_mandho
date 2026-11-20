terraform {
  required_version = ">= 1.5.0"
  backend "azurerm" {
    resource_group_name  = "rg-community-mgmt"
    storage_account_name = "sgcommunitytfstate536e"
    container_name       = "tfstate"
    key                  = "sg-community.tfstate"
    use_azuread_auth     = true
  }
  required_providers {
    azurerm = { source = "hashicorp/azurerm", version = "~> 4.0" }
    azapi   = { source = "Azure/azapi", version = "~> 2.0" }
  }
}

provider "azurerm" {
  features {}
  subscription_id = var.subscription_id
}
provider "azapi" {}

data "azurerm_resource_group" "existing" {
  name = var.resource_group_name
}

resource "azurerm_static_web_app" "frontend" {
  name                = "swa-sg-community-536e"
  resource_group_name = data.azurerm_resource_group.existing.name
  location            = "centralus"
  sku_tier            = "Free"
  sku_size            = "Free"
}

resource "azurerm_container_registry" "registry" {
  name                = "sgcommunityacr536e"
  resource_group_name = data.azurerm_resource_group.existing.name
  location            = data.azurerm_resource_group.existing.location
  sku                 = "Basic"
  admin_enabled       = false
}

resource "azurerm_container_app_environment" "environment" {
  name                = "cae-sg-community"
  resource_group_name = data.azurerm_resource_group.existing.name
  location            = data.azurerm_resource_group.existing.location
  workload_profile {
    name                  = "Consumption"
    workload_profile_type = "Consumption"
  }
}

resource "azurerm_user_assigned_identity" "backend" {
  name                = "uai-sg-community-backend"
  resource_group_name = data.azurerm_resource_group.existing.name
  location            = data.azurerm_resource_group.existing.location
}

resource "azurerm_container_app" "backend" {
  name                         = "ca-sg-community-api"
  container_app_environment_id = azurerm_container_app_environment.environment.id
  resource_group_name          = data.azurerm_resource_group.existing.name
  revision_mode                = "Single"
  workload_profile_name        = "Consumption"
  identity {
    type         = "SystemAssigned, UserAssigned"
    identity_ids = [azurerm_user_assigned_identity.backend.id]
  }
  secret {
    name  = "flask-secret"
    value = var.app_secret_key
  }
  secret {
    name                = "recaptcha-secret"
    identity            = azurerm_user_assigned_identity.backend.id
    key_vault_secret_id = "https://kv-sg-community-536e.vault.azure.net/secrets/recaptcha-secret"
  }
  registry {
    server   = azurerm_container_registry.registry.login_server
    identity = "system"
  }
  # Image revisions are deployed by GitHub Actions, not by Terraform.
  lifecycle {
    ignore_changes = [template[0].container[0].image]
  }
  ingress {
    external_enabled = true
    target_port      = 5000
    traffic_weight {
      latest_revision = true
      percentage      = 100
    }
  }
  template {
    min_replicas = var.backend_min_replicas
    max_replicas = 1
    container {
      name   = "api"
      image  = "${azurerm_container_registry.registry.login_server}/sg-community:entra-v1"
      cpu    = 0.25
      memory = "0.5Gi"
      env {
        name        = "SECRET_KEY"
        secret_name = "flask-secret"
      }
      env {
        name  = "DB_SERVER"
        value = "${azurerm_mssql_server.server.fully_qualified_domain_name},1433"
      }
      env {
        name  = "DB_NAME"
        value = azapi_resource.database.name
      }
      env {
        name  = "DB_AUTHENTICATION"
        value = "ManagedIdentity"
      }
      env {
        name  = "AZURE_CLIENT_ID"
        value = azurerm_user_assigned_identity.backend.client_id
      }
      env {
        name  = "URL_FRONTEND"
        value = "https://${azurerm_static_web_app.frontend.default_host_name}"
      }
      env {
        name  = "RECAPTCHA_ENABLED"
        value = "true"
      }
      env {
        name        = "RECAPTCHA_SECRET_KEY"
        secret_name = "recaptcha-secret"
      }
    }
  }
}

resource "azurerm_role_assignment" "backend_acr_pull" {
  scope                = azurerm_container_registry.registry.id
  role_definition_name = "AcrPull"
  principal_id         = azurerm_container_app.backend.identity[0].principal_id
}

resource "azurerm_mssql_server" "server" {
  name                         = "sql-sg-community-536e"
  resource_group_name          = data.azurerm_resource_group.existing.name
  location                     = data.azurerm_resource_group.existing.location
  version                      = "12.0"
  administrator_login          = "sgcommunityadmin"
  administrator_login_password = var.sql_admin_password
  minimum_tls_version          = "1.2"
  azuread_administrator {
    login_username              = var.sql_entra_admin_login
    object_id                   = var.sql_entra_admin_object_id
    tenant_id                   = var.tenant_id
    azuread_authentication_only = var.sql_entra_only
  }
}

resource "azurerm_mssql_firewall_rule" "azure_services" {
  count            = var.allow_azure_services ? 1 : 0
  name             = "AllowAllWindowsAzureIps"
  server_id        = azurerm_mssql_server.server.id
  start_ip_address = "0.0.0.0"
  end_ip_address   = "0.0.0.0"
}

# Temporary operator access for initial migration and Entra principal setup.
resource "azurerm_mssql_firewall_rule" "operator" {
  count            = var.operator_public_ip == "" ? 0 : 1
  name             = "temporary-operator"
  server_id        = azurerm_mssql_server.server.id
  start_ip_address = var.operator_public_ip
  end_ip_address   = var.operator_public_ip
}

resource "azurerm_mssql_firewall_rule" "operator_additional" {
  for_each         = var.operator_additional_ips
  name             = "temporary-operator-${replace(each.value, ".", "-")}"
  server_id        = azurerm_mssql_server.server.id
  start_ip_address = each.value
  end_ip_address   = each.value
}

resource "azapi_resource" "database" {
  type      = "Microsoft.Sql/servers/databases@2023-08-01"
  parent_id = azurerm_mssql_server.server.id
  name      = "sg_community"
  location  = data.azurerm_resource_group.existing.location
  body = {
    sku = { name = "GP_S_Gen5", tier = "GeneralPurpose", family = "Gen5", capacity = 2 }
    properties = {
      useFreeLimit                = true
      freeLimitExhaustionBehavior = "AutoPause"
      autoPauseDelay              = 60
      minCapacity                 = 0.5
      maxSizeBytes                = 34359738368
    }
  }
  lifecycle { prevent_destroy = true }
}

variable "subscription_id" { type = string }
variable "resource_group_name" { type = string }
variable "tenant_id" { type = string }
variable "app_secret_key" {
  type      = string
  sensitive = true
}
variable "backend_min_replicas" {
  type    = number
  default = 0
}
variable "sql_entra_admin_login" { type = string }
variable "sql_entra_admin_object_id" { type = string }
variable "sql_entra_only" {
  type    = bool
  default = true
}
variable "allow_azure_services" {
  type    = bool
  default = true
}
variable "operator_public_ip" {
  type    = string
  default = ""
}
variable "operator_additional_ips" {
  type    = set(string)
  default = []
}
variable "sql_admin_password" {
  type      = string
  sensitive = true
}

output "static_web_app_hostname" { value = azurerm_static_web_app.frontend.default_host_name }
output "registry_login_server" { value = azurerm_container_registry.registry.login_server }
output "sql_server_fqdn" { value = azurerm_mssql_server.server.fully_qualified_domain_name }
