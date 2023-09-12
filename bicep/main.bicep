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

resource blobServices 'Microsoft.Storage/storageAccounts/blobServices@2023-01-01' = {
  name: 'default'
  parent: storageAccount
  properties: {
    cors: {
      corsRules: [
        {
          allowedHeaders: ['*']
          allowedMethods: ['*']
          exposedHeaders: []
          maxAgeInSeconds: 0
          allowedOrigins: [
            'http://localhost:5173', 'https://texttrek.z16.web.core.windows.net'
          ]
        }
      ]
    }
  }
}
