"""This file defines the schemas for the provider and requirer sides of the prometheus_scrape interface."""

from pydantic import BaseModel, ConfigDict, Field, Json


class AlertRuleModel(BaseModel):
    """An alerting or recording rule, as in a Prometheus rule file.

    Rules can have any other field that Prometheus allows, such as `keep_firing_for`.
    """

    model_config = ConfigDict(extra='allow')

    alert: str | None = Field(
        default=None,
        description='The name of the alert. Set for alerting rules.',
        examples=['SomethingIsUp'],
    )
    record: str | None = Field(
        default=None,
        description='The name of the time series to record the result in. Set for recording rules.',
        examples=['job:http_requests:rate5m'],
    )
    expr: str = Field(
        description='The PromQL expression to evaluate.',
        examples=['something_bad == 1'],
    )
    for_: str | None = Field(
        default=None,
        alias='for',
        description='How long the expression must be true before the alert fires.',
        examples=['0m', '5m'],
    )
    labels: dict[str, str] = Field(
        description='Labels to add to the alert or the recorded series, including the Juju topology labels.',
        examples=[{'severity': 'critical', 'juju_model': 'cos', 'juju_application': 'zinc-k8s'}],
    )
    annotations: dict[str, str] | None = Field(
        default=None,
        description='Annotations to add to the alert. The values are templates, expanded when the alert fires.',
        examples=[{'summary': 'Zinc target missing (instance {{ $labels.instance }})'}],
    )


class AlertGroupModel(BaseModel):
    """A group of rules, as in a Prometheus rule file.

    Groups can have any other field that Prometheus allows, such as `interval`.
    """

    model_config = ConfigDict(extra='allow')

    name: str = Field(
        description='The name of the group.',
        examples=['cos_c2e9f4d5_zinc_k8s_alerts'],
    )
    rules: list[AlertRuleModel] = Field(
        description='The rules in the group.',
    )


class AlertRulesModel(BaseModel):
    """Rules in the format of a Prometheus rule file."""

    groups: list[AlertGroupModel] = Field(
        default_factory=list,
        description='The rule groups. Absent when the provider has no rules.',
    )


class ScrapeStaticConfigModel(BaseModel):
    """A static set of scrape targets, as in Prometheus's `static_config`."""

    model_config = ConfigDict(extra='allow')

    targets: list[str] = Field(
        description='The targets to scrape, each `host:port`. A host of `*` means each unit of the provider, at the address in its unit databag.',
        examples=[['*:4080'], ['example.com:9100']],
    )
    labels: dict[str, str] | None = Field(
        default=None,
        description='Labels to add to every metric scraped from these targets.',
        examples=[{'team': 'search'}],
    )


class ScrapeJobModel(BaseModel):
    """A scrape job, as in Prometheus's `scrape_config`.

    Jobs can have other fields of `scrape_config`, such as `scrape_interval`, `scheme`, or
    `tls_config`.
    """

    model_config = ConfigDict(extra='allow')

    job_name: str | None = Field(
        default=None,
        description='The name of the job. Each job of a provider must have a unique name, which should be a fixed string rather than one that changes.',
        examples=['zinc'],
    )
    metrics_path: str | None = Field(
        default=None,
        description='The HTTP path to scrape metrics from.',
        examples=['/metrics'],
    )
    static_configs: list[ScrapeStaticConfigModel] = Field(
        description='The targets to scrape.',
        examples=[[{'targets': ['*:4080']}]],
    )


class ScrapeMetadataModel(BaseModel):
    """The Juju topology of the provider."""

    model_config = ConfigDict(extra='allow')

    model: str = Field(
        description='The name of the Juju model.',
        examples=['cos'],
    )
    # in pydantic v2, `model_` is a protected namespace
    juju_model_uuid: str = Field(
        alias='model_uuid',
        description='The UUID of the Juju model.',
        examples=['c2e9f4d5-dcb3-4870-8509-330eb9745ee8'],
    )
    application: str = Field(
        description='The name of the Juju application.',
        examples=['zinc-k8s'],
    )
    unit: str = Field(
        description='The name of the unit that wrote the metadata.',
        examples=['zinc-k8s/0'],
    )
    charm_name: str | None = Field(
        default=None,
        description='The name of the charm.',
        examples=['zinc-k8s'],
    )


class ProviderAppData(BaseModel):
    """Application databag model for the provider side of the prometheus_scrape interface."""

    model_config = ConfigDict(
        json_schema_extra={
            'examples': [
                {
                    'alert_rules': '{"groups": [{"name": "an_alert_rule_group", "rules": [{"alert": "SomethingIsUp", '
                    '"expr": "something_bad == 1", "for": "0m", "labels": {"some-label": "some-value"}, '
                    '"annotations": {"some-annotation": "some-other-value"}}]}]}',
                    'scrape_jobs': '[{"metrics_path": "/metrics", "static_configs": [{"targets": ["*:4080"]}]}]',
                    'scrape_metadata': '{"model": "cos", "model_uuid": "c2e9f4d5-dcb3-4870-8509-330eb9745ee8", '
                    '"application": "zinc-k8s", "unit": "zinc-k8s/0", "charm_name": "zinc-k8s"}',
                },
                {
                    'alert_rules': '{}',
                    'scrape_jobs': '[{"metrics_path": "/metrics", "static_configs": [{"targets": ["*:80"]}]}]',
                    'scrape_metadata': '{"model": "cos", "model_uuid": "c2e9f4d5-dcb3-4870-8509-330eb9745ee8", '
                    '"application": "zinc-k8s", "unit": "zinc-k8s/0", "charm_name": "zinc-k8s"}',
                },
                {
                    'alert_rules': '{"groups": [{"name": "global_rules", "rules": [{"expr": '
                    '"rate(http_requests_total[5m])", "labels": {}, "record": "job:http_requests:rate5m"}]}]}',
                },
            ]
        }
    )

    alert_rules: Json[AlertRulesModel] | None = Field(
        default=None,
        description='The alert and recording rules for the provider, in the format of a Prometheus rule file, as a JSON object. By default, the library loads them from `src/prometheus_alert_rules`.',
        examples=[
            '{"groups": [{"name": "an_alert_rule_group", "rules": [{"alert": "SomethingIsUp", "expr": "something_bad == 1", "for": "0m", "labels": {"some-label": "some-value"}}]}]}',
            '{}',
        ],
    )
    scrape_jobs: Json[list[ScrapeJobModel]] | None = Field(
        default=None,
        description='The scrape jobs for the requirer to run, as a JSON list. Absent if the provider only forwards rules.',
        examples=['[{"metrics_path": "/metrics", "static_configs": [{"targets": ["*:4080"]}]}]'],
    )
    scrape_metadata: Json[ScrapeMetadataModel] | None = Field(
        default=None,
        description='The Juju topology of the provider, as a JSON object, which the requirer uses to label the metrics and name the jobs and rules. Absent if the provider only forwards rules.',
        examples=[
            '{"model": "cos", "model_uuid": "c2e9f4d5-dcb3-4870-8509-330eb9745ee8", "application": "zinc-k8s", "unit": "zinc-k8s/0", "charm_name": "zinc-k8s"}'
        ],
    )


class ProviderUnitData(BaseModel):
    """Unit databag model for the provider side of the prometheus_scrape interface."""

    model_config = ConfigDict(
        extra='allow',
        json_schema_extra={
            'examples': [
                {
                    'prometheus_scrape_unit_address': '10.1.2.3',
                    'prometheus_scrape_unit_name': 'zinc-k8s/0',
                    'prometheus_scrape_unit_fqdn': 'zinc-k8s-0.zinc-k8s-endpoints.cos.svc.cluster.local',
                },
                {
                    'prometheus_scrape_unit_address': 'zinc-k8s-0.zinc-k8s-endpoints.cos.svc.cluster.local',
                    'prometheus_scrape_unit_name': 'zinc-k8s/0',
                    'prometheus_scrape_unit_fqdn': 'zinc-k8s-0.zinc-k8s-endpoints.cos.svc.cluster.local',
                },
                {
                    'prometheus_scrape_unit_address': 'ingress.example.com',
                    'prometheus_scrape_unit_name': 'zinc-k8s/0',
                    'prometheus_scrape_unit_path': '/cos-zinc-k8s-0',
                },
            ]
        },
    )

    prometheus_scrape_unit_address: str = Field(
        description='The address to scrape the unit at, which replaces `*` in the targets of the scrape jobs. It is the unit\'s IP address, its fully qualified domain name if the IP address isn\'t known, or the host of the ingress or proxy in front of it.',
        examples=['10.1.2.3', 'zinc-k8s-0.zinc-k8s-endpoints.cos.svc.cluster.local'],
    )
    prometheus_scrape_unit_name: str = Field(
        description='The name of the unit, which the requirer uses for the `juju_unit` label.',
        examples=['zinc-k8s/0'],
    )
    prometheus_scrape_unit_path: str | None = Field(
        default=None,
        description='The path prefix to scrape the unit at. It is present when the provider is behind an ingress or a proxy.',
        examples=['/cos-zinc-k8s-0'],
    )
    prometheus_scrape_unit_fqdn: str | None = Field(
        default=None,
        description='The fully qualified domain name of the unit, which the requirer uses to match targets that name the unit rather than using `*`. It is absent when the provider is behind an ingress or a proxy.',
        examples=['zinc-k8s-0.zinc-k8s-endpoints.cos.svc.cluster.local'],
    )


class RequirerEventModel(BaseModel):
    """Feedback to the provider about the scrape jobs and rules it published."""

    model_config = ConfigDict(extra='allow')

    errors: str | None = Field(
        default=None,
        description='Why the provider\'s alert rules could not be used. Absent while the rules are valid.',
        examples=['error validating: rule 0: could not parse expression'],
    )
    scrape_job_errors: str | None = Field(
        default=None,
        description='Why the provider\'s scrape jobs could not be used. Absent while the jobs are valid.',
        examples=[
            "Command '['cos-tool-amd64', 'validate-config', '/tmp/tmpq8n2v3.yaml']' returned non-zero exit status 1."
        ],
    )


class RequirerAppData(BaseModel):
    """Application databag model for the requirer side of the prometheus_scrape interface."""

    model_config = ConfigDict(
        json_schema_extra={
            'examples': [
                {'event': '{}'},
                {'event': '{"errors": "error validating: rule 0: could not parse expression"}'},
            ]
        }
    )

    event: Json[RequirerEventModel] | None = Field(
        default=None,
        description='Feedback to the provider about the scrape jobs and rules it published, as a JSON object.',
        examples=['{}', '{"errors": "error validating: rule 0: could not parse expression"}'],
    )


RequirerUnitData = None
