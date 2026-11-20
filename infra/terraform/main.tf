terraform {
  required_version = ">= 1.5.0"
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
}

resource "azurerm_mssql_server" "server" {
  name                         = "sql-sg-community-536e"
  resource_group_name          = data.azurerm_resource_group.existing.name
  location                     = data.azurerm_resource_group.existing.location
  version                      = "12.0"
  administrator_login          = "sgcommunityadmin"
  administrator_login_password = var.sql_admin_password
  minimum_tls_version          = "1.2"
}

resource "azapi_resource" "database" {
  type      = "Microsoft.Sql/servers/databases@2023-08-01"
  parent_id = azurerm_mssql_server.server.id
  name      = "sg_community"
  location  = data.azurerm_resource_group.existing.location
  body = {
    sku = { name = "GP_S_Gen5_2", tier = "GeneralPurpose" }
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
variable "sql_admin_password" {
  type      = string
  sensitive = true
}

output "static_web_app_hostname" { value = azurerm_static_web_app.frontend.default_host_name }
output "registry_login_server" { value = azurerm_container_registry.registry.login_server }
output "sql_server_fqdn" { value = azurerm_mssql_server.server.fully_qualified_domain_name }
