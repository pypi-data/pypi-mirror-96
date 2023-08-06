# agilicus_api.CertificatesApi

All URIs are relative to *https://api.agilicus.com*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_csr**](CertificatesApi.md#get_csr) | **GET** /v1/certificate_signing_requests/{csr_id} | Get a CertSigningReq
[**list_csr**](CertificatesApi.md#list_csr) | **GET** /v1/certificate_signing_requests | list certificate signing requests
[**replace_csr_cert**](CertificatesApi.md#replace_csr_cert) | **PUT** /v1/certificate_signing_requests/{csr_id}/certificate_status | Update a CertSigningReqCertificateStatus


# **get_csr**
> CertSigningReq get_csr(csr_id, org_id=org_id)

Get a CertSigningReq

Get a CertSigningReq

### Example

* Bearer (JWT) Authentication (token-valid):
```python
from __future__ import print_function
import time
import agilicus_api
from agilicus_api.rest import ApiException
from pprint import pprint
configuration = agilicus_api.Configuration()
# Configure Bearer authorization (JWT): token-valid
configuration.access_token = 'YOUR_BEARER_TOKEN'

# Defining host is optional and default to https://api.agilicus.com
configuration.host = "https://api.agilicus.com"
# Enter a context with an instance of the API client
with agilicus_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = agilicus_api.CertificatesApi(api_client)
    csr_id = '1234' # str | A certificate signing request id
org_id = '1234' # str | Organisation Unique identifier (optional)

    try:
        # Get a CertSigningReq
        api_response = api_instance.get_csr(csr_id, org_id=org_id)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling CertificatesApi->get_csr: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **csr_id** | **str**| A certificate signing request id | 
 **org_id** | **str**| Organisation Unique identifier | [optional] 

### Return type

[**CertSigningReq**](CertSigningReq.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | CertSigningReq found and returned |  -  |
**404** | CertSigningReq does not exist |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_csr**
> ListCertSigningReqResponse list_csr(limit=limit, org_id=org_id, ready=ready, reason=reason)

list certificate signing requests

List certificate signing requests. 

### Example

* Bearer (JWT) Authentication (token-valid):
```python
from __future__ import print_function
import time
import agilicus_api
from agilicus_api.rest import ApiException
from pprint import pprint
configuration = agilicus_api.Configuration()
# Configure Bearer authorization (JWT): token-valid
configuration.access_token = 'YOUR_BEARER_TOKEN'

# Defining host is optional and default to https://api.agilicus.com
configuration.host = "https://api.agilicus.com"
# Enter a context with an instance of the API client
with agilicus_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = agilicus_api.CertificatesApi(api_client)
    limit = 500 # int | limit the number of rows in the response (optional) (default to 500)
org_id = '1234' # str | Organisation Unique identifier (optional)
ready = true # bool | Query a CSR based on its ready status (optional)
reason = agilicus_api.CSRReasonEnum() # CSRReasonEnum | Query a CSR based on its reason status (optional)

    try:
        # list certificate signing requests
        api_response = api_instance.list_csr(limit=limit, org_id=org_id, ready=ready, reason=reason)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling CertificatesApi->list_csr: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **limit** | **int**| limit the number of rows in the response | [optional] [default to 500]
 **org_id** | **str**| Organisation Unique identifier | [optional] 
 **ready** | **bool**| Query a CSR based on its ready status | [optional] 
 **reason** | [**CSRReasonEnum**](.md)| Query a CSR based on its reason status | [optional] 

### Return type

[**ListCertSigningReqResponse**](ListCertSigningReqResponse.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Return a list of CertSigningReq |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **replace_csr_cert**
> CertSigningReqCertificateStatus replace_csr_cert(csr_id, cert_signing_req_certificate_status=cert_signing_req_certificate_status)

Update a CertSigningReqCertificateStatus

Update a CertSigningReqCertificateStatus

### Example

* Bearer (JWT) Authentication (token-valid):
```python
from __future__ import print_function
import time
import agilicus_api
from agilicus_api.rest import ApiException
from pprint import pprint
configuration = agilicus_api.Configuration()
# Configure Bearer authorization (JWT): token-valid
configuration.access_token = 'YOUR_BEARER_TOKEN'

# Defining host is optional and default to https://api.agilicus.com
configuration.host = "https://api.agilicus.com"
# Enter a context with an instance of the API client
with agilicus_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = agilicus_api.CertificatesApi(api_client)
    csr_id = '1234' # str | A certificate signing request id
cert_signing_req_certificate_status = agilicus_api.CertSigningReqCertificateStatus() # CertSigningReqCertificateStatus |  (optional)

    try:
        # Update a CertSigningReqCertificateStatus
        api_response = api_instance.replace_csr_cert(csr_id, cert_signing_req_certificate_status=cert_signing_req_certificate_status)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling CertificatesApi->replace_csr_cert: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **csr_id** | **str**| A certificate signing request id | 
 **cert_signing_req_certificate_status** | [**CertSigningReqCertificateStatus**](CertSigningReqCertificateStatus.md)|  | [optional] 

### Return type

[**CertSigningReqCertificateStatus**](CertSigningReqCertificateStatus.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | CertSigningReqCertificateStatus updated |  -  |
**400** | The contents of the request body are invalid |  -  |
**404** | csr does not exist |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

