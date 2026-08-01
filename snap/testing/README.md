# charmlibs.snap_testing

The `charmlibs-snap` testing library: a stateful fake snapd. Charms that use `charmlibs.snap`
should use this library in their `ops.testing` (or plain pytest) tests instead of monkeypatching
`charmlibs.snap`'s public functions directly.

To install, add `charmlibs-snap-testing` to your Python dependencies. Then in your test code:

```python
from charmlibs import snap_testing


def test_install_handler(snapd: snap_testing.Snapd):  # the `snapd` fixture ships automatically
    ctx = ops.testing.Context(PrometheusCharm)
    ctx.run(ctx.on.install(), ops.testing.State())

    assert snapd.installed['prometheus'].channel == '2/stable'
    assert snapd.installed['prometheus'].services['prometheus'] == 'active'
```

Or, without the fixture:

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

`Snapd` enters as a context manager around the code under test -- it patches
`charmlibs.snap._client.get/get_logs/post/put` for the duration of the `with` block (or the
fixture's lifetime), so the real library code above the socket -- validation, channel
resolution, error mapping -- all still runs. Only the daemon itself is simulated.

See the [design document](../../non-roadmap/snaptest/design.md) in the `canonical-work-queue`
staging repo for the full design, and the
[implementation log](../../non-roadmap/snaptest/IMPLEMENTATION.md) for what's built, what
deviates from the design, and what's left.

See the [library reference documentation](https://canonical.com/juju/docs/charmlibs/reference/charmlibs/snap)
for more on `charmlibs.snap` itself.
