# kubeflow_dashboard_links

## Behavior

Keywords are as in RFC 2119.

### Provider

- MUST NOT write to either databag.
- MUST show a link on the dashboard, at its `location`, for each entry in each requirer's `dashboard_links`.
- SHOULD treat a requirer that hasn't written `dashboard_links` as having no links.
- SHOULD remove a requirer's links when the relation is removed.
- MAY add links of its own, and MAY choose the order of the links.

### Requirer

- MUST write `dashboard_links` to the application databag from the leader unit, with zero or more links.
- MUST set each link's `location` to one of `menu`, `external`, `quick`, or `documentation`.
- SHOULD use a relative link for the `menu` and `quick` locations, and a full URL for the others.
- SHOULD update `dashboard_links` when its links change, for example when the charm is upgraded.
