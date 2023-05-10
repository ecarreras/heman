# Changelog

## Unreleased

- New plugable and configurable curve backends
- New curve backend for Timescale based curves
- Fix: curve time handling and conversion, now curves properly
  start and end in 00:00 local time and timestamps base on UTC Epoch
- Upgrade notes:
    - Need to set the environ `POSTGRESQL_URI` pointing to ERP database
    for the timescale curve backend.
    - You can set environ `DEFAULT_CURVE_BACKEND` to set the default
    to either `mongo` or `timescale`, default `mongo`
    - You can set environ `CURVE_BACKENDS` to a json dict, mapping
    concrete curves (`tg_f1`...) to a different backend.
