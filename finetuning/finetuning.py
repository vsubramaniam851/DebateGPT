import os, sys
import numpy as np
import pandas as pd
import time
import openai
import argparse

api_key = None #TODO: Fill this in!
openai.api_key = api_key 

def gpt_ft(train_data, epochs, suffix, model = "gpt-3.5-turbo-0613"):
    print("GPT-3.5 Finetuning")
    print(f"Creating training file {train_data}")
    time.sleep(10) #Wait 10 seconds just to be sure training file is correct
    train_response = openai.File.create(
        file = open(train_data, "rb"),
        purpose = "fine-tune"
    )
    train_id = train_response["id"]
    openai.File.wait_for_processing(id = train_id)

    print("Start finetuning job")
    ft_job = openai.FineTuningJob.create(
        training_file = train_id,
        model = model,
        suffix = suffix,
        hyperparameters = {
            "n_epochs": epochs
        }
    )

    job_id = ft_job["id"]
    response = openai.FineTuningJob.retrieve(job_id)
    while response["status"] != "succeeded":
        response = openai.FineTuningJob.retrieve(job_id)
        continue
    print("Finetuning finished!")

    response = openai.FineTuningJob.list_events(id = job_id, limit = 50)
    events = response["data"]
    events.reverse()
    for event in events:
        print(event["message"])

    response = openai.FineTuningJob.retrieve(job_id)
    finetuned_model_id = response["fine_tuned_model"]
    result_files_id = response["result_files"][0]
    return finetuned_model_id, result_files_id

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--epochs", action = "store", type = int, dest = "epochs", default = 4)
    parser.add_argument("--train_file", action = "store", type = str, dest = "train_file", default = "alpaca-ft-train")
    parser.add_argument("--model_name", action = "store", type = str, dest = "model_name", default = "debategpt")
    parser.add_argument("--model", action = "store", type = str, dest = "model", default = "gpt-3.5-turbo-0613")
    parser.add_argument("--save_name", action = "store", type = str, dest = "save_name", default = "finetuning_results")
    args = parser.parse_args()
    train_data = os.path.join("ft_data", f"{args.train_file}.jsonl")
    assert os.path.exists(train_data)

    model_id, result_files_id = gpt_ft(train_data, args.epochs, args.model_name, args.model)
    print("MODEL ID:", model_id)
    with open("ft_data/model_names.txt", "a") as f:
        f.write(f"{model_id}\n")
    print("FILE RESULTS ID:", result_files_id)
    os.system(f"curl https://api.openai.com/v1/files/{result_files_id}/content -H \"Authorization: Bearer {api_key}\" > ft_data/{args.save_name}.csv")