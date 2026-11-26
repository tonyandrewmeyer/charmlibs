"""This file defines the schema for the requirer side of the nginx-route interface.

It defines one model, `RequirerAppData`.
"""

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class RequirerAppData(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "service-hostname": "example.test",
                    "service-name": "test-app",
                    "service-port": "8080",
                    "service-namespace": "test-namespace",
                },
                {
                    "service-hostname": "blog.example.com",
                    "service-name": "wordpress-k8s",
                    "service-port": "80",
                    "service-namespace": "wordpress",
                    "owasp-modsecurity-crs": "True",
                    "owasp-modsecurity-custom-rules": 'SecAction "id:900130,phase:1,nolog,pass,t:none,setvar:tx.crs_exclusions_wordpress=1"\n',
                },
            ]
        }
    )

    service_hostname: str = Field(
        alias="service-hostname",
        description="The hostname of the service to create an ingress for.",
        examples=["example.com"],
        title="Service Hostname",
    )
    service_name: str = Field(
        alias="service-name",
        description="The name of the Kubernetes service to create an ingress for.",
        examples=["wordpress", "indico"],
        title="Service Name",
    )
    service_port: int = Field(
        alias="service-port",
        description="The port of the service to create an ingress for.",
        examples=["8080", "80"],
        title="Service Port",
    )
    service_namespace: Optional[str] = Field(
        None,
        alias="service-namespace",
        description="The namespace of the service to create an ingress for. If not set, the provider uses the namespace of its own model.",
        examples=["test-namespace"],
        title="Service Namespace",
    )
    additional_hostnames: Optional[str] = Field(
        None,
        alias="additional-hostnames",
        description="Comma-separated list of additional hostnames for this ingress to listen on.",
        examples=["www.example.com,example.com"],
        title="Additional Hostnames",
    )
    backend_protocol: Optional[str] = Field(
        None,
        alias="backend-protocol",
        description="The protocol used to talk to the service: one of `HTTP`, `HTTPS`, `GRPC`, `GRPCS`, or `FCGI` (case-insensitive). Defaults to `HTTP`.",
        examples=["HTTPS"],
        title="Backend Protocol",
    )
    enable_access_log: Optional[bool] = Field(
        None,
        alias="enable-access-log",
        description="Whether to enable the Nginx access log for this ingress. Defaults to true.",
        examples=["false", "true"],
        title="Enable Access Log",
    )
    limit_rps: Optional[int] = Field(
        None,
        alias="limit-rps",
        description="Number of requests accepted from a given IP each second. The burst limit is set to this limit multiplied by 5. When clients exceed this limit a 503 error will be returned. Setting this to 0 disables rate-limiting.",
        examples=["10"],
        title="Limit Rps",
    )
    limit_whitelist: Optional[str] = Field(
        None,
        alias="limit-whitelist",
        description="If rate-limiting is set, client IP source ranges to be excluded. The value is a comma-separated list of CIDRs.",
        examples=["10.0.0.0/8,172.16.0.0/12,192.168.0.0/16"],
        title="Limit Whitelist",
    )
    max_body_size: Optional[int] = Field(
        None,
        alias="max-body-size",
        description="Max allowed body-size (for file uploads) in megabytes, set to 0 to disable limits.",
        examples=["20"],
        title="Max Body Size",
    )
    owasp_modsecurity_crs: Optional[bool] = Field(
        None,
        alias="owasp-modsecurity-crs",
        description="Enable OWASP ModSecurity Core Rule Set (CRS). A set of generic attack detection rules for use with ModSecurity or compatible web application firewalls. The CRS aims to protect web applications from a wide range of attacks, including the OWASP Top Ten, with a minimum of false alerts. See https://github.com/coreruleset/coreruleset for more details. The provider treats any value other than `true` (case-insensitive) as false.",
        examples=["True", "false"],
        title="Owasp Modsecurity Crs",
    )
    owasp_modsecurity_custom_rules: Optional[str] = Field(
        None,
        alias="owasp-modsecurity-custom-rules",
        description="New line separated list of custom rules to be added to modsecurity-snippet annotation. A literal `\\n` is also treated as a new line.",
        examples=[
            "SecAction id:900130,phase:1,nolog,pass,t:none,setvar:tx.crs_exclusions_wordpress=1\n"
        ],
        title="Owasp Modsecurity Custom Rules",
    )
    path_routes: Optional[str] = Field(
        None,
        alias="path-routes",
        description='Comma separated list of the routes under the hostname that you wish to map to the relation. Example: "/admin,/portal" will map example.test/admin and example.test/portal only. Defaults to "/".',
        examples=["/admin,/portal", "/something(/|$)(.*)"],
        title="Path Routes",
    )
    proxy_buffer_size: Optional[int] = Field(
        None,
        alias="proxy-buffer-size",
        description="Size, in kilobytes, of the buffer used for reading the first part of the response from the proxied server. Must be larger than 0, and should be a multiple of the page size.",
        examples=["4"],
        title="Proxy Buffer Size",
    )
    proxy_connect_timeout: Optional[int] = Field(
        None,
        alias="proxy-connect-timeout",
        description="Timeout, in seconds, for establishing a connection with the proxied server.",
        examples=["5"],
        title="Proxy Connect Timeout",
    )
    proxy_read_timeout: Optional[int] = Field(
        None,
        alias="proxy-read-timeout",
        description="Timeout, in seconds, for reading a response from the proxied server.",
        examples=["60"],
        title="Proxy Read Timeout",
    )
    proxy_send_timeout: Optional[int] = Field(
        None,
        alias="proxy-send-timeout",
        description="Timeout, in seconds, for transmitting a request to the proxied server.",
        examples=["60"],
        title="Proxy Send Timeout",
    )
    retry_errors: Optional[str] = Field(
        None,
        alias="retry-errors",
        description='Specifies in which cases a request should be retried against the next server. Comma-separated list, e.g. "error,timeout,http_502,http_503,http_504". See http://nginx.org/en/docs/http/ngx_http_proxy_module.html#proxy_next_upstream for more details. Unrecognised values will be ignored. The nginx default will be used if this is set to an empty value.',
        examples=["error,timeout,http_502,http_503,http_504"],
        title="Retry Errors",
    )
    rewrite_enabled: Optional[bool] = Field(
        None,
        alias="rewrite-enabled",
        description="Whether requests should be rewritten to the `rewrite-target`. The provider treats any value other than `true` (case-insensitive) as false.",
        examples=["True", "false"],
        title="Rewrite Enabled",
    )
    rewrite_target: Optional[str] = Field(
        None,
        alias="rewrite-target",
        description='The path to rewrite requests to. If not set, rewrite-target will be "/".',
        examples=["/app1", "/$2"],
        title="Rewrite Target",
    )
    session_cookie_max_age: Optional[int] = Field(
        None,
        alias="session-cookie-max-age",
        description="The max age to configure a session cookie for. Leaving unset or setting to 0 will disable session cookies and cookie-based affinity.",
        examples=["3600"],
        title="Session Cookie Max Age",
    )
    tls_secret_name: Optional[str] = Field(
        None,
        alias="tls-secret-name",
        description="The name of the Kubernetes TLS secret to use. Leaving this empty will configure an ingress with TLS disabled.",
        examples=["example-com-tls"],
        title="Tls Secret Name",
    )
    use_regex: Optional[bool] = Field(
        None,
        alias="use-regex",
        description="Whether the paths in `path-routes` are regular expressions. The provider treats any value other than `true` (case-insensitive) as false.",
        examples=["true"],
        title="Use Regex",
    )


ProviderAppData = None
ProviderUnitData = None
RequirerUnitData = None
