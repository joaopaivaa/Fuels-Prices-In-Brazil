import subprocess
import sys

steps = [
    "src/etl_fuels_prices/download_executor.py",
    "src/etl_fuels_prices/transformation_silver_layer.py",
    "src/etl_fuels_prices/transformation_gold_layer.py",
]

try:

    print(f"Downloading new data ...")
    extraction_step = subprocess.run(
        [sys.executable, "src/etl_fuels_prices/download_executor.py"],
        check=True
    )

    print(f"Transforming data to silver layer...")
    subprocess.run(
        [sys.executable, "src/etl_fuels_prices/transformation_silver_layer.py"],
        check=True
    )

    print(f"Transforming data to gold layer...")
    subprocess.run(
        [sys.executable, "src/etl_fuels_prices/transformation_gold_layer.py"],
        check=True
    )

except subprocess.CalledProcessError as e:
    print(f"An error occurred during the pipeline execution: {e}")