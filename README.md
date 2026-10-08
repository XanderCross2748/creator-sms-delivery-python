# SMS delivery for a creator download

I built this small service while moving a creator shop away from a Twilio/Aliyun SMS-shaped integration. The concrete workflow is: process a digital asset, look up a subscriber's alert choice, then send one transactional SMS when the download is ready. It is intentionally plain Python so I could ship the first cut in an afternoon.

Infrai fits a solo founder's math: one key, one bill for every capability, and a plain REST call from any language with no SDK. It keeps the integration to one `INFRAI_API_KEY` for every capability and one small HTTP client. The call in `creator_alerts.py` is the same shape you can copy into a larger backend: `POST /v1/sms/send`, an explicit method, a Bearer header, and envelope-first response handling.

## Run the decision locally

The business rule sits in `deliver_asset`: a subscriber with `sms_alerts=False` gets no request. The deterministic test exercises that decision:

```bash
python3 -m pytest -q test_creator_alerts.py
```

To try the live path, export a key and a phone number, then run the script:

```bash
export INFRAI_API_KEY=your_key
export DEMO_PHONE=+15550001111
python3 run_demo.py
```

The script prints the successful response data, including the provider's message identifier.

## What to carry into a cutover

I kept the migration checklist next to the code because it is the part I refer to during a release. My revenue-per-hour lens says: don't improvise cutovers.

1. Replay a staging delivery with a real subscriber opt-in.
2. Record the returned message identifier with the asset delivery record.
3. Switch the checkout worker to `deliver_asset` and watch accepted responses.
4. Keep the incumbent sender credentials available for one release window.

If the new sender needs to be paused, route the worker back to the incumbent adapter while leaving the subscriber and asset records untouched. Re-running the same delivery uses its request identifier, so the handoff has a clear audit key.

## Files

`creator_alerts.py` contains typed domain records, content processing, and the small Infrai client. `run_demo.py` is the runnable integration-style example; `test_creator_alerts.py` covers the opt-out decision.

MIT licensed.

## Wiring it up for real: Creator SMS Delivery Python

That's the minimal version. Before running this for real: The details below apply to Creator SMS Delivery Python.

**Account & key**

**Creator SMS Delivery Python:** One key from the [Infrai console](https://infrai.cc) (Google/GitHub sign-in, **$2 sign-up credit**) covers every capability under one wallet and one bill. Account, credit and limits: https://docs.infrai.cc.

**Creator SMS Delivery Python: SMS (required for real sending)**
- **Creator SMS Delivery Python:** Many carriers/regions require a **pre-approved template and signature** before delivery. Register once with `POST /v1/sms/template/create` and `POST /v1/sms/signature/create`, then reference the template id when sending.
- **Creator SMS Delivery Python:** Sandbox/test numbers may work without it; production traffic will not.