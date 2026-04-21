import subprocess
import sys

steps = [
    "download_executor.py",
    "transformation_silver_layer.py",
    "transformation_gold_layer.py",
]

try:
    print(f"Downloading new data ...")
    subprocess.run(
        [sys.executable, "download_executor.py"],
        check=True
    )
except subprocess.CalledProcessError as e:
    print(f"An error occurred during the download step: {e}")

print(f"Transforming data to silver layer...")
subprocess.run(
    [sys.executable, "transformation_silver_layer.py"],
    check=True
)

print(f"Transforming data to gold layer...")
subprocess.run(
    [sys.executable, "transformation_gold_layer.py"],
    check=True
)