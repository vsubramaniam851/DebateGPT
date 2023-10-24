import openai
import json
import numpy as np
from tqdm import tqdm
import argparse
import time

openai_key = None #TODO: Fill this in!
openai.api_key = openai_key

def construct_assistant_message(completion):
    content = completion["choices"][0]["message"]["content"]
    return {"role": "assistant", "content": content}

def read_jsonl(path: str):
    with open(path) as fh:
        return [json.loads(line) for line in fh.readlines() if line]

def generate_answer(answer_context, model = "gpt3.5", temperature = 1):
    if model == "gpt3.5":
        model_str = "gpt-3.5-turbo-0301"
    elif model == "gpt3.5-06":
        model_str = "gpt-3.5-turbo-0613"
    elif model == "ft-gpt3.5":
        model_str = None #TODO: Fill this in!
    else:
        model_str = "gpt-4-0613"
    try:
        completion = openai.ChatCompletion.create(
                  model=model_str,
                  messages=answer_context,
                  temperature = temperature,
                  n=1)
    except:
        print("retrying due to an error......")
        time.sleep(20)
        return generate_answer(answer_context)
    return completion

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", action = "store", default = "ft-gpt3.5", type = str, choices = ["gpt3.5", "gpt4", "ft-gpt3.5", "gpt3.5-06"])
    parser.add_argument("--temperature", action = "store", type = float, dest = "temperature", default = 1)
    parser.add_argument("--save_name", action = "store", default = "debategpt", type = str)
    parser.add_argument("--fewshot", action = "store_true", dest = "fewshot")
    parser.set_defaults(fewshot = False)    
    args = parser.parse_args()
    generated_description = {}

    questions = read_jsonl("/storage/vsub851/llm-debate-summarize-ft/gsm/grade-school-math/grade_school_math/data/test.jsonl")
    if args.fewshot:
        with open("gsm-fewshot.txt", "r") as f:
            few_shot_prompt = f.read()
        system_prompt = {
            "role": "system",
            "content": few_shot_prompt
        }

    for data in tqdm(questions):
        question = data["question"]
        answer = data["answer"]
        if args.fewshot:
            agent_contexts = [[system_prompt, {"role": "user", "content": """Can you solve the following math problem? {} Explain your reasoning. Your final answer should be a single numerical number, in the form \\boxed{{answer}}, at the end of your response.""".format(question)}] for agent in range(1)]
        else:
            agent_contexts = [[{"role": "user", "content": """Can you solve the following math problem? {} Explain your reasoning. Your final answer should be a single numerical number, in the form \\boxed{{answer}}, at the end of your response.""".format(question)}] for agent in range(1)]
        for i, agent_context in enumerate(agent_contexts):
            completion = generate_answer(agent_context, model = args.model, temperature= args.temperature)
            print(completion)

            assistant_message = construct_assistant_message(completion)
            agent_context.append(assistant_message)

    generated_description[question] = (agent_contexts, answer)

    json.dump(generated_description, open("{}_full-gsm.json".format(args.save_name), "w"))