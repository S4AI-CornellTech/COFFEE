#!/usr/bin/env python3
import pandas as pd
import argparse
import glob
import os

def extract_metrics_from_file(input_csv, required_columns):
    # Read the CSV file
    df = pd.read_csv(input_csv)
    
    # Remove rows where the column header might be repeated (e.g., in concatenated files)
    df = df[df[required_columns[2]].astype(str) != required_columns[2]]

    # Check for missing required columns
    missing = [c for c in required_columns if c not in df.columns]
    if missing:
        raise ValueError(f"File {input_csv} is missing columns: {missing}")

    # Extract only the required columns
    df_ex = df[required_columns].copy()
    df_ex["Source"] = os.path.basename(input_csv)

    # Convert specific columns to numeric types
    numeric_cols = [
        "Total Dynamic Read Energy (mJ)",
        "Total Dynamic Write Energy (mJ)",
        "Total Read Latency (ms)",
        "Total Write Latency (ms)",
        "Read Latency (ns)",
        "Write Latency (ns)",
        "Read Energy (pJ)",
        "Write Energy (pJ)",
        "Leakage Power (mW)"
    ]
    df_ex[numeric_cols] = df_ex[numeric_cols].apply(pd.to_numeric, errors='coerce')

    # Calculate EDP (Energy-Delay Product)
    df_ex["ReadEDP (mJ ms)"] = df_ex["Total Dynamic Read Energy (mJ)"] * df_ex["Total Read Latency (ms)"]
    df_ex["WriteEDP (mJ ms)"] = df_ex["Total Dynamic Read Energy (mJ)"] * df_ex["Total Write Latency (ms)"]

    # Calculate total memory latency
    df_ex["Total memory latency (ms)"] = df_ex["Total Read Latency (ms)"] + df_ex["Total Write Latency (ms)"]

    # Calculate total energy per access (Static + Dynamic energy)
    df_ex["Read Energy per access (pJ)"] = df_ex["Leakage Power (mW)"] * df_ex["Read Latency (ns)"] + df_ex["Read Energy (pJ)"] 
    df_ex["Write Energy per access (pJ)"] = df_ex["Leakage Power (mW)"] * df_ex["Write Latency (ns)"] + df_ex["Write Energy (pJ)"] 
    
    # Calculate static energy per access
    df_ex["Read Static Energy per access (pJ)"] = df_ex["Leakage Power (mW)"] * df_ex["Read Latency (ns)"]  
    df_ex["Write Static Energy per access (pJ)"] = df_ex["Leakage Power (mW)"] * df_ex["Write Latency (ns)"] 

    # Calculate EDP per access
    # WriteEDP per access (nJ ns): Write Latency (ns) * Write Energy (pJ) [ns*pJ -> nJ ns]
    df_ex["WriteEDP per access (nJ ns)"] = df_ex["Write Latency (ns)"] * df_ex["Write Energy per access (pJ)"] * 1e-3
    # ReadEDP per access (nJ ns)
    df_ex["ReadEDP per access (nj ns)"] = df_ex["Read Latency (ns)"] * df_ex["Read Energy per access (pJ)"] * 1e-3

    return df_ex

def main():
    parser = argparse.ArgumentParser(
        description="Extract and integrate metrics from NVMExplorer output CSV files."
    )
    parser.add_argument(
        "--nvm_dir",
        required=True,
        help="Path to the directory containing NVMExplorer output CSV files"
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Path to save the integrated output CSV file"
    )
    args = parser.parse_args()

    # Define the columns to extract from the original CSV
    required_columns = [
        "Benchmark Name",
        "MemoryCellInputFile",
        "Total Dynamic Read Energy (mJ)",
        "Total Dynamic Write Energy (mJ)",
        "Total Read Latency (ms)",
        "Total Write Latency (ms)",
        "Area (mm^2)",
        "Area Efficiency (percent)",
        "Total Power",
        "Read Latency (ns)",
        "Write Latency (ns)",
        "Read Energy (pJ)",
        "Write Energy (pJ)",
        "Leakage Power (mW)",
        "Capacity (MB)",
        "CellArea (F^2)"
    ]

    # Fetch all CSV files in the target directory
    search_pattern = os.path.join(args.nvm_dir, "*.csv")
    raw_files = glob.glob(search_pattern)

    # Filter files based on specific sizes and benchmark names
    sizes = ["2MB", "4MB"]
    input_files = [
        f for f in raw_files
        if any(f"FeFET_{size}" in os.path.basename(f) for size in sizes)
           and "main_dnn" in os.path.basename(f)
    ]

    if not input_files:
        print("No matching results found. Exiting.")
        return

    all_dfs = []
    for fn in input_files:
        print(f"Processing file: {fn}")
        df = extract_metrics_from_file(fn, required_columns)
        if df is not None:
            all_dfs.append(df)

    if not all_dfs:
        print("No valid data extracted. Exiting.")
        return

    # Concatenate all dataframes and filter by Benchmark Name
    result_df = pd.concat(all_dfs, ignore_index=True)
    result_df = result_df[result_df["Benchmark Name"].isin(["ResNet50_int"])]

    try:
        # Ensure the output directory exists
        output_dir = os.path.dirname(args.output)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        # Save the final integrated dataframe to CSV
        result_df.to_csv(args.output, index=False)
        print(f"Successfully finished writing to: {args.output}")
    except Exception as e:
        print(f"Error occurred while writing to {args.output}: {e}")

if __name__ == "__main__":
    main()