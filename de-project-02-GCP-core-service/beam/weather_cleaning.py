import apache_beam as beam


class CleanWeather(beam.DoFn):
    def process(self, record):
        temperature = record.get("temperature")
        humidity = record.get("humidity")

        if temperature is None:
            return

        clean_record = {
            "city": record["city"],
            "temperature_c": float(temperature),
            "humidity_pct": float(humidity) if humidity is not None else None,
        }
        yield clean_record


def main():
    raw_weather = [
        {
            "city": "Kathmandu",
            "temperature": 24.5,
            "humidity": 72,
        },
        {
            "city": "pokhara",
            "temperature": 22.1,
            "humidity": 81,
        },
        {
            "city": "Invalid city",
            "temperature": None,
            "humidity": 50,
        },
        {
            "city": "hetaud",
            "temperature": None,
            "humidity": None,
        },
    ]

    with beam.Pipeline() as pipeline:
        (
            pipeline
            | "create raw weather" >> beam.Create(raw_weather)
            | "clean weather" >> beam.ParDo(CleanWeather())
            | "Print cleaned weather" >> beam.Map(print)
        )


if __name__ == "__main__":
    main()
