from app.workers.insights import generate_call_insights
from app.celery import celery


generate_call_insights.app = celery


def main():
    for i in range(1, 11):
        result = generate_call_insights.apply_async(
            kwargs={"call_id": i}, queue="insights"
        )
        print(f"Enqueued task for call_id={i}, task_id={result.id}")


if __name__ == "__main__":
    main()
