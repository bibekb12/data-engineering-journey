import argparse, json, random, time
from datetime import datetime, timezone

from google.cloud import pubsub_v1

PROJECT_ID = "de-project-02-gcp-warehouse"
TOPIC_ID = "clickstream-events"

PAGES = [
    "/",
    "/home",
    "/products",
    "/product/123",
    "/cart",
    "/checkout",
]

EVENT_TYPES = [
    "page_view",
    "click",
    "add_to_cart",
    "purchase",
]


def create_event():
    """Generate a single fake clickstream event"""
    return {
        "user_id": f"user_{random.randint(1,100):03d}",
        "page": random.choice(PAGES),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event_type": random.choice(EVENT_TYPES),
    }


def publish_event(publisher, topic_path, event):
    """publish one event to pub/sub"""
    message = json.dumps(event).encode("utf-8")
    future = publisher.publish(topic_path, message)
    message_id = future.result()
    return message_id


def run(events=None, interval=1.0):
    """publish events either a fixed number or continuously"""
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(PROJECT_ID, TOPIC_ID)

    print("=== Event Simulator ===")
    print(f"Project: {PROJECT_ID}")
    print(f"Topic: {TOPIC_ID}")
    print(f"Interval: {interval}s")

    if events is not None:
        print(f"Events: {events}")
    else:
        print("Mode: Continuous")
    print()

    count = 0

    try:
        while events is None or count < events:
            event = create_event()

            message_id = publish_event(
                publisher,
                topic_path,
                event,
            )

            count += 1

            print(
                f"[{count}] " f"message_id={message_id} " f"event={json.dumps(event)}"
            )

            if events is not None and count >= events:
                break

            time.sleep(interval)
    except KeyboardInterrupt:
        print("\n ===Simulator stopped ===")

    print(f"Published events: {count}")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Generate fake clickstream events and publish them to pub/sub."
    )

    mode = parser.add_mutually_exclusive_group(required=True)

    mode.add_argument(
        "--events",
        type=int,
        help="publish a fixed number of events.",
    )

    mode.add_argument(
        "--continuous",
        action="store_true",
        help="Publish events continously until Ctrl+C",
    )

    parser.add_argument(
        "--interval",
        type=float,
        default=1.0,
        help="Seconds between events. Default 1.0",
    )

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    if args.events is not None and args.events <= 0:
        raise SystemExit("--events must be greater than 0")
    if args.interval < 0:
        raise SystemExit("--interval must be >= 0")

    run(events=args.events, interval=args.interval)
