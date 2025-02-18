param uniqueId string
param prefix string
param location string = resourceGroup().location
param userAssignedIdentityResourceId string
param logAnalyticsWorkspaceId string
param serviceBusName string

resource intacc 'Microsoft.Logic/integrationAccounts@2019-05-01' = {
  name: '${prefix}-intacc-${uniqueId}'
  location: location
  properties: {
    
  }
  sku: {
    name: 'Free'
  }
}

module office365Connection 'br/public:avm/res/web/connection:0.4.1' = {
  name: 'office365'
  params: {
    name: 'office365'
    api: {
      id: '/subscriptions/${subscription().subscriptionId}/providers/Microsoft.Web/locations/${location}/managedApis/office365'
    }
    displayName: 'office365'
  }
}

module sbConnection 'br/public:avm/res/web/connection:0.4.1' = {
  name: 'servicebus'
  params: {
    name: 'servicebus'
    api: {
      id: '/subscriptions/${subscription().subscriptionId}/providers/Microsoft.Web/locations/${location}/managedApis/servicebus'
    }
    displayName: 'servicebus'
    parameterValueSet: {
      name: 'managedIdentityAuth'
      values: {
        namespaceEndpoint: {
          value: 'sb://${serviceBusName}.servicebus.windows.net/'
        }
      }
    }
  }
}

module logicApp 'br/public:avm/res/logic/workflow:0.4.0' = {
  name: 'approval-logicapp'
  params: {
    name: '${prefix}-approval-${uniqueId}'
    location: location
    managedIdentities: { userAssignedResourceIds: [userAssignedIdentityResourceId] }
    integrationAccount: {
      id: intacc.id
    }
    diagnosticSettings: [
      {
        name: 'customSetting'
        metricCategories: [
          {
            category: 'AllMetrics'
          }
        ]
        workspaceResourceId: logAnalyticsWorkspaceId
      }
    ]
    workflowActions: loadJsonContent('./logicapp/approval.actions.json')
    workflowTriggers: loadJsonContent('./logicapp/approval.triggers.json')
    workflowParameters: loadJsonContent('./logicapp/approval.parameters.json')
    definitionParameters: {
      '$connections': {
        value: {
          servicebus: {
            id: '/subscriptions/${subscription().subscriptionId}/providers/Microsoft.Web/locations/${location}/managedApis/servicebus'
            connectionId: sbConnection.outputs.resourceId
            connectionName: 'servicebus'
            connectionProperties: {
                authentication: {
                    type: 'ManagedServiceIdentity'
                    identity: userAssignedIdentityResourceId
                }
            }
          }
          office365: {
            id: '/subscriptions/${subscription().subscriptionId}/providers/Microsoft.Web/locations/${location}/managedApis/office365'
            connectionId: office365Connection.outputs.resourceId
            connectionName: office365Connection.name
          }
        }
      }
    }
  }
}
