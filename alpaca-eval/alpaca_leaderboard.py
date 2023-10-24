import os, sys
import numpy as np
import pandas as pd
import time
import json
import openai
import datasets
import argparse
from tqdm import tqdm

openai_key = None #TODO: Fill this in.
openai.api_key = openai_key

def generate_answer(answer_context, model = "gpt3.5-06"):
    if model == "gpt3.5-06":
        model_str = "gpt-3.5-turbo-0613"
    elif model == "ft-gpt3.5":
        model_str = None #TODO: Fill this in!
    else:
        model_str = "gpt-4-0613"
    try:
        completion = openai.ChatCompletion.create(
                  model=model_str,
                  messages=answer_context,
                  n=1)
    except:
        print("retrying due to an error......")
        time.sleep(20)
        return generate_answer(answer_context)
    return completion

def construct_assistant_message(completion):
    content = completion["choices"][0]["message"]["content"]
    return {"role": "assistant", "content": content}

def post_json(json_data):
    model_outputs = []
    for prompt in json_data:
        new_prompt = prompt
        response_dict = {"instruction": new_prompt}
        full_output = json_data[prompt][0]
        response = full_output[-1]["content"] ##First agent, final response (after debate)
        response_dict["output"] = response
        model_outputs.append(response_dict)
    return model_outputs

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", action = "store", default = "ft-gpt3.5", choices = ["gpt4", "ft-gpt3.5", "gpt3.5-06"])
    parser.add_argument("--filename", action = "store", default = "debategpt-alpaca-eval")
    args = parser.parse_args()
    eval_set = datasets.load_dataset("tatsu-lab/alpaca_eval", "alpaca_eval")["eval"]
    response_dict = {}
    print(len(eval_set))
    for example in eval_set:
        instruction = example["instruction"]
        agent_context = [[{"role": "user", "content": instruction}]]
        completion = generate_answer(agent_context[0], args.model)
        print(completion)
        agent_context[0].append(construct_assistant_message(completion))
        response_dict[instruction] = agent_context
    formatted_responses = post_json(response_dict)
    if not os.path.exists("leaderboard_eval"):
        os.makedirs("leaderboard_eval")
    with open(f"leaderboard_eval/{args.filename}.json", "w") as f:
        json.dump(formatted_responses, f)
