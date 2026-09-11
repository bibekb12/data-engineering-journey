import apache_beam as beam


def main():
    with beam.Pipeline() as pipline:
        (
            pipline
            | "create data" >> beam.Create(["weather", "data", "engineering"])
            | "Uppercase" >> beam.Map(str.upper)
            | "Print" >> beam.Map(print)
        )


if __name__ == "__main__":
    main()
