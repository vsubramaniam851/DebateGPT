# DebateGPT: Fine-tuning Large Language Models with Multi-agent Debate Supervision

### [Project Page](https://composable-models.github.io/llm_debate/) | [Paper](https://arxiv.org/abs/2305.14325)

[Vighnesh Subramaniam](https://scholar.google.com/citations?user=Or3MAdgAAAAJ&hl=en)
[Antonio Torralba](https://groups.csail.mit.edu/vision/torralbalab/)
[Shuang Li](https://people.csail.mit.edu/lishuang/)

This is the implementation of our paper "DebateGPT: Fine-tuning Large Language Models with Multi-agent Debate Supervision". We will be updating this page with more tasks soon.

## Generating Fine-tuning Data
We generate responses to the 5K instructions from the Alpaca dataset. The instructions are given in the `data/` directory. To generate the multi-agent debate responses, first open `generate_data.py` and set your OpenAI key. Then run the file:
	`python generate_data.py`

This generates debate responses for the 5K data according to the methods described in our paper and saves the outputs into a `.jsonl` file for fine-tuning under the `ft_data` directory. We plan to release debate responses to this data at a later time. 

## Fine-tuning GPT-3.5
To fine-tune GPT-3.5, open `finetuning.py` and set your OpenAI key. Then run:
	`python finetuning.py`

The file automatically saves your finetuning results to a csv file under `ft_data` and appends the fine-tuned model name to a text file under `ft_data/model_names.txt`. This model name is important for running inference. 

## Evaluation
We include evaluate the model on 6 separate tasks in the paper. The code for running each evaluation is found in the following subfolders

* ./alpaca-eval/ contains code for running AlpacaEval
* ./arithmetic/ contains code for running Arithmetic
* ./gsm/ contains code for running GSM
* ./mmlu/ contains code for running MMLU
* ./arc/ contains code for the AI2 Reasoning Challenge (ARC)
* ./winogrande/ contains code for running Winogrande

**AlpacaEval**

To generate answers for AlpacaEval, cd into the `alpaca-eval` directory and open `alpaca-leaderboard.py`. Set your OpenAI key and fine-tuned model name. Then run
	`python alpaca-leaderboard.py --out [OUTFILE]`

Then run the alpaca_eval package code given [here](https://github.com/tatsu-lab/alpaca_eval)

**Arithmetic**

To generate answers for arithmetic, cd into the `arithmetic` directory and open `gen_math.py`. Set your OpenAI key and fine-tuned model name. Then run
	`python gen_math.py`

**Grade School Math**
First, cd into the `gsm`` directory and download the GSM dataset [here](https://github.com/openai/grade-school-math)

To generate answers for the Grade School Math problems, open `gen_gsm.py` and set your OpenAI key and fine-tuned model name. Then run
	`python gen_gsm.py --save_name [SAVE_NAME]`

To evaluate the generated results of the Grade School Math problems:
	`python eval_gsm.py --save_name [SAVE_NAME]`

The scripts can optionally take a `--save_name` flag giving a path indicating where the desired results are.

**MMLU**
First, cd into the `mmlu` directory and download the MMLU dataset [here](https://github.com/hendrycks/test)

To generate answers for MMLU, open `gen_mmlu.py` and set your OpenAI key and fine-tuned model name. Then run
	`python gen_mmlu.py --save_name [SAVE_NAME]`

To evaluate the generated results:
	`python eval_mmlu.py --save_name [SAVE_NAME]`

The scripts can optionally take a `--save_name` flag giving a path indicating where the desired results are.

**ARC**
First, cd into the `arc` directory and download the ARC dataset [here](https://allenai.org/data/arc)

To generate answers for ARC, open `gen_arc.py` and set your OpenAI key and fine-tuned model name. Then run
	`python gen_arc.py --save_name [SAVE_NAME]`

To evaluate the generated results:
	`python eval_arc.py --save_name [SAVE_NAME]`

The scripts can optionally take a `--save_name` flag giving a path indicating where the desired results are.

**Winogrande**
First, cd into the `winogrande` directory and download the Winogrande dataset [here](https://winogrande.allenai.org/)

To generate answers for Winogrande, open `gen_winogrande.py` and set your OpenAI key and fine-tuned model name. Then run
	`python gen_winogrande.py --save_name [SAVE_NAME]`

To evaluate the generated results:
	`python eval_winogrande.py --save_name [SAVE_NAME]`

The scripts can optionally take a `--save_name` flag giving a path indicating where the desired results are.


If you would like to cite the paper, here is a bibtex file:
```
@article{subramaniam2023debategpt,
  title={DebateGPT: Fine-tuning Large Language Models with Multi-agent Debate Supervision},
  author={Subramaniam, Vighnesh and Torralba, Antonio and Li, Shuang},
  journal={arXiv preprint },
  year={2023}
}
```
