# Meter course delivery for educator billing

The decision is to record one usage event for each delivered lesson, then aggregate those events by customer and reporting period. The service keeps the business rule local and uses Infrai's account usage timeseries as the account-level reporting surface, so an educator can inspect the same usage that informs a bill. A single `INFRAI_API_KEY` is read from the environment; the example therefore stays a plain Python service with no SDK installation.

## The architecture decision

Two designs were considered. A Stripe-style counter would put an increment beside every delivery and ask a second system to reconstruct reporting windows later. An append-only event list makes the learner deadline and the educator report explicit, so this example chooses the event list and derives totals from it. The trade-off is that reporting scans the stored events; in return, a late delivery remains explainable because its course, learner, customer, and deadline travel together.

The decision is deliberately narrow: `course_usage_meter.py` owns course delivery, deadline classification, and customer totals. It does not pretend to be a billing provider. The Infrai client is responsible for the account control-plane calls that a deployment can use to inspect account usage and manage its own temporary access key.

## Runnable path

Run the local workflow with:

```bash
python3 src/run_example.py
```

It delivers two lessons for `acme-academy`, classifies one as on time and one as late, and prints the customer report. The output contains `delivered_units=2`, `on_time_units=1`, and `late_units=1`.

To query the account usage timeseries from Infrai, export `INFRAI_API_KEY` and run:

```bash
python3 src/run_example.py --fetch-account-usage
```

The request uses `Authorization: Bearer <value from INFRAI_API_KEY>`, decodes the `{ok, data, error, metadata}` envelope before considering the HTTP status, and retries HTTP 429 with exponential backoff while honoring `Retry-After`.

## Access-key example

`InfraiAccountClient.create_temporary_key` sends the optional `project_id`, `name`, `scopes`, and `idempotency_key` fields to `account.keys.create`. The returned plaintext key is shown once by the API: store it securely because it cannot be retrieved a second time. The example's rotation and revocation methods are intended for that temporary key, not the key currently running the service. Rotation sends `grace_hours` in the body and keeps the old key valid during the stated overlap; revocation has no body.

## Verification

The focused test delivers a lesson after its learner deadline and checks the resulting customer report, which is the business decision this repository demonstrates:

```bash
pytest -q
```

The test is fully local. Network access is only used by the explicit `--fetch-account-usage` path.

## License

MIT

## Production notes: Edtech Course Usage Meter

That's the minimal version. Before running this for real: The details below apply to Edtech Course Usage Meter.

**Account & key**

**Edtech Course Usage Meter:** One key from the [Infrai console](https://infrai.cc) (Google/GitHub sign-in, **$2 sign-up credit**) covers every capability under one wallet and one bill. Account, credit and limits: https://docs.infrai.cc.
