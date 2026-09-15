import argparse
import json
from datetime import datetime

import apache_beam as beam
from apache_beam.io.gcp.bigquery import BigQueryDisposition, WriteToBigQuery
from apache_beam.io.gcp.pubsub import ReadFromPubSub
from apache_beam.options.pipeline_options import PipelineOptions
from apache_beam.transforms.window import FixedWindows

PROJECT_ID = "de-project-02-gcp-warehouse"
SUBSCRIPTION = (
    "projects/de-project-02-gcp-warehouse/" "subscriptions/clickstream-events-sub"
)

BQ_TABLE = "de-project-02-gcp-warehouse:streaming.page_events"


class ParseEvent(beam.DoFn):
    def process(self, message):
        event = json.loads(message.decode("utf-8"))

        timestamp = datetime.fromisoformat(event["timestamp"].replace("Z", "+00:00"))

        # Count.PerKey() expects (key, value)
        # Here:
        #   key   = page
        #   value = 1 event
        yield beam.window.TimestampedValue(
            (event["page"], 1),
            timestamp.timestamp(),
        )


class AddWindowInfo(beam.DoFn):
    def process(self, element, window=beam.DoFn.WindowParam):
        page, count = element

        yield {
            "window_start": window.start.to_utc_datetime(),
            "window_end": window.end.to_utc_datetime(),
            "page": page,
            "event_count": count,
        }


def run(argv=None):
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--runner",
        default="DirectRunner",
    )

    known_args, pipeline_args = parser.parse_known_args(argv)

    pipeline_options = PipelineOptions(
        pipeline_args,
        streaming=True,
        save_main_session=True,
    )

    with beam.Pipeline(
        runner=known_args.runner,
        options=pipeline_options,
    ) as pipeline:

        events = (
            pipeline
            | "ReadFromPubSub" >> ReadFromPubSub(subscription=SUBSCRIPTION)
            | "ParseEvents" >> beam.ParDo(ParseEvent())
        )

        windowed_counts = (
            events
            | "FixedWindows" >> beam.WindowInto(FixedWindows(60))
            | "CountByPage" >> beam.combiners.Count.PerKey()
        )

        results = windowed_counts | "AddWindowInfo" >> beam.ParDo(AddWindowInfo())

        results | "WriteToBigQuery" >> WriteToBigQuery(
            table=BQ_TABLE,
            schema={
                "fields": [
                    {
                        "name": "window_start",
                        "type": "TIMESTAMP",
                    },
                    {
                        "name": "window_end",
                        "type": "TIMESTAMP",
                    },
                    {
                        "name": "page",
                        "type": "STRING",
                    },
                    {
                        "name": "event_count",
                        "type": "INTEGER",
                    },
                ]
            },
            write_disposition=BigQueryDisposition.WRITE_APPEND,
            create_disposition=BigQueryDisposition.CREATE_NEVER,
        )


if __name__ == "__main__":
    run()
