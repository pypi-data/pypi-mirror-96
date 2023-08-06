# CertSigningReqCertificateStatus

A CSR certificate status
## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**certificates** | [**list[X509Certificate]**](X509Certificate.md) | The issued x509 certificates, formatted as PEM. This list is sorted by X509Certificate.not_before.  | [optional] 
**ready** | **bool** | The status of the certificate. true: The certificate has been signed and is ready for use false: The certificate is not ready  | 
**message** | **str** | A system message associated with the reason.  | 
**reason** | [**CSRReasonEnum**](CSRReasonEnum.md) |  | 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


