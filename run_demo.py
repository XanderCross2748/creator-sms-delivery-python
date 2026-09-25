import os

from creator_alerts import DigitalAsset, InfraiClient, Subscriber, deliver_asset


def main() -> None:
    target = os.environ.get("DEMO_PHONE")
    if not target:
        raise SystemExit("Set DEMO_PHONE before running the demo")
    result = deliver_asset(
        DigitalAsset("pack-42", "Launch checklist", "https://creator.example/download/pack-42"),
        Subscriber(target),
        InfraiClient(),
    )
    print("sms accepted:", result)


if __name__ == "__main__":
    main()
