I'm setting up this paper, and I need suggestions on how to plan the second part (the asymmetric game). In particular I was thinking about the core requirements. For sure one is that the game must be playable text-only (maybe with the help of tools), that it must not involve any real-time capacity, that it should be asymmetric so it must not be solvable from only one side, that it must require the agents in the 2 roles to go and talk back and forth, 

# RQ
Do LLMs have issues speaing to each other? As we're going toward agent swarms, with possibly heterogeneous agent families, are LLMs able to communicate with each other effectively?

## Methodology
We try to detect this effect of "communication deterioration" by putting a homogeneous swarm of agents (e.g. 3 Qwen models) in a cooperative task and measure their effectiveness. Then repeat the experiment with a heterogeneous swarm of agents (e.g. 2 Qwen models and 1 Gemma). Measure the average "drop" in accuracy (if any) and say that this is the amount of loss derived from "communication issues" between different families of models

## Datasets
I want to use 2 datasets:
- **CooperBench**: a recent benchmark on LLM cooperation. 2 agents have to implement a PR each on a github repo. The PRs are kinda complex, but the interesting finding of the original paper is that a single agent handling both tasks performs always better than 2 agents dividing the work. This is also because the only kind of "cooperation" actually required to solve the tasks is just avoiding interfering with the other PRs (the benchmark has only destructive interference -- not constructive interference).
- **a new asymmetric bench**: This is a new one that I'd have to build first. This new one is an asymmetric game. The agents are required to solve puzzles and quizzes, but the interesting part is that one agent is the "driver" i.e. the only one that can interact, "see", and "explore" the quiz world, while the others are the "experts", who are the only ones with access to the knowledge, tools etc... required to solve the quizzes. In practice one doesn't have access to the solutions, while the others have access to the solution but don't know which is the question. In this new game the agents are required to cooperate, otherwise they can't win

