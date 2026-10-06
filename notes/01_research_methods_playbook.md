# Research Methods Playbook: How Top AI / Robotics / OR Papers Are Structured, Run and Reported

Purpose: a concrete, replicable recipe for writing a simulation-based paper on a lunar surface logistics marketplace (a discrete-event, agent-based testbed plus a market mechanism). Everything below is extracted from primary sources read on 2026-10-05 and listed in the References section. Where a source practice is weak (e.g., no confidence intervals), the gap is noted and the stronger rule from the methods literature is adopted instead.

Sources studied in depth: Reflexion (Shinn et al., arXiv 2303.11366v4), Recursive Agent Optimization / RAO (Gandhi, Chakraborty, Wang, Kumar, Neubig, arXiv 2605.06639v2), ReAct (Yao et al., ICLR 2023, arXiv 2210.03629v3), the NeurIPS Paper Checklist, the ODD protocol second update (Grimm et al. 2020, JASSS 23(2)7), the STRESS guidelines (Monks et al. 2019, J. Simulation 13(1)) and their worked application (Taylor et al., WSC 2018), the reproducibility study of open DES models (Heather et al. 2025, arXiv 2501.13137), the Pineau ML Reproducibility Checklist v2.0 and the NeurIPS 2018 "Reproducible, Reusable, and Robust RL" slides, and Lipton and Steinhardt, "Troubling Trends in Machine Learning Scholarship" (2018).

---

## A. Section-by-section anatomy of the two arXiv papers

### A.1 Reflexion: Language Agents with Verbal Reinforcement Learning (arXiv 2303.11366v4)

Total length: roughly 9 pages of main text plus about 3,000 words of appendix. Section order and content:

| # | Section | Approx. length | What it contains |
|---|---------|----------------|------------------|
| - | Abstract | ~200 words | Problem (LLM agents cannot learn from trial-and-error without fine-tuning), one-sentence mechanism ("converts binary or scalar feedback from the environment into verbal feedback"), headline number ("91% pass@1 accuracy on the HumanEval coding benchmark, surpassing the previous state-of-the-art GPT-4 that achieves 80%"). |
| 1 | Introduction | ~1,200 words | Opens with recent agent work (ReAct, SayCan). States the gap: prior methods rely on in-context examples and cannot improve across trials. Proposes the method, contrasts with classical RL (lightweight, no fine-tuning, interpretable). Names the three test domains. Ends with 4 contribution bullets (quoted in Section E below). |
| 2 | Related work | ~800 words + 2 tables | Two comparison tables positioning Reflexion against Self-Refine, CoT, ReAct, etc. on feature axes (self-refinement, hidden constraints, decision making, binary reward, memory). Tables, not prose, carry the positioning. |
| 3 | Method ("Reflexion: reinforcement via verbal reflection") | ~1,500 words | Subsections: Actor, Evaluator, Self-reflection, Memory, The Reflexion process. Each is 1-2 paragraphs with a role definition. Figure 2(a) is a modular block diagram (Actor -> Environment -> Evaluator -> Self-Reflection -> Memory -> Actor); Figure 2(b) is Algorithm 1. |
| 4 | Experiments | ~4,000 words | 4.1 Sequential decision making: ALFWorld; 4.2 Reasoning: HotpotQA; 4.3 Programming. Each subsection has an identical internal pattern: setup paragraph -> Results paragraph -> Analysis paragraph (and an Ablation study for 4.3). |
| 5 | Limitations | ~300 words | Local minima in policy optimization; memory bounded to 1-3 experiences; limits of test-driven development (non-deterministic generators, impure functions, hardware-dependent output, concurrency). |
| 6 | Broader impact | ~250 words | Dual framing: automation benefit vs. misuse; argues self-reflections are inspectable. |
| 7 | Conclusion | ~200 words | Restates method and gains, points to future work (vector-database memory, richer evaluators). |
| 8 | Reproducibility | ~50 words | Pointer to code and prompts. |
| - | References | ~80 entries | |
| A-D | Appendices | ~3,000 words | Additional model evaluations (weaker LLMs), a WebShop failure case study, full prompts, worked trajectories. |

Formalization. Notation is introduced inline, not in a separate section: policy `pi_theta(a_i | s_i)`; trajectory `tau_t = [a_0, o_0, ..., a_i, o_i]`; three models `M_a` (Actor), `M_e` (Evaluator), `M_sr` (Self-Reflection); episodic memory `mem`; self-reflection string `sr_t`; scalar reward `r_t = M_e(tau_t)`. The only "equation" of substance is the re-parameterization `theta = {M_a, mem}`: the policy is the frozen LLM plus the memory buffer. Algorithm 1 is a standard boxed pseudocode: initialize models and buffers; generate initial trajectory; evaluate; loop until success or `max_trials`: generate `tau_t` with `pi_theta`, evaluate with `M_e`, reflect with `M_sr`, append `sr_t` to `mem`, increment `t`.

Figures and tables. Learning curves dominate: Figure 3a (ALFWorld proportion of solved tasks vs. trial, 12 trials), Figure 4a-c (HotpotQA, 14 trials, including an ablation curve with episodic memory only vs. memory + self-reflection). Figure 3b is a failure-category breakdown (hallucination vs. inefficient planning) per trial. Tables: Table 1 (pass@1 for every model x strategy x language x benchmark), Table 2 (test-generation quality: TP/FN/FP/TN rates), Table 3 (ablation on 50 hard LeetCode problems). Comparison tables in Related Work.

Hedging. The paper is assertive in results but qualifies the mechanism: "At its core, Reflexion is an optimization technique that uses natural language to do policy optimization"; acknowledges it relies on "the power of the LLM's self-evaluation capabilities (or heuristics) and not having a formal guarantee for success." A dedicated negative case (WebShop, Appendix B.1) states "Reflexion is unable to solve tasks that require a significant amount of diversity and exploration."

Weaknesses to avoid replicating: no seeds or confidence intervals reported; no token/cost accounting; single-run learning curves.

### A.2 Recursive Agent Optimization / RAO (arXiv 2605.06639v2, dated 2026-10-02)

Total: ~11,000 words main text, ~8,000 words appendix. Section order:

| # | Section | Approx. length | What it contains |
|---|---------|----------------|------------------|
| - | Abstract | ~250 words | Defines recursive agents (spawn sub-tasks to copies of themselves); states RAO trains *when* and *how* to delegate; lists four benefits with one number ("up to 2.5x" wall-clock speedup). |
| 1 | Introduction | ~1,500 words | Problem: longer horizons and working-memory demands; divide-and-conquer suits software engineering, research, document processing. Gap: existing recursive/multi-agent systems are inference-time scaffolds around pretrained models, never trained to decide when delegation helps. Two explicit research questions in italics: "How should we train a model to exploit recursive inference effectively?" and "How can we leverage the recursive structure of inference to better train agents?" Contributions stated as a narrative paragraph, not bullets. |
| 2 | Recursive Agents: Inference and Training | ~2,500 words | 2.1 Recursive Agent Inference (execution tree definition). 2.2 RAO: 2.2.1 Local Node Reward (Eq. 1), 2.2.2 Policy Optimization Objective (Eqs. 2-5). No algorithm box; equations are interleaved with prose explaining each term. |
| 3 | Experiments | ~3,000 words | One subsection per environment: 3.1 TextCraft-Synth (synthetic, controlled difficulty), 3.2 Oolong-Real (real long-context), 3.3 DeepDive (real deep research). Each gives task definition, action space (full tables in Appendix A.4), train/test split, context limits, metrics. |
| 4 | Discussion of Experimental Results | ~1,500 words | Organized by *claim*, with a bold run-in heading per claim: recursive agents generalize to harder tasks; solve tasks beyond the context window; reduce wall-clock time; learn when/how much to delegate. Each claim paragraph cites one table or figure. |
| 5 | Ablation Experiments | ~700 words | 5.0.1 Reward density x trajectory weighting (2x2); 5.0.2 Delegation bonus design (success rate vs. success count, exposing a reward-hacking failure). |
| 6 | Related Work | ~1,200 words | Placed *after* experiments. |
| 7 | Conclusion | ~800 words | Restates findings; a long list of open directions (compute-aware evaluation, heterogeneous recursion, surrogate sampling). Doubles as the limitations discussion. |
| A.1-A.9 | Appendices | ~8,000 words | A.1 Additional baselines (pass@k/best@k oracle, Chain-of-Agents); A.2 "When does RAO work best?" (negative/neutral result on easy tasks); A.3 Unbiased baseline lemma + proof; A.4 Action-space tables; A.5 Hyperparameters; A.6 Token usage tables; A.7-A.9 full prompts. |

Formalization. A notation block is built up in 2.1-2.2: policy `pi_theta`; task spec `X`; trajectory `tau_X`; execution tree `T`; children `C(X)`; depth-d subtask distribution `D_d(theta)`; maximum depth `D`; success signal `s~(X, tau_X) in [0,1]`. Five numbered equations:

- Eq. 1 local node reward: `R(X, tau_X) = s~(X, tau_X) + lambda * (1/|C(X)|) * sum_{c in C(X)} s~(c, tau_c)` (own success plus a delegation bonus equal to mean child success).
- Eq. 2 objective averaged uniformly over depths: `J(theta) = (1/(D+1)) sum_{d=0}^{D} E_{X ~ D_d(theta)} E_{tau_X ~ pi_theta} [R(X, tau_X)]`.
- Eq. 3 leave-one-out advantage: `A(tau^(g)) = R(tau^(g)) - b_{-g}`, with `b_{-g}` the mean root reward of the other G-1 rollouts.
- Eq. 4 inverse-frequency depth weight: `w_d = N / ((D+1) N_d)`.
- Eq. 5 the resulting gradient estimator.

Each equation is followed by one sentence saying what each term does and why it is there. Figure 1 is a concrete worked example (travel-planning execution tree) rather than an abstract block diagram.

Figures and tables. Tables 1-3 are the main results, one per environment, with rows stratified by difficulty (Easy/Medium/Hard) or input length (55K/118K/175K tokens) and columns for success rate or reward, steps, and wall-clock seconds. Figures 4-6 are training curves (moving average, window 10, stated in the caption). Figure 7 is a histogram of maximum delegation depth per difficulty, used as *mechanistic evidence* that the agent learned difficulty-appropriate behavior. Figures 8-9 are ablation curves. Appendix Tables 9-11 give input/output/cache-read/total tokens per difficulty bucket.

Hedging. Mechanistic claims are explicitly flagged as hypotheses: "We hypothesize that this stronger test-time scaling comes from teaching the model a divide-and-conquer strategy that naturally transfers to harder problems." Aggregate conclusions use "suggest": "Together, these results suggest that RAO is effective at training agents to exploit recursive execution across diverse task structures." The appendix states the boundary condition plainly: "RAO helps the most when tasks are either difficult enough to benefit from divide-and-conquer and/or long-horizon enough to require extended context windows."

Weaknesses to avoid replicating: no error bars or seed counts stated; limitations folded into the conclusion rather than a dedicated section.

### A.3 ReAct (arXiv 2210.03629v3) as a third reference point

Sections: Abstract; 1 Introduction (ends with a four-item numbered contribution sentence); 2 ReAct method (~1,500 words, defines augmented action space `A^ = A U L`, "An action a^_t in L ... which we will refer to as a thought or a reasoning trace, does not affect the external environment, thus leading to no observation feedback"); 3 Knowledge-intensive reasoning tasks (HotpotQA, FEVER); 4 Decision-making tasks (ALFWorld, WebShop); 5 Related work; 6 Conclusion; Ethics statement; Appendices A-E (additional results, prompts, trajectories, failure examples). Experiments are organized by *task family*, with Setup / Methods / Results / Analysis blocks inside each.

Notable practices: (a) a hand-labeled error taxonomy with counts: 50 correct and 50 incorrect trajectories sampled per method (200 total), categorized into True positive, False positive (hallucinated trace), Reasoning error, Search result error, Hallucination, Label ambiguity, with percentages per method (Table 2); (b) prompt-robustness trials: "we construct 6 prompts for each task type through each permutation of 2 annotated trajectories from the 3 we annotate", then report best, worst, and average across the "six controlled trials, with relative performance gain ranging from 33% to 90% and averaging 62%"; (c) a scaling analysis across PaLM-8B/62B/540B with and without fine-tuning (Figure 3).

---

## B. Experimental design rules extracted

Rules below are what the three agent papers actually do, upgraded where the methods sources (NeurIPS checklist, Pineau, Lipton and Steinhardt, STRESS) demand more.

### B.1 Baselines

1. Use at least three kinds of baseline:
   - Naive / status quo (ReAct's "Standard" and "Act"; Reflexion's plain ReAct and CoT; RAO's single-agent trained with identical compute). For a logistics marketplace: first-come-first-served dispatch, greedy nearest-vehicle assignment, fixed-price allocation.
   - Strongest prior method re-implemented under identical conditions (RAO re-runs Chain-of-Agents; Reflexion compares to CodeT, Self-Debugging, CodeRL).
   - Oracle / upper bound (RAO reports pass@k and best@k with an oracle ranker for k in {1,5,10,15,20,25}; ReAct reports expert-human WebShop performance; Reflexion reports CoT with ground-truth context "CoT (GT)"). For a marketplace: a centralized omniscient optimizer with full information and no communication delay, and an offline MILP solved with hindsight.
2. Baselines must receive the same tuning effort as the proposed method. Pineau's NeurIPS 2018 audit found that only 20% of surveyed deep-RL papers provided hyperparameters for baselines versus 55% for the proposed algorithm; two runs of the *same* TRPO code with different hyperparameters appeared to be different algorithms. State the baseline tuning budget explicitly.
3. Report best, worst and mean across controlled trials for both method and baselines (ReAct: "even the worse ReAct trial (48%) beats the best trial of both methods").

### B.2 Benchmarks / scenarios

1. Mix one synthetic, fully controlled environment with difficulty knobs (RAO's TextCraft-Synth with Easy 2-3 / Medium 4-6 / Hard 7-9 crafting depth) and at least one "real" or externally sourced scenario (RAO's Oolong-Real and DeepDive; Reflexion's HumanEval, MBPP, and a newly built LeetcodeHardGym).
2. Contribute a benchmark artifact if none exists (Reflexion's LeetcodeHardGym is listed as a contribution). For lunar logistics: a scenario suite with named instances (e.g., base-camp resupply, ISRU plant feed, multi-site science campaign) and difficulty levels defined by a scalar knob (demand rate, fleet size, communication blackout fraction, terrain delay variance).
3. Define difficulty by a measurable structural property, not by intuition (RAO: recursion depth required; ReAct/ALFWorld: six task types).

### B.3 Metrics

1. One primary metric per claim, defined in a sentence before use (STRESS 1.2: define every output and how it is calculated). RAO: success rate, average reward with partial credit, environment steps "computed on the intersection of tasks solved by both methods", wall-clock seconds, tokens. ReAct: EM, accuracy, success rate, average attribute-coverage score. Reflexion: pass@1, cumulative proportion solved per trial.
2. Always pair an outcome metric with a cost metric (RAO reports steps and seconds alongside success rate; token tables in Appendix A.6 show recursive agents use 5.2x *fewer* tokens on one task and 21x-29x *more* on others, and the paper says so).
3. For marketplaces: primary = fraction of demands served on time (or total delivered mass-km per sol); secondary = allocative efficiency relative to the oracle optimum, price dispersion, fairness (Gini of supplier utilization), robustness under blackout, and computation time per clearing round.

### B.4 Seeds, trials, uncertainty

1. The three agent papers are weak here (no CIs; single runs or best-of-6 prompts). Do not copy that. Follow the NeurIPS checklist item 7 and Pineau: report "the exact number of training and evaluation runs", "a description of results with central tendency (e.g. mean) & variation (e.g. error bars)", state what the error bars capture (seed variance vs. scenario variance), and how they were computed (standard deviation, standard error, or bootstrap CI; state the normality assumption if used).
2. Pineau's "Consider the case of n=10" slide shows that reporting the top-3 of 10 seeds creates a "strong positive bias: seems to beat the baseline!" and makes "variance appear much smaller". Report all seeds; never cherry-pick.
3. Rule of thumb for a stochastic DES: at least 10 independent replications per scenario x method cell, 30 where the primary metric's coefficient of variation exceeds 0.2; report mean +- 95% CI (t-based or 1,000-sample bootstrap) and the number of replications in every table caption. Use common random numbers across methods within a replication where possible (STRESS 5.2, 4.3).
4. State the random-number generator, seed list, and seed-to-stream mapping (STRESS 5.2). Heather et al. 2025 found random sampling and seed documentation among the most frequently incomplete STRESS items and a direct barrier to reproduction.

### B.5 Learning curves and time-series plots

1. Reflexion and RAO both show performance versus trial/training step. Caption states the smoothing (RAO: "moving average, window size 10"). Plot the full set of runs or mean with shaded CI band; label the baseline as a flat reference line.
2. For a marketplace simulator the analogue is: performance vs. simulated sol; price convergence vs. clearing round; cumulative served demand vs. time under a disruption, annotated at the disruption onset.

### B.6 Ablation design

1. Remove one component at a time, keep everything else fixed, report the full model and every single-removal variant in one table (Reflexion Table 3: full 68%; without test generation 52%; without self-reflection 60%; baseline 60%).
2. Where two components may interact, run the 2x2 (RAO Figure 8: dense vs. sparse reward x weighted vs. unweighted).
3. Include at least one ablation that *replaces a design choice with the obvious alternative* and shows why the alternative fails (RAO Figure 9: success-count bonus induces reward hacking; agent spawns more sub-agents and runs longer).
4. Lipton and Steinhardt: raw numbers have "limited value for scientific progress absent insight into what drives them"; the remedies are "error analysis, ablation studies, and robustness checks (to e.g. choice of hyper-parameters, as well as ideally to choice of dataset)". Plan the ablation table before running the main experiment.

### B.7 Stratified analysis

1. Break every main result down by difficulty bucket or input size (RAO Table 1 by Easy/Medium/Hard; Table 2 by 55K/118K/175K tokens; ReAct Table 3 by ALFWorld task type).
2. Add a mechanistic plot showing the method's internal behavior changes with difficulty (RAO Figure 7: distribution of maximum delegation depth per difficulty; Reflexion Figure 3b: failure categories per trial).

### B.8 Generalization tests

1. Train / tune on the middle of the difficulty range, test on both ends (RAO: "All Textcraft-Synth runs are trained only on medium-difficulty problems", then hard-task success 88% vs. 20%). Train on short inputs (<60K tokens), test on 175K.
2. Transfer to a different domain or language (Reflexion: Python -> Rust via MultiPL-E; evaluation on weaker LLMs in Appendix A, including a null result for StarChat-Beta).
3. For a marketplace: tune mechanism parameters on nominal demand, then test on surge demand, on blackout schedules not seen in tuning, and on a fleet composition change.

### B.9 Cost and compute reporting

1. NeurIPS checklist item 8: "type of compute workers, memory, time of execution", compute per run and total, including unreported preliminary experiments. Pineau: "average runtime for each result, or estimated energy cost" and "computing infrastructure used". STRESS 5.4: model run time and hardware.
2. RAO's Appendix A.6 token tables are the model: one row per difficulty bucket, columns for each cost component, both methods side by side.

### B.10 Failure analysis with concrete examples

1. Build a small hand-labeled taxonomy with counts (ReAct Table 2: 200 trajectories, six categories, percentages per method) and quote at least one representative trajectory per category in an appendix.
2. Report emergent failure modes seen during development, with where they appear in the plots (RAO: "a transient failure mode around training steps 40-80, where the recursive agent briefly learns to print the entire input in the root context, exhausting its context window. It then quickly recovers").
3. Include a scenario where the method does not help and say why (Reflexion WebShop; RAO Appendix A.2 email search where "performance equalizes between the single and recursive agents").

### B.11 Limitations conventions

1. Dedicated section (Reflexion Section 5; NeurIPS item 2 explicitly asks for a separate Limitations section covering "strong assumptions and how robust the results are to violations of these assumptions").
2. Content pattern: (a) assumptions the model makes that the real system violates; (b) conditions under which gains vanish, with evidence; (c) scalability limits with numbers; (d) what was not tested. Avoid vague "future work" filler; each limitation names a specific untested condition.

---

## C. ODD protocol + STRESS-DES condensed into a fillable template

Use this as the structure of the model-description appendix (full ODD, 5-10 pages per Grimm et al.) and as the skeleton for the Section 3 summary ODD in the main text (narrative, italicized ODD keywords, state-variable lists moved to tables, only design concepts essential to the research question).

### C.1 ODD (Grimm et al. 2020, seven numbered elements)

**1. Purpose and patterns**
- Purpose: one paragraph. "The model's purpose is to ... [specific question]."
- Patterns used as evaluation criteria: list 3-6 observed or expected patterns (e.g., queueing of landers at a shared pad under surge, price spikes during blackout, utilization skew toward the nearest supplier). State source: data, literature, or domain expert expectation. These patterns drive entity selection and are checked in validation.

**2. Entities, state variables and scales**
- Entity types: spatial cells / routes, vehicles (rovers, hoppers, landers), depots and ISRU plants, demand sites, market agents (buyers, sellers, auctioneer or clearing house), environment (illumination, comm windows, dust/thermal events).
- Table per entity type: state variable, units, type (static/dynamic), range. Do not list parameters here.
- Temporal resolution (event-driven; reporting granularity in sols) and extent (N sols). Spatial resolution and extent (graph nodes/edges with distances, or grid at X m).

**3. Process overview and scheduling**
- Numbered list of processes in execution order per event type: demand arrival -> bid submission -> market clearing -> task assignment -> routing/travel -> service -> payment/settlement -> state update -> logging.
- State when state variables update (immediately vs. at end of clearing round) and how ties and simultaneous events are ordered (STRESS 5.3).

**4. Design concepts** (omit those that do not apply; add a Rationale sub-paragraph where a choice is non-obvious)
- Basic principles: which theories (mechanism design: VCG / combinatorial auction / posted price; vehicle routing; queueing).
- Emergence: what is expected to emerge rather than be imposed (prices, route congestion, supplier specialization).
- Adaptation: how agents change bids or routes in response to outcomes.
- Objectives: each agent's utility (profit, served-demand fraction, energy budget).
- Learning: whether agents update parameters across rounds (e.g., bid-shading rule).
- Prediction: do agents forecast demand or travel time? With what model?
- Sensing: what each agent observes (own state, public prices, comm-window-delayed information).
- Interaction: direct (bids/awards) vs. mediated (shared pad queues).
- Stochasticity: list every random process and why it is random (demand arrivals, travel-time noise, failures, comm dropouts).
- Collectives: consortia or fleets acting jointly, if any.
- Observation: every output collected, when, and how aggregated (ties to STRESS 1.2).

**5. Initialization**
- Initial fleet positions, inventories, prices, demand backlog; whether initialization is fixed or sampled; seed handling.

**6. Input data**
- External time series or tables driving the model (illumination/comm windows from ephemeris, terrain distances, mass manifests), with sources and preprocessing.

**7. Submodels**
- One subsection per process in element 3: equations or pseudocode, parameters grouped by submodel in a table (symbol, meaning, value, unit, source/justification), and evidence or reasoning behind each.

Grimm et al. also recommend: link ODD sections to code via consistent naming and comments; declare a license for the ODD text; if adapting an existing model, mark re-used material; consider a TRACE document for the full evaluation (calibration, verification, validation) in the supplement.

### C.2 STRESS-DES (Monks et al. 2019; wording via Taylor et al. 2018 and Heather et al. 2025)

Twenty items in six sections. Fill each with one to three sentences or a pointer to the appendix table.

**1. Objectives**
- 1.1 Purpose of the model: background and rationale.
- 1.2 Model outputs: every quantitative performance measure and how it is calculated.
- 1.3 Experimentation aims: the research questions the model was used to answer; list scenarios tested.

**2. Logic**
- 2.1 Base model overview diagram: state chart or process-flow diagram of the base model; keep complicated diagrams out of the main text.
- 2.2 Base model logic: text explaining the diagram including all intermediate calculations.
- 2.3 Scenario logic: logical differences between base case and each scenario (parameter sweeps vs. structural changes).
- 2.4 Algorithms: detail of any algorithm that mimics complex or manual real-world processes (here: the market clearing algorithm, the routing heuristic, the dispatcher).
- 2.5 Components: entities (what flows through the system: cargo lots, demand orders), activities (loading, traversal, unloading, charging), resources (vehicles, pads, power), queues (discipline and capacity at each), entry/exit points (how orders and vehicles are created and destroyed).

**3. Data**
- 3.1 Data sources: all sources (ephemeris, mission manifests, published rover performance), with citations.
- 3.2 Pre-processing: any manipulation or filtering before use.
- 3.3 Input parameters: every parameter, description, value, and distribution with fitted parameters.
- 3.4 Assumptions: where real-system data is unavailable, state and justify assumed values, distributions, and logic.

**4. Experimentation**
- 4.1 Initialization: warm-up period, its length, and how it was selected (e.g., Welch's method or MSER); initial conditions.
- 4.2 Run length: duration and time units (e.g., 90 sols, event-driven).
- 4.3 Estimation approach: deterministic or stochastic; number of replications or batch means; how the number was chosen (CI half-width target); common random numbers.

**5. Implementation**
- 5.1 Software or programming language: OS, language, simulation library, all versions.
- 5.2 Random sampling: RNG algorithm (e.g., PCG64), seeding scheme, stream allocation per process.
- 5.3 Model execution: event scheduling (discrete-event vs. fixed step), tie-breaking and priority rules for simultaneous events.
- 5.4 System specification: hardware, run time per replication and total.

**6. Code access**
- 6.1 Computer model sharing statement: where the model, scenarios, output-processing and figure scripts are available; license; DOI.

Heather et al. 2025 (eight open healthcare DES models) report that technical items (input parameters, initialization, random sampling, execution) were most often incomplete; software versions and system specifications were rarely complete; and the main barriers to reproduction were missing or unclear licenses (half the models initially unlicensed), parameter mismatches between paper and code, missing scenario code (six of seven studies with scenarios), missing output-calculation and figure code, and inadequate dependency documentation. Treat those five as release-blocking checks.

---

## D. Reproducibility checklist for a simulation paper

Merged from the NeurIPS checklist (16 items), Pineau v2.0, IJCAI, STRESS, and ODD. Each line should be answerable Yes / No / N/A with a comment.

Claims and scope
- [ ] Abstract and introduction claims match what the experiments show, including the scenarios where the method does not help (NeurIPS 1).
- [ ] Dedicated Limitations section listing assumptions and their robustness (NeurIPS 2).
- [ ] Any theoretical property of the mechanism (incentive compatibility, budget balance, efficiency bound) stated with full assumptions and proof or proof sketch (NeurIPS 3; IJCAI theory items).

Model description
- [ ] Full ODD in supplement; summary ODD in main text (Grimm 2020).
- [ ] All 20 STRESS-DES items answered (Monks 2019).
- [ ] Every parameter in a table with value, unit, source; parameters grouped by submodel (ODD 7).
- [ ] Clear description of the mathematical setting, algorithm and assumptions (Pineau).

Experimental protocol
- [ ] Exact number of replications per cell, and how chosen (Pineau; STRESS 4.3).
- [ ] Error bars defined (SD vs. SE vs. 95% CI), what variability they capture, how computed (NeurIPS 7).
- [ ] Hyperparameter / mechanism-parameter ranges searched, selection method, final values, for method *and* baselines (Pineau; IJCAI).
- [ ] Warm-up and run length stated with method of selection (STRESS 4.1, 4.2).
- [ ] RNG, seeds, stream allocation, common random numbers (STRESS 5.2).
- [ ] Scenario definitions and difficulty knobs enumerated; generalization split declared before tuning (RAO practice).
- [ ] Ablations: one-at-a-time removals plus any interaction 2x2 (Lipton and Steinhardt; Reflexion; RAO).
- [ ] Failure taxonomy with counts and example traces (ReAct Table 2).

Compute and cost
- [ ] Hardware, OS, library versions (STRESS 5.1, 5.4).
- [ ] Run time per replication, total compute including discarded preliminary runs (NeurIPS 8).
- [ ] Any LLM used in the pipeline is declared with model id, version, temperature, and prompts (NeurIPS 16).

Artifacts
- [ ] Code, scenario files, seeds, output-processing and figure scripts released with a license and DOI (NeurIPS 5; STRESS 6.1; Heather 2025 barriers).
- [ ] README with results table and the exact command per result (Pineau).
- [ ] Dependencies pinned (Pineau; Heather 2025).
- [ ] Third-party data and software cited with licenses (NeurIPS 12).
- [ ] New benchmark/scenario suite documented with a datasheet-style description (NeurIPS 13).

Ethics
- [ ] Broader impacts paragraph that names direct negative uses (e.g., mechanisms that disadvantage small suppliers) without speculating on remote ones (NeurIPS 10).

---

## E. Writing-style notes

### E.1 Introduction paragraph pattern (problem -> gap -> contribution)

All three agent papers follow the same five-paragraph shape:

1. Context: what is now possible and why it matters (RAO: agents face "longer horizons, larger working memory demands"; Reflexion: recent agent frameworks).
2. Specific problem: the concrete failure (Reflexion: agents "cannot learn from trial-and-error without expensive fine-tuning"; RAO: recursion is only an "inference-time scaffold").
3. Gap stated as a question or a sentence beginning with what prior methods do *not* do. RAO uses two italicized research questions.
4. Proposal in one or two sentences with the mechanism in plain words, followed by one headline number.
5. Contributions. Reflexion uses four bullets; ReAct uses one sentence with (1)-(4); RAO uses a narrative paragraph. Bullets are preferred for a 15-20 page paper.

Reflexion's bullets, verbatim, as a template of specificity:
- "We propose Reflexion, a new paradigm for 'verbal' reinforcement that parameterizes a policy as an agent's memory encoding paired with a choice of LLM parameters."
- "We explore this emergent property of self-reflection in LLMs and empirically show that self-reflection is extremely useful to learn complex tasks over a handful of trials."
- "We introduce LeetcodeHardGym, a code-generation RL gym environment consisting of 40 challenging Leetcode questions ('hard-level') in 19 programming languages."
- "We show that Reflexion achieves improvements over strong baselines across several tasks, and achieves state-of-the-art results on various code generation benchmarks."

ReAct's version: "To summarize, our key contributions are the following: (1) we introduce ReAct, a novel prompt-based paradigm ...; (2) we perform extensive experiments across diverse benchmarks ...; (3) we present systematic ablations and analysis ...; (4) we analyze the limitations of ReAct under the prompting setup." Note that the fourth contribution is the limitation analysis itself.

Template for the lunar paper: (1) a testbed/benchmark artifact; (2) a mechanism; (3) an empirical finding with a number; (4) an analysis of when it fails.

### E.2 Stating contributions

- Each bullet starts with a verb: propose, introduce, show, analyze.
- Each bullet carries one concrete noun (a named system, a named benchmark with a size: "40 challenging Leetcode questions ... in 19 programming languages").
- The empirical bullet names the comparison class ("over strong baselines") and the scope ("across several tasks").

### E.3 Describing figures and tables in text

- Lead with the claim, then cite the exhibit as evidence, then say what in the exhibit supports the claim. RAO: "Table 1 shows that while both single-agent and recursive models generalize well to easy tasks, only the recursive agents perform strongly on hard tasks (88% vs. 20% success rate)."
- Explain the trend shape, not just the endpoint. Reflexion: "Figure 3 shows that the learning process occurs over several experiences ... the immediate spike in the improvement between the first two trials, then a steady increase over the next 11 trials to a near-perfect performance."
- Tie the exhibit back to the mechanism section. RAO: "As discussed in Section 2.2, we attribute this to the structured sub-agent rewards that serve a role akin to dense process rewards."
- Use mechanistic exhibits to close the loop. RAO: "Fig. 7 plots the maximum depth reached by successful Textcraft-Synth rollouts ... suggesting that the agent learns difficulty-appropriate delegation behavior."
- Captions state smoothing, replication count, and what the error band is.

### E.4 Phrasing results

Pattern: [Method] [verb] [baseline] by [absolute number] [metric] on [benchmark] [condition].

- ReAct: "ReAct outperforms imitation and reinforcement learning methods by an absolute success rate of 34% and 10% respectively, while being prompted with only one or two in-context examples."
- Reflexion: "Reflexion agents improve on decision-making AlfWorld tasks over strong baseline approaches by an absolute 22% in 12 iterative learning steps, and on reasoning questions in HotPotQA by 20%, and Python programming tasks on HumanEval by as much as 11%."
- Reflexion: "ReAct + Reflexion significantly outperforms ReAct by completing 130 out of 134 tasks."
- RAO: "the recursive agent is 1.8x and 2.5x faster on medium and hard tasks, respectively, despite taking 1.8x and 2.8x more steps."
- ReAct: "even the worse ReAct trial (48%) beats the best trial of both methods."
- RAO on a trade-off: "the single-agent baseline is slightly faster on easy tasks, but ..."

Rules: say "absolute" or "relative" every time; give raw counts when the denominator is small (130 of 134); report the cost side in the same sentence when it cuts against you ("despite taking ... more steps"); when the method loses, say so with the number (ReAct "slightly lags behind CoT on HotpotQA (27.4 vs. 29.4)").

### E.5 Hedging

- Mechanism explanations are labelled: "We hypothesize that ...", "we attribute this to ...", "these results suggest ...".
- Boundary conditions are stated as sentences, not footnotes: "RAO helps the most when tasks are either difficult enough ... and/or long-horizon enough ...".
- Lipton and Steinhardt: separate speculation from technical claims; quarantine informal ideas in a clearly marked paragraph or a "Discussion" subsection; test each explanation with "Would I rely on this explanation for making predictions or for getting a system to work?"

### E.6 Tone, and what to avoid so the text reads as written by a careful human

Do:
- Short declarative sentences for results; longer sentences for setup. Vary length; the papers routinely follow a 30-word setup sentence with a 10-word result sentence.
- Concrete numbers in nearly every results sentence; name the exhibit.
- Verbs: outperforms, improves, achieves, lags, recovers, fails, generalizes. Nouns: success rate, replications, scenario, mechanism.
- One idea per paragraph, with a bold run-in heading in the results discussion (RAO Section 4).
- Define each term once, then reuse the exact term (Lipton and Steinhardt on overloaded terminology: do not call the same thing "market", "exchange" and "auction" interchangeably).

Avoid:
- Hype adjectives and intensifiers: "novel" (beyond one use in contributions), "groundbreaking", "remarkable", "significantly" without a test, "robust" without a robustness experiment.
- Filler transitions: "It is worth noting that", "Importantly,", "Notably," more than once per section; "In this section, we ..." openers.
- Words and tics that mark machine-generated prose: "delve", "leverage" as a verb for "use", "harness", "landscape", "paradigm shift", "crucial", "pivotal", "multifaceted", "tapestry", "underscore", "foster", "seamless", "holistic", "in today's rapidly evolving", triple adjectives, every paragraph ending in a summary sentence, uniform paragraph lengths, bullet lists where prose is expected.
- Suggestive definitions and suitcase words (Lipton and Steinhardt): do not name a component "trust" or "intelligence" when it is a scalar; do not call a heuristic "optimal".
- Mathiness: no equation that is not referenced later and used; no theorem for a setting the experiments do not cover (the Adam convex-case example).
- Unexplained anthropomorphism: agents "decide" under a rule you wrote; say which rule.
- Claims about generality beyond tested scenarios ("dermatologist-level" problem).

---

## F. Proposed paper skeleton (15-20 pages)

Working title shape: "[Name]: A Discrete-Event Agent-Based Testbed and Market Mechanism for Lunar Surface Logistics". Target: a venue accepting simulation + mechanism papers (e.g., Winter Simulation Conference, J. Simulation, AAMAS, or an arXiv preprint written to NeurIPS checklist standards).

| # | Section | Pages | Method source | Content |
|---|---------|-------|---------------|---------|
| 0 | Abstract | 0.3 | Reflexion / RAO abstracts | Problem, testbed in one sentence, mechanism in one sentence, headline number (e.g., "+X absolute points of on-time delivery over greedy dispatch at equal fleet size, within Y% of an omniscient optimizer"), artifact release. |
| 1 | Introduction | 1.5 | E.1 pattern | Context (planned lunar surface activity, multi-operator fleets). Problem (no shared testbed, allocation by fixed contracts). Gap as two research questions. Proposal. Four contribution bullets: testbed + scenario suite, mechanism, empirical finding, failure analysis. |
| 2 | Background and related work | 1.5 | Reflexion Related Work tables | Three strands: lunar logistics studies, agent-based/DES logistics simulators, market mechanisms for transport/resource allocation. One comparison table (Table 1) positioning the testbed on axes (open code, stochastic, multi-operator, market layer, comm delay, disruptions). |
| 3 | Problem formulation | 1.5 | RAO Section 2 style | Notation block: sites `S`, vehicles `V`, orders `O` with release time, deadline, mass, origin/destination; travel-time distribution; communication windows; agent utilities; social objective. Equations: objective (1), feasibility constraints (2), mechanism allocation rule and payment rule (3-4). One worked example figure like RAO Figure 1. |
| 4 | The testbed (summary ODD) | 2.5 | ODD 1-7, STRESS 2.x, 5.3 | Narrative ODD with italic keywords; entity/state-variable table (Table 2); process/scheduling list; design concepts that matter (stochasticity, sensing under comm delay, observation); architecture figure; scenario suite with difficulty knobs (Table 3). Full ODD and STRESS tables in Appendix A/B. |
| 5 | Market mechanism | 1.5 | Reflexion Section 3 modularity | Components (bidding, clearing, settlement, re-planning), Algorithm 1 box, properties stated with assumptions and proofs in Appendix C. |
| 6 | Experimental setup | 1.5 | B.1-B.4, B.9 | Baselines (FCFS, greedy nearest, fixed-price contract, offline MILP oracle, omniscient online oracle); metrics with definitions; replications and CI method; warm-up and run length; parameter table; tuning protocol for all methods; hardware and run time. |
| 7 | Results | 4 | RAO Section 4 claim-per-heading | 7.1 Main comparison (Table 4, Figure 4). 7.2 Stratified by difficulty knob (Figure 5). 7.3 Generalization: tuned on nominal, tested on surge/blackout (Figure 6). 7.4 Mechanistic evidence: price and utilization dynamics (Figure 7). 7.5 Cost: computation time and messages per round (Table 5). |
| 8 | Ablations | 1.5 | B.6 | One-at-a-time removals (Table 6) and one 2x2 interaction (Figure 8); one "obvious alternative" that fails (e.g., pay-as-bid vs. uniform price showing bid shading). |
| 9 | Failure analysis | 1 | ReAct Table 2, RAO failure modes | Hand-labelled taxonomy over N failed orders with counts; two example traces; one scenario where the mechanism does not beat greedy and why. |
| 10 | Limitations | 0.7 | NeurIPS 2, B.11 | Model assumptions vs. reality (terrain, thermal, regolith handling), untested scales, strategic-agent assumptions, single-mechanism family. |
| 11 | Broader impact and reproducibility | 0.5 | NeurIPS 10, 5; STRESS 6.1 | Who could be disadvantaged by the mechanism; code/data/seeds release with license and DOI. |
| 12 | Conclusion | 0.5 | | Restate the three findings with numbers; three specific next steps. |
| - | References | 1.5 | | |
| A | Full ODD | supp. | Grimm 2020 | 5-10 pages. |
| B | STRESS-DES checklist | supp. | Monks 2019 | 20 items as a table. |
| C | Proofs | supp. | NeurIPS 3 | |
| D | Parameter tables and scenario files | supp. | ODD 7, STRESS 3.3 | |
| E | Additional results, all seeds, token/compute tables | supp. | RAO A.6 | |
| F | Example traces per failure category | supp. | ReAct App. E | |

### Suggested figures (9)

1. Fig. 1: Worked example of one order moving through the system (sites, vehicle, bid, award, delivery), annotated timeline. (RAO Fig. 1 style.)
2. Fig. 2: Testbed architecture block diagram: environment, agents, market layer, logger, with event flow arrows. (Reflexion Fig. 2a style.)
3. Fig. 3: Scenario suite map: sites, routes, and the three difficulty knobs with their ranges.
4. Fig. 4: Main result: on-time delivery fraction (mean, 95% CI, n replications) per method, grouped by scenario.
5. Fig. 5: Stratified by difficulty knob (x = demand rate or blackout fraction, y = primary metric, one line per method, CI bands).
6. Fig. 6: Generalization: tuned on nominal, evaluated on surge and blackout; paired bars or lines.
7. Fig. 7: Mechanistic dynamics: clearing price and vehicle utilization vs. sol with a disruption onset marked; price convergence by round.
8. Fig. 8: Ablation 2x2 (e.g., re-planning on/off x information delay on/off).
9. Fig. 9: Failure taxonomy counts per method (stacked bars) plus, optionally, Fig. 10: Pareto plot of outcome vs. computation cost per method.

### Suggested tables (6)

1. Table 1: Positioning against existing simulators/mechanisms on feature axes.
2. Table 2: Entities and state variables (summary ODD element 2).
3. Table 3: Scenario suite: name, difficulty knob values, number of orders, fleet, horizon.
4. Table 4: Main results: primary and secondary metrics, mean +- 95% CI, n, per method x scenario, oracle row at top.
5. Table 5: Cost: wall-clock per replication, clearing time per round, messages per round, per method and difficulty bucket.
6. Table 6: Ablations: full mechanism and each single-component removal, primary metric with CI.

### Pre-registration-style checklist before running experiments

- Primary metric and stopping rule for replications fixed in writing.
- Difficulty knobs and generalization split declared.
- Baseline tuning budget equal to the method's and logged.
- Seed list committed to the repository.
- Figure list above mapped to specific logged quantities so the logger captures them from the first run.

---

## References

1. Shinn, N., Cassano, F., Berman, E., Gopinath, A., Narasimhan, K., Yao, S. "Reflexion: Language Agents with Verbal Reinforcement Learning." arXiv:2303.11366v4. https://arxiv.org/html/2303.11366v4
2. Gandhi, A., Chakraborty, S., Wang, X., Kumar, A., Neubig, G. "Recursive Agent Optimization." arXiv:2605.06639v2 (2 Oct 2026). https://arxiv.org/html/2605.06639v2 ; project page https://apga.github.io/RAO
3. Yao, S., Zhao, J., Yu, D., Du, N., Shafran, I., Narasimhan, K., Cao, Y. "ReAct: Synergizing Reasoning and Acting in Language Models." ICLR 2023, arXiv:2210.03629v3. https://arxiv.org/abs/2210.03629 ; https://arxiv.org/pdf/2210.03629 ; https://ar5iv.labs.arxiv.org/html/2210.03629
4. NeurIPS Paper Checklist. https://neurips.cc/public/guides/PaperChecklist
5. Grimm, V., Railsback, S. F., Vincenot, C. E., Berger, U., Gallagher, C., DeAngelis, D. L., Edmonds, B., Ge, J., Giske, J., Groeneveld, J., Johnston, A. S. A., Milles, A., Nabe-Nielsen, J., Polhill, J. G., Radchuk, V., Rohwaeder, M.-S., Stillman, R. A., Thiele, J. C., Ayllon, D. "The ODD Protocol for Describing Agent-Based and Other Simulation Models: A Second Update to Improve Clarity, Replication, and Structural Realism." JASSS 23(2) 7, 2020. https://www.jasss.org/23/2/7.html (DOI 10.18564/jasss.4259)
6. Monks, T., Currie, C. S. M., Onggo, B. S., Robinson, S., Kunc, M., Taylor, S. J. E. "Strengthening the reporting of empirical simulation studies: Introducing the STRESS guidelines." Journal of Simulation 13(1), 55-67, 2019. https://doi.org/10.1080/17477778.2018.1442155 ; EQUATOR entry https://www.equator-network.org/reporting-guidelines/strengthening-the-reporting-of-empirical-simulation-studies-introducing-the-stress-guidelines
7. Taylor, S. J. E., Anagnostou, A., Currie, C., Monks, T., Onggo, B. S., Kunc, M., Robinson, S. "Applying the STRESS Guidelines for Reproducibility in Modeling & Simulation: Application to a Disease Modeling Case Study." Proceedings of the 2018 Winter Simulation Conference. https://www.informs-sim.org/wsc18papers/includes/files/061.pdf (also https://bura.brunel.ac.uk/bitstream/2438/18563/1/FullText.pdf)
8. Heather, A., Monks, T., Harper, A., Mustafee, N., Mayne, A. "On the reproducibility of discrete-event simulation studies in health research: an empirical study using open models." arXiv:2501.13137. https://arxiv.org/html/2501.13137
9. Pineau, J. "The Machine Learning Reproducibility Checklist (v2.0, Apr. 7 2020)." https://www.cs.mcgill.ca/~jpineau/ReproducibilityChecklist.pdf
10. Pineau, J. "Reproducible, Reusable, and Robust Reinforcement Learning." NeurIPS 2018 invited talk slides. https://folk.idi.ntnu.no/odderik/RAI-2020/jpineau-AAAIwsReproducibility.pdf (mirror: https://cs.utexas.edu/~pstone/Courses/394Rspring22/resources/week15-joelle.pdf)
11. Pineau, J., Vincent-Lamarre, P., Sinha, K., Lariviere, V., Beygelzimer, A., d'Alche-Buc, F., Fox, E., Larochelle, H. "Improving Reproducibility in Machine Learning Research (A Report from the NeurIPS 2019 Reproducibility Program)." JMLR 22, 2021. https://jmlr.org/papers/v22/20-303.html
12. IJCAI Reproducibility Checklist. https://www.ijcai.org/reproducibility
13. Lipton, Z. C., Steinhardt, J. "Troubling Trends in Machine Learning Scholarship." arXiv:1807.03341, 2018. https://ar5iv.arxiv.org/html/1807.03341 ; https://arxiv.org/abs/1807.03341v2
