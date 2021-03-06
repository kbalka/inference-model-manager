# Management API

Management API component provides a convenience layer for controlling CRD records and handling AI models in MinIO storage.
With that users and platform admin can control all aspects of Inference Endpoints functionality without direct access
to Kubernetes API. 

Authorization of the models management functions is implemented based on user token permissions in kubernetes namespace 
associated with the MinIo bucket.
 
All the kubernetes operations are executed by Management API component using the user token so the authorization 
is configured in Kubernetes using appropriate user roles and role bindings. 

The roles and permissions are created automatically by Management API during tenant creation. 


## Docker image building

```
make docker_build
```
While the docker image is built it should be pushed to a docker registry accessible by the K8S cluster.

## Deployment in Kubernetes cluster

Refer to the [helm chart](../helm-deployment/management-api-subchart) documentation. 


## API documentation

### Tenants
Tenants are managed by Platform Admin. It is possible to take actions as follow:
* create tenant,
* delete tenant,
* list tenants.

#### Create tenant
Create tenant will create Kubernetes namespace and Minio bucket with given `name`. In `quota` you 
can provide dictionary that contains
[Kuberentes resource quota values](https://kubernetes.io/docs/concepts/policy/resource-quotas/).  
Currently supported values are `requests.cpu`, `limits.cpu`, `requests.memory` and `limits.memory`.  
You can also specify `maxEndpoints` value that will represent how many endpoints users can create 
within a tenant.     
You can specify only these values that you need.    
Note that when creating endpoint, user needs 
to provide the same set of values (excluding `maxEndpoints`) - he will be informed about what exactly 
he needs to add.  
`cert` is a CA certificate used to verify certificates presented by clients connecting to endpoint instances.   
Example command:
```
curl -X POST "https://<management_api_address>:443/tenants" -H "accept: application/json" \
-H "Authorization: <jwt_token>" -H "Content-Type: application/json" \
-d "{\"cert\": <cert_encoded_with_base64>, \"scope\": <string>, \"name\": <string>, \"quota\": <dict>}"
```

#### Delete tenant
Delete tenant will delete Kubernetes namespace and Minio bucket with given `name`. 
It will also delete models and endpoints within a tenant.  
Example command:
```
curl -X DELETE "https://<management_api_address>:443/tenants" -H "accept: application/json" \
-H "Authorization: <jwt_token>" -H "Content-Type: application/json" -d "{\"name\": <string>}"
```

#### List tenants
List tenants will list tenant names created by Platform Admin.
Example command:  
```
curl -X GET "https://<management_api_address>:443/tenants" -H "accept: application/json" \
-H "Authorization: <jwt_token>" -H "Content-Type: application/json"
```

### Endpoints
Endpoints are managed by Platform Users. It is possible to take actions as follow:
* create endpoint
* view endpoint
* update endpoint
* scale endpoint
* delete endpoint
* list endpoints

#### Create endpoint
Create endpoint will create deployment with Tensorflow Serving instance. It will be exposed by 
`endpointName.<domain>.com:9000`. `modelName` is a name of a model uploaded to a Minio bucket.
Add `modelVersion` to specify version of a model.   
`resources` is a dictionary with quota compliant to the one provided by Platform Admin within tenant. 
If there's no resource quota presented in tenant, `resources` here are optional.  
Example command:
```
curl -X POST "https://<management_api_address>:443/tenants/<namespace>/endpoints" -H "accept: 
application/json" \
-H "Authorization: <jwt_token>" -H "Content-Type: application/json" \
-d "{\"endpointName\": <string>, \"modelName\": <string>, \"modelVersion\": <int>, \"subjectName\": <string>
\"resources\": <dict>}"
```

#### View endpoint
View endpoint will show information about endpoint: endpoint status, model path, resources and replicas.  
Example command:
```
curl -X GET "https://<management_api_address>:443/tenants/<namespace>/endpoints/<endpoint-name>" \
-H "accept: application/json" -H "Authorization: <jwt_token>" -H "Content-Type: application/json"
```

#### Update endpoint
Update endpoint allows to change model that endpoint points to.  
Example command:
```
curl -X PATCH "https://<management_api_address>:443/tenants/<namespace>/endpoints/<endpoint-name>" \
-H "accept: application/json" -H "Authorization: <jwt_token>" -H "Content-Type: application/json" \
-d "{\"modelName\": <string>, \"modelVersion\": <int>}"
```
#### Scale endpoint
Scale endpoint allows to change the number of replicas of endpoint.  
Example command:
```
curl -X PATCH "https://<management_api_address>:443/tenants/<namespace>/endpoints/<endpoint-name>/replicas" \
-H "accept: application/json" -H "Authorization: <jwt_token>" -H "Content-Type: application/json" \
-d "{\"replicas\": <int>}"
```
#### Delete endpoint
Delete endpoint will delete endpoint with given name.  
Example command:
```
curl -X DELETE "https://<management_api_address>:443/tenants/<namespace>/endpoints" \
-H "accept: application/json" -H "Authorization: <jwt_token>" -H "Content-Type: application/json" \
-d "{\"endpointName\": <string>}"
``` 
#### List endpoints
List endpoints will list endpoints names created within given tenant.  
Example command:
```
curl -X GET "https://<management_api_address>:443/tenants/<namespace>/endpoints" -H "accept: application/json" \
-H "Authorization: <jwt_token>" -H "Content-Type: application/json"
```

### Models 
Models are pretrained deep learning models able to be server via Tensoflow Serving.

#### Upload model
To upload model use `scripts/model_upload_cli.py`.  
Run help to get information about usage:
```
python model_upload_cli.py -h
```

#### Listing the models
Listing the models will display the information about the stored models. 
Example command:

```
curl -X GET "https://<management_api_address>:443/tenants/<namespace>/models" -H "accept: application/json" \
-H "Authorization: <jwt_token>" -H "Content-Type: application/json" }"
```

#### Delete model
Delete model will delete model with given name and version.  
Example command:

```
curl -X DELETE "https://<management_api_address>:443/tenants/<namespace>/models" -H "accept: application/json" \
-H "Authorization: <jwt_token>" -H "Content-Type: application/json" \
-d "{\"modelName\": <string>, \"modelVersion\": <int>}"
```

## Script for API calls

You can refer to api_call.sh example CLI employing all API endpoints on [scripts](../scripts/)