from creator_alerts import DigitalAsset, Subscriber, deliver_asset


class StubClient:
    def __init__(self):
        self.calls = []

    def send_sms(self, to, message, request_id):
        self.calls.append((to, message, request_id))
        return {"message_id": "msg-1"}


def test_unsubscribed_subscriber_receives_no_alert():
    client = StubClient()
    asset = DigitalAsset("a1", "Mini course", "https://creator.example/a1")
    assert deliver_asset(asset, Subscriber("+15550001111", sms_alerts=False), client) is None
    assert client.calls == []

