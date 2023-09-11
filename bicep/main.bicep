resource storageAccount 'Microsoft.Storage/storageAccounts@2021-02-01' = {
  name: 'texttrek'
  location: resourceGroup().location
  kind: 'StorageV2'
  sku: {
    name: 'Standard_LRS'
  }
  properties: {

  }
}

module setStatic './setStorageStaticWebsite.ps1.bicep' = {
  name: 'setStatic'
  params: {
    storageAccountName: storageAccount.name
    staticWebsiteState: 'Enabled'
  }
}
