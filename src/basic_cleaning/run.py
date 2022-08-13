#!/usr/bin/env python
"""
Download from W&B the raw dataset and apply some basic data cleaning, exporting the result to a new artifact
"""
import argparse
import logging
import os

import pandas as pd
import wandb

logging.basicConfig(level=logging.INFO, format="%(asctime)-15s %(message)s")
logger = logging.getLogger()


def go(args):

    run = wandb.init(job_type="basic_cleaning")
    run.config.update(args)

    # Download input artifact. This will also log that this script is using this
    # particular version of the artifact
    # artifact_local_path = run.use_artifact(args.input_artifact).file()

    logger.info("Downloading artifact")
    artifact_path = run.use_artifact(args.input_artifact).file()
    df = pd.read_csv(artifact_path)
    
    logger.info("Dropping outliers")
    df = df[df['price'].between(args.min_price, args.max_price)]
    
    logger.info("Converting last_review column to datetime")
    df['last_review'] = pd.to_datetime(df['last_review'])
    
    logger.info("Saving clean sample locally")
    df.to_csv("clean_sample.csv", index=False)
    
    logger.info("Saving artifact to WandB")
    artifact = wandb.Artifact(
        args.output_artifact,
        type=args.output_type,
        description=args.output_description,
    )
    artifact.add_file("clean_sample.csv")
    run.log_artifact(artifact)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="A very basic data cleaning")


    parser.add_argument(
        "--input_artifact", 
        type=str,
        help="Name for the input artifact",
        required=True
    )

    parser.add_argument(
        "--output_artifact", 
        type=str,
        help="Name for the output artifact",
        required=True
    )

    parser.add_argument(
        "--output_type", 
        type=str,
        help="Type of the output artifact",
        required=True
    )

    parser.add_argument(
        "--output_description", 
        type=str,
        help="Description of the output artifact",
        required=True
    )

    parser.add_argument(
        "--min_price", 
        type=float,
        help="Minimum price when cleaning outliers",
        required=True
    )

    parser.add_argument(
        "--max_price", 
        type=float,
        help="Maximum price when cleaning outliers",
        required=True
    )


    args = parser.parse_args()

    go(args)
