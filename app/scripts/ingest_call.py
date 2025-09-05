from app.workers.ingestion import ingest_call


def main():
    for i in range(1, 11):
        result = ingest_call.apply_async(
            kwargs={"call_id": i},
            queue="ingestion"
        )
        print(f"Enqueued task for call_id={i}, task_id={result.id}")


if __name__ == "__main__":
    main()