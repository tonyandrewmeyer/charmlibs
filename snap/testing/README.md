# charmlibs.snap_testing

The `charmlibs-snap` testing library: a stateful fake snapd. Charms that use `charmlibs.snap`
should use this library in their `ops.testing` (or plain pytest) tests instead of monkeypatching
`charmlibs.snap`'s public functions directly.

To install, add `charmlibs-snap[testing]` to your test dependencies (the `testing` extra keeps
this package's version in step with `charmlibs-snap`'s). Then in your test code:

```python
from charmlibs import snap_testing


def test_install_handler(snapd: snap_testing.Snapd):  # the `snapd` fixture ships automatically
    ctx = ops.testing.Context(PrometheusCharm)
    ctx.run(ctx.on.install(), ops.testing.State())

    assert snapd.installed['prometheus'].channel == '2/stable'
    assert snapd.installed['prometheus'].services == {}
```

The fixture gives an empty machine in permissive mode: any snap can be installed from any
channel, and fields the call didn't name get fixed defaults (revision `'1'`, version `'1.0'`).
A snap installed this way has no services, so a charm that starts one gets the same
`AppNotFoundError` it would from a snap that doesn't ship it. To test services, either seed
the snap as installed with its services:

```python
def test_config_changed_refreshes_channel():
    snapd = snap_testing.Snapd([
        snap_testing.Snap('prometheus', channel='2/stable', services={'prometheus': 'active'}),
    ])
    ctx = ops.testing.Context(PrometheusCharm)

    with snapd:
        ctx.run(ctx.on.config_changed(), ops.testing.State(config={'channel': '2/edge'}))

    assert snapd.installed['prometheus'].channel == '2/edge'
```

or describe a store, which makes the double authoritative: only the snaps, channels and
revisions it lists exist, and an install gets its revision, version and services from it.

```python
def test_install_starts_prometheus():
    snapd = snap_testing.Snapd(store=[
        snap_testing.StoreSnap(
            'prometheus',
            channels={'2/stable': 101, '2/edge': 105},
            version='2.53.0',
            services=['prometheus'],
            daemon_services=['prometheus'],  # enabled and started on install
        ),
    ])
    ctx = ops.testing.Context(PrometheusCharm)

    with snapd:
        ctx.run(ctx.on.install(), ops.testing.State())

    installed = snapd.installed['prometheus']
    assert (installed.revision, installed.version) == ('101', '2.53.0')
    assert installed.services == {'prometheus': 'active'}
```

`Snapd` enters as a context manager around the code under test -- it patches
`charmlibs.snap._client.get/get_logs/post/put` for the duration of the `with` block (or the
fixture's lifetime), so the real library code above the socket -- validation, channel
resolution, error mapping -- all still runs. Only the daemon itself is simulated.

What the double reproduces was checked against a real snapd, and `charmlibs-snap`'s own unit
tests run against it, so a difference between the two is a bug in the double.

See the [library reference documentation](https://canonical.com/juju/docs/charmlibs/reference/charmlibs/snap)
for more on `charmlibs.snap` itself.
