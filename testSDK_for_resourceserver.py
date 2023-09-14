#Python script which creates the resource server dynamically.(It makes 4 API calls to cognito)
#1) it takes the user pool id, app client name, resource server and its scopes as arguments
#2) it takes the user pool id to connect to cognito and list the app client
#3) if the app client is not present, it creates the app client
#4) it creates the resource server and its scopes & if the resource server is already present, the code will handle the erorr/exception
#5) it attaches the new scopes to app client 
# Author: Abinash Patnaik
# Example: python testSDK_for_resourceserver.py us-east-1_9REgrgq7L USAA_user_pool_client test read write


import boto3
import sys
#session = boto3.Session(profile_name='default')

# total arguments
n = len(sys.argv)
print("Total arguments passed:", n)
 
# Fetching the arguments passed
print("\nName of Python script:", sys.argv[0])
print ("Passed parameters as below: ")
UserPoolId_passed = sys.argv[1]
ClientName_passed= sys.argv[2]
resource_servers_passed = sys.argv[3]
scopes_passed = []
for i in range(4, n):
    scopes_passed.append(sys.argv[i])
resource_servers_scope_passed = scopes_passed

print (UserPoolId_passed)
print(ClientName_passed)
print (resource_servers_passed)
print (resource_servers_scope_passed)
myClientName= ClientName_passed

# Replace with your AWS details: 
region = "us-east-1"

# Initialize the Cognito Identity Provider client
cognito_client = boto3.client("cognito-idp", region_name=region)

# Listing user pool client
data = cognito_client.list_user_pool_clients(UserPoolId=UserPoolId_passed,MaxResults=10)["UserPoolClients"]
client_names = [item['ClientName'] for item in data]
print (client_names)

# Capturing the client ID if the passed Client name is already present
for item in data:
    if item.get('ClientName') == ClientName_passed:
        # Print the 'ClientId' when 'ClientName' matches
        print(item['ClientId'])
        myClientId=(item['ClientId'])
        print (myClientId)


#Preparing scopes for cognito app client 
AllowedOAuthScopes_gen=[]
for j in resource_servers_scope_passed:
    AllowedOAuthScopes_gen.append(resource_servers_passed+'/'+j)

print (AllowedOAuthScopes_gen)

# Describe user pool client to fetch the attached scope if the passed Client name is already present
if myClientName in client_names:
    print ("*******************************************************")
    response = cognito_client.describe_user_pool_client(
    UserPoolId=UserPoolId_passed,
    ClientId=myClientId
    )

    hosted_ui_config = response.get('UserPoolClient', {}).get('AllowedOAuthScopes')
    if hosted_ui_config:
        print("Hosted UI Parameters for Client ID {} in User Pool {}:" .format(myClientId,UserPoolId_passed))
        print(hosted_ui_config)
        for items in hosted_ui_config:
            if items not in AllowedOAuthScopes_gen:
                AllowedOAuthScopes_gen.append(items)
    else:
        print("Hosted UI Parameters not found for Client ID {} in User Pool {}:" .format(myClientId,UserPoolId_passed))

print (AllowedOAuthScopes_gen)

print ("*******************************************************")

# Create a new resource server if the resource server is not present in cognito
print ("Creating resource server -> {} in Cognito".format(resource_servers_passed))
try:
    response = cognito_client.create_resource_server(
        UserPoolId=UserPoolId_passed,
        Identifier=resource_servers_passed,
        Name=resource_servers_passed,         
        Scopes= [ 
            { 
                "ScopeDescription": scope,
                "ScopeName": scope
            }
            for scope in resource_servers_scope_passed
        ]    
    )
    # Get the ID of the created resource server
    resource_server_id = response["ResourceServer"]["Identifier"]
    print("Resource server and scopes created successfully.")
except Exception:
    print("Resource server already present")



if myClientName in client_names:
    print("user pool client passed-{} is already present in Cognito user pool" .format(myClientName))
    flag = 'true'
    # Attach/update custom scopes in the app client
    print("Updating Cognito App Client with resource server scopes")
    response = cognito_client.update_user_pool_client(
    UserPoolId=UserPoolId_passed,
    ClientId=myClientId,
    ClientName=myClientName,
    SupportedIdentityProviders=['COGNITO'],
    CallbackURLs=['https://www.google.com'],
    AllowedOAuthFlows=['client_credentials'],
    AllowedOAuthFlowsUserPoolClient=True,
    AllowedOAuthScopes=AllowedOAuthScopes_gen,
    )
    print ("Cognito App Client updated with resource server scopes")

else:
    print("user pool client is not present in the Cognito user pool")
    response = cognito_client.create_user_pool_client(
    UserPoolId=UserPoolId_passed,
    ClientName=myClientName,
    GenerateSecret=True,
    RefreshTokenValidity=30,
    AccessTokenValidity=60,
    IdTokenValidity=60,
    TokenValidityUnits={'AccessToken': 'minutes', 'IdToken': 'minutes', 'RefreshToken': 'days'},
    ExplicitAuthFlows=['ALLOW_ADMIN_USER_PASSWORD_AUTH','ALLOW_CUSTOM_AUTH','ALLOW_USER_PASSWORD_AUTH','ALLOW_USER_SRP_AUTH','ALLOW_REFRESH_TOKEN_AUTH',],
    CallbackURLs=['https://www.google.com',],
    AllowedOAuthFlows=['client_credentials',],
    SupportedIdentityProviders=['COGNITO'],
    AllowedOAuthScopes=AllowedOAuthScopes_gen,
    AllowedOAuthFlowsUserPoolClient=True,
    PreventUserExistenceErrors='ENABLED',
    EnableTokenRevocation=True,
    EnablePropagateAdditionalUserContextData=True|False,
    AuthSessionValidity=3
    )
    print ("Cognito App Client creates with resource server scopes")













    


   










