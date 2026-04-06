"""
Background worker placeholder for future smartwatch stream ingestion.

Current architecture keeps this file to mirror the OCR-style project layout.
"""

import time


def run(poll_interval: float = 5.0):
    print(f"[Worker] Started placeholder loop (interval={poll_interval}s)")
    while True:
        # Future: pull smartwatch queue/device bridge and persist into DB.
        time.sleep(poll_interval)


if __name__ == "__main__":
    run()
