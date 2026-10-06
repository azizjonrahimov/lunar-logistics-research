# 03 — Marketplace mechanisms, empirical anchors, and simulation design for a neutral lunar cargo marketplace

Compiled 2026-10-05. Purpose: (a) catalogue the dispatch mechanisms we will implement as baselines in the lunar rover-logistics simulator, (b) collect quantitative anchors from the literature that justify parameter choices, (c) specify an experimental design per Law & Kelton, (d) give a reference list.

**Verification legend used throughout**
- **[V]** = statement checked against the source text (abstract, full text, or the saved PDF).
- **[S]** = taken from a search-engine snippet of the source; the number is attributed to that source but was not read in the source itself. Re-check before quoting in a paper.
- **[M]** = from memory / general knowledge; no URL verified here. Treat as a hypothesis.

---

## Part A — Mechanism catalogue (baselines to implement)

Notation: requests (loads) `T`, rovers `R`, each rover `r` has a current route `π_r`; `c(π)` = route cost (time or energy); `Δ` = batching interval; `H` = planning horizon.

### A1. Greedy nearest-available dispatch (control baseline, "street-hail" analogue)

**Description.** Each arriving request is immediately assigned to the closest idle (or soonest-free) compatible rover. No batching, no re-planning. This is the "closest driver policy" that Özkan & Ward note is "simple and easy to implement" and common in practice [V].

```
on_request_arrival(t):
    cand = {r in R : r.idle and compatible(r, t)}
    if cand empty: enqueue(t)            # or reject after max_wait
    else: r* = argmin_{r in cand} travel_time(r.pos, t.pickup); assign(t, r*)
on_rover_idle(r):
    if queue nonempty: t* = argmin_{t in queue} travel_time(r.pos, t.pickup); assign(t*, r)
```

**Complexity.** O(|R|) per request (O(|R| log |R|) with a spatial index).
**Known quality.** No approximation guarantee; Özkan & Ward (2020) show the closest-driver policy can be far from optimal and propose a policy accounting for future arrivals [V, abstract-level]. Feng, Kong & Wang (2021) show on-demand nearest matching can be *less* efficient than street-hailing when utilization is medium and the road is long, because en-route (deadhead) time is long; they propose response caps (a matching radius) [V]. Castillo, Knoepfle & Weyl (2017) describe the "wild goose chase": when idle supply is thin, nearest matching sends vehicles to far pickups, wasting time and driving further supply exit [V].
**Pros.** Trivial; zero latency; decentralizable. **Cons.** Myopic; high empty travel at thin supply; sensitive to arrival order.
**Citations.** Özkan & Ward 2020 (Stochastic Systems 10(1):29–70), https://pubsonline.informs.org/doi/10.1287/stsy.2019.0037 ; Feng, Kong, Wang 2021 (M&SOM), https://pubsonline.informs.org/doi/fpi/10.1287/msom.2020.0880 ; Castillo, Knoepfle, Weyl 2017, https://conference.nber.org/conf_papers/f98620/f98620.pdf

### A2. Batched centralized assignment (Hungarian / min-cost bipartite matching every Δ)

**Description.** Hold arriving requests for a window Δ; every Δ solve a minimum-cost assignment between the pooled requests and available rovers (cost = travel time to pickup, or marginal insertion cost into the rover's route). This is what Uber describes as batched matching ("evaluates nearby drivers and riders in one batch, then pairs riders and drivers … to reduce the average wait time for everyone, not just the closest pair") [S, Uber marketplace page].

```
every Δ:
    Tb = pending requests; Rb = rovers free (or free within Δ)
    C[i][j] = marginal_cost(insert t_i into π_{r_j})   # or travel time to pickup
    (add dummy rows/cols to square the matrix; forbidden pairs = +inf)
    X = hungarian(C)                                    # O(n^3), Kuhn 1955 / Munkres
    for (i,j) in X with C[i][j] < inf: assign(t_i, r_j)
    unassigned requests stay for next batch (age-weight their cost to avoid starvation)
```

**Complexity.** O(n³) with n = max(|Tb|,|Rb|) (Hungarian; Kuhn 1955 is the first polynomial algorithm for this LP class [V]). For n ≤ a few hundred this is milliseconds.
**Known quality.** Optimal for the one-shot assignment within a batch; not optimal across time. Theory on *how long to wait*: Ashlagi, Burq, Dutta, Jaillet, Saberi & Sholley (EC'19 / MOR 2023) show that for agents who stay d periods and arrive in random order, a batching algorithm that computes a max-weight matching every (d+1) periods is 0.279-competitive [V]. Akbarpour, Li & Oveis Gharan (JPE 2020): if the planner can identify agents about to depart, waiting to thicken the market substantially reduces unmatched agents; if not, matching greedily is close to optimal [V]. Yan, Zhu, Korolko & Woodard (NRL 2020): batching "increases the pool of options available for each driver and helps prevent the so-called wild goose chase"; jointly optimizing pricing and dynamic waiting raised utilization, throughput and welfare on Uber data [V, abstract-level].
**Pros.** Large reduction in empty travel at modest Δ; simple to explain to participants (neutrality: one cost matrix, one optimal matching). **Cons.** Adds Δ to every wait; requires a trusted central auctioneer; one-shot (no multi-stop route optimization unless cost = insertion cost).
**Citations.** Kuhn 1955, https://doi.org/10.1002/nav.3800020109 ; Ashlagi et al. EC'19, https://www.mit.edu/~jaillet/general/ec19.pdf and MOR 2023, https://ideas.repec.org/a/inm/ormoor/v48y2023i2p999-1016.html ; Akbarpour, Li, Oveis Gharan 2020, https://ideas.repec.org/a/ucp/jpolec/doi10.1086-704761.html (arXiv https://arxiv.org/abs/1402.3643) ; Yan et al. 2020, https://www.uber.com/blog/research/dynamic-pricing-and-matching-in-ride-hailing-platforms ; Uber matching page, https://www.uber.com/us/en/marketplace/matching/

### A3. Sequential single-item auction (SSI / SSA) — Koenig, Lagoudakis et al.

**Description.** Tasks are auctioned one at a time. In each round every rover bids on every unallocated task; the bid is the *increase* in its route cost if the task is inserted (cheapest insertion). The single globally lowest bid wins; repeat until all tasks are allocated. Because bids are conditioned on tasks already won, SSI captures synergies that parallel single-item auctions miss, without the exponential bundle enumeration of combinatorial auctions [V].

```
U = all unallocated tasks
while U nonempty:
    for r in R: for t in U:
        bid[r][t] = c(cheapest_insert(π_r, t)) - c(π_r)      # MiniSum bidding rule
    (r*, t*) = argmin bid
    π_{r*} = cheapest_insert(π_{r*}, t*);  U.remove(t*)
# dynamic variant: run again whenever new tasks arrive or a rover fails (re-auction its tasks)
```

**Complexity.** At most |T|·|R| bids in total (same as parallel single-item auctions) [V]; polynomial when cheapest-insertion is used to estimate path costs [V]. Each round costs O(|R|·|U|·|π|).
**Known quality.** Theorem 1 (Koenig et al. AAAI 2006; proof in Lagoudakis et al. RSS 2005): the sum of all path costs (MiniSum) is at most a factor **2** from optimum in known terrain with symmetric, triangle-inequality costs; a lower-bound example shows it can be a factor **1.5** off [V]. Their Figure 8 summarises: combinatorial auctions = exponential runtime/bids, optimal; SSA = polynomial, |T||R| bids, ratio 1.5–2; parallel single-item = polynomial, |T||R| bids, **unbounded** ratio [V]. Bounds for MiniMax / MiniAve objectives exist in Lagoudakis et al. 2005 but were not read here [M].
**Pros.** Provable bound, few messages, trivially supports re-auctioning on failure, participants need not reveal cost structure beyond bids (fits a multi-company marketplace). **Cons.** Needs a sequential coordinator (one round per task); greedy over task order; no notion of price/payment unless added (Vickrey-style second-lowest bid is a natural extension for a neutral marketplace [M]).
**Citations.** Koenig, Tovey, Lagoudakis, Markakis, Kempe, Keskinocak, Kleywegt, Meyerson, Jain 2006, AAAI, pp. 1625–1629, https://cdn.aaai.org/AAAI/2006/AAAI06-266.pdf ; Lagoudakis et al. 2005, RSS, https://roboticsproceedings.org/rss01/p45.html ; Gerkey & Matarić 2004 taxonomy (IJRR 23(9):939–954), https://robotics.usc.edu/publications/347

### A4. Consensus-Based Bundle Algorithm (CBBA) — Choi, Brunet & How 2009

**Description.** Fully decentralized multi-assignment. Phase 1 (bundle construction): each rover greedily adds to its bundle the task with the highest marginal score, keeping a path-ordered list. Phase 2 (consensus): rovers exchange winning-bid and winner lists with neighbours and resolve conflicts with a fixed decision table; a rover that loses a task drops it and everything added after it in its bundle. Iterate until no changes [V, abstract-level; phases from the standard description].

```
repeat:
    # Phase 1 — bundle building (local)
    while |b_r| < L_max:
        for t not in b_r: s[t] = max over insert positions of marginal_score(π_r, t)
        h[t] = (s[t] > y_r[t])               # can I outbid current winner?
        t* = argmax_t s[t]*h[t]; if none: break
        insert t* into b_r and π_r;  y_r[t*] = s[t*];  z_r[t*] = r
    # Phase 2 — consensus (communicate y_r, z_r, timestamps to neighbours)
    for each message from k: apply CBBA decision table (update / reset / leave) per task
    if some task in b_r was overruled: truncate b_r from that task onward
until no changes in y, z for all r
```

**Complexity.** Communication is local (neighbour-to-neighbour). Convergence is guaranteed under the diminishing-marginal-gain (DMG) scoring assumption with a static connected network; the bound is proportional to network diameter D times the number of tasks/bundle length (ED-CBBA paper states N_min·D under DMG, synchronous conflict resolution) [S]. Original paper: max(L_t, N_t)·D iterations [M].
**Known quality.** Converged solution is conflict-free and guaranteed ≥ 50 % of optimal score in the worst case under DMG [S: multiple secondary sources; the original abstract says "provable worst-case performance" [V]]. Robust to inconsistent situational awareness and changing network topology [V].
**Pros.** No central auctioneer (attractive for a marketplace where companies distrust each other); degrades gracefully with comms loss; handles multi-task bundles. **Cons.** DMG restricts scoring functions (time-discounted reward works; hard time windows need care); more messages than SSI; no explicit prices.
**Citations.** Choi, Brunet, How 2009, IEEE T-RO 25(4):912–926, https://dspace.mit.edu/handle/1721.1/52330 ; secondary: ED-CBBA, https://arxiv.org/abs/2509.06481 ; CBBA plugin docs, https://space-simulator.readthedocs.io/en/latest/pages/plugins/cbba.html

### A5. Posted-price load board with carrier self-selection, and hybrid (posted price + bid)

**Description.** The marketplace posts each load with a price; rover operators (carriers) browse and *choose* loads (as on DAT / Convoy / Uber Freight). Chen, Kim, Wang & Wang (arXiv 2106.00923) note that "unlike ridesharing platforms that use centralized matching, most freight platforms allow carriers to browse and choose loads themselves," and compare a pure posted-price mechanism with a hybrid in which carriers either accept the posted price or submit a bid; the hybrid is more profitable and they give tight bounds between the mechanisms across market sizes, validated on U.S. freight data [V, abstract-level]. For *contract* (recurring-lane) procurement, Caplice & Sheffi (2003) document combinatorial auctions where carriers bid on lane bundles, used by Home Depot, Walmart, Staples to buy billions of dollars of service [V].

```
# posted price (per load, per lane): p_t = f(distance, urgency, current supply/demand)
on_request_arrival(t): post(t, p_t)
each carrier r (agent model): utility(t) = p_t - own_cost(r, t) - opportunity_cost; accept if > 0 (MNL choice over lanes)
# hybrid: carrier may submit bid b < or > p_t; platform accepts lowest bid below reservation after window Δ_bid
# contract layer (optional): periodic combinatorial auction over recurring lanes (Caplice & Sheffi) -> routing guide;
#   spot board handles tender rejections and surges
```

**Complexity.** Pricing is O(1) per load given a model; the carrier choice model (MNL) is O(#lanes). Hybrid winner determination O(bids log bids) for single-item; combinatorial contract auctions are NP-hard in general (Caplice & Sheffi solve with MIP) [V/M].
**Known quality.** No optimality guarantee on routing; efficiency depends on *thickness*: Harris & Nguyen (AEJ:Micro 2025) find "a strong link between the thickness and the efficiency of the spot market" and that the US contract-plus-spot institution achieves 44 % of relationship-level first-best surplus [V]. Acocella, Caplice & Sheffi (TR-E 2020): primary-carrier tender acceptance fell from 81.9 % (soft market) to 68.5 % (tight market); backup carriers charge 9–12 % premiums and spot rates exceed contract by 23–35 % [S from paper HTML summary].
**Pros.** Closest to how a *neutral* marketplace among competing companies would actually run (no one cedes routing control); prices carry information; supports both contract and spot layers. **Cons.** Unfilled loads at thin supply; price dispersion; strategic behaviour; requires an agent model of carrier acceptance (a source of modelling uncertainty).
**Citations.** Chen, Kim, Wang, Wang, https://arxiv.org/abs/2106.00923 ; Caplice & Sheffi 2003 (J. Business Logistics), https://caplice.mit.edu/wp-content/uploads/2019/08/Paper-13-CapliceSheffi_OptimizationBasedProcurement_JBL2003.pdf and 2006 chapter, https://caplice.mit.edu/wp-content/uploads/2019/08/Paper-12-Caplice-and-Sheffi-2006.pdf ; Harris & Nguyen 2025, https://www.aeaweb.org/doi/10.1257/mic.20210343 ; Acocella, Caplice, Sheffi 2020, https://arxiv.org/abs/2108.07348

### A6. Rolling-horizon re-optimization of a dynamic PDPTW (periodic MILP / heuristic re-plan)

**Description.** Keep a full multi-stop plan for every rover. At each decision epoch (every Δ, or event-driven on arrival/failure), re-solve the pickup-and-delivery problem with time windows over a horizon H for all *unserved* requests, fixing the parts of routes already in execution. This is the standard "periodic re-optimization" strategy in Pillac et al.'s review of dynamic VRP (which also defines the *degree of dynamism* = share of requests unknown at the start) and in Berbeglia, Cordeau & Laporte's review of dynamic pickup-and-delivery [V, abstract-level]. Waiting strategies matter: Mitrović-Minić & Laporte (TR-B 2004) compare drive-first, wait-first, dynamic waiting and advanced dynamic waiting; advanced dynamic waiting was most efficient in both total route length and vehicle count [V]. Ichoua, Gendreau & Potvin (TS 2006) exploit probabilistic knowledge of future requests by inserting dummy customers to keep territory coverage [V].

```
every Δ or on event:
    fix: current leg of each rover; committed pickups already loaded
    build PDPTW instance: unserved requests, rover states, time windows, capacities, compatibility, energy
    solve: MILP with time limit (small instances) or ALNS/insertion+local search (larger)
    objective: w1*lateness + w2*distance/energy + w3*unserved penalty  (lexicographic or weighted)
    dispatch next legs; idle rovers follow waiting strategy (ADW: wait at current node a fraction of slack, then reposition)
```

**Complexity.** PDPTW is NP-hard; MILP exact only for ~10–30 requests per epoch; heuristics scale to hundreds. Re-plan frequency is bounded by solver time.
**Known quality.** Best achievable routing quality among the baselines (it *is* the optimizer the others approximate); value of re-optimization grows with degree of dynamism. No clean competitive ratio.
**Pros.** Upper benchmark for routing efficiency; natural home for time windows, capacity, energy, multi-stop consolidation. **Cons.** Requires full information from all companies (least "neutral"); computationally heavy; brittle to data errors.
**Citations.** Pillac, Gendreau, Guéret, Medaglia 2013, EJOR 225(1):1–11, https://doi.org/10.1016/j.ejor.2012.08.015 (preprint https://www.cirrelt.ca/DocumentsTravail/CIRRELT-2011-62.pdf) ; Berbeglia, Cordeau, Laporte 2010, EJOR 202(1):8–15, https://ideas.repec.org/a/eee/ejores/v202y2010i1p8-15.html ; Mitrović-Minić & Laporte 2004, TR-B 38(7):635–655, https://ideas.repec.org/a/eee/transb/v38y2004i7p635-655.html ; Ichoua, Gendreau, Potvin 2006, TS 40(2):211–225, https://pubsonline.informs.org/doi/fpi/10.1287/trsc.1050.0114

### A0. Reference condition: in-house fleets, no pooling

Each company serves only its own requests with its own rovers using A1 or A6 internally. This is the counterfactual against which "pooling gain" is measured, mirroring the non-cooperative setting in Cruijssen et al. (2007) and the collaborative-VRP literature surveyed by Gansterer & Hartl (2018) [V].

### A7. Add-on module: gain sharing (needed for any pooled mechanism to be acceptable)

Gansterer & Hartl's survey: the auction-based collaboration framework has five phases — request selection, bundle generation, bidding, winner determination, profit sharing — and "most problems in collaborative transportation use sharing methods based on cooperative game theory," with the Shapley value "generally the most applied method," proportional methods and the nucleolus also used [V]. Cruijssen, Cools & Dullaert (2007) find that "finding a reliable party to lead the cooperation and constructing a fair allocation mechanism for the benefits" are the impediments respondents agree with most [V]. Frisk et al. (2010) compare Shapley, nucleolus, separable/non-separable cost, shadow prices and volume weights on an 8-company forest-transport case and propose an "equal relative profits" rule [V]. Krajewska et al. (2008) use the Shapley value for PDPTW carrier coalitions [V].

```
# Shapley by Monte-Carlo (n companies, cost function via re-running the simulator on subsets)
phi[i] = 0
for k in 1..K: perm = random permutation of companies; S = {}
    for i in perm: phi[i] += (cost(S) - cost(S ∪ {i}))/K ; S.add(i)
# cost(S) = pooled cost of coalition S (one sim run or a cached estimate); exact Shapley is O(2^n)
```

Citations: Gansterer & Hartl 2018, EJOR 268(1):1–12, https://arxiv.org/abs/1706.05254 ; Cruijssen, Cools, Dullaert 2007, TR-E 43(2):129–142, https://research.tilburguniversity.edu/en/publications/horizontal-cooperation-in-logistics-opportunities-and-impediments/ ; Frisk, Göthe-Lundgren, Jörnsten, Rönnqvist 2010, EJOR 205(2):448–458, https://openaccess.nhh.no/nhh-xmlui/handle/11250/163867 ; Krajewska, Kopfer, Laporte, Røpke, Zaccour 2008, JORS 59(11):1483–1491, https://ideas.repec.org/a/pal/jorsoc/v59y2008i11d10.1057_palgrave.jors.2602489.html

---

## Part B — Empirical anchors (numbers to parameterise or validate the simulator)

| # | Finding | Value | Source (URL) | Status |
|---|---------|-------|--------------|--------|
| B1 | Joint route planning synergy (horizontal cooperation, road freight) | up to 30 % cost; cooperative vs non-cooperative "around 20–30 %" | Cruijssen, Bräysy, Dullaert, Fleuren, Salomon 2007, IJPDLM 37(4):287–304, https://research.vu.nl/en/publications/joint-route-planning-under-varying-market-conditions/ ; as cited in Gansterer & Hartl, https://ar5iv.labs.arxiv.org/html/1706.05254 | V (via survey text) |
| B2 | Other collaborative-routing savings compiled by Gansterer & Hartl | courier: up to 20 % travel cost (Lin 2008); city logistics: 25.6 % distance (Montoya-Torres 2016); inventory routing: 4–24 % cost, 8–33 % emissions (Soysal 2016); up to 27 % (Bailey 2011); stochastic demand 4–7.3 % (Quintero-Araujo 2016) | https://ar5iv.labs.arxiv.org/html/1706.05254 | V |
| B3 | Collaborative forest transport savings | 5–15 % | Frisk et al. 2010, https://openaccess.nhh.no/nhh-xmlui/handle/11250/163867 | V (abstract) |
| B4 | Shipper collaboration case (Nistevo network, 2,500-mile 7-leg continuous-move tour) | 19 % savings for both shippers | Ergun, Kuyzu, Savelsbergh TRISTAN V abstract, https://tristanconference.org/system/tristan-v/website/pdf/abstract_00026.pdf ; journal version TS 41(2):206–221, https://pubsonline.informs.org/doi/10.1287/trsc.1060.0169 | V (abstract PDF) |
| B5 | US truckload empty (deadhead) miles | 16.3 % (2023, non-tank); 20.6 % all carriers / 26 % private fleets (2020); 20.7 % (2017) | ATRI Operational Costs of Trucking, https://truckingresearch.org/2024/06/new-atri-research-industry-costs-increased-more-than-6-percent-during-freight-recession/ | S |
| B6 | Spot vs contract: thickness–efficiency link; institution achieves 44 % of relationship-level first-best surplus | qualitative + 44 % | Harris & Nguyen 2025, AEJ:Micro 17(1):308–353, https://www.aeaweb.org/doi/10.1257/mic.20210343 | V (abstract) |
| B7 | Primary-carrier tender acceptance, soft vs tight market; backup premium; spot premium | 81.9 % → 68.5 %; +9–12 %; +23–35 % | Acocella, Caplice, Sheffi 2020, TR-E 142, https://arxiv.org/abs/2108.07348 | S (from HTML summary) |
| B8 | Hybrid (posted + bid) vs pure posted price in freight marketplace | hybrid more profitable; tight bounds vs market size | Chen, Kim, Wang, Wang, https://arxiv.org/abs/2106.00923 | V (abstract; no numbers in abstract) |
| B9 | Batching competitive ratio (agents live d periods, random arrival order; max-weight matching every d+1 periods) | 0.279-competitive | Ashlagi et al. EC'19/MOR 2023, https://www.mit.edu/~jaillet/general/ec19.pdf | V (abstract) |
| B10 | Waiting vs greedy in dynamic matching | with departure info, waiting substantially reduces unmatched; without it, greedy is close to optimal | Akbarpour, Li, Oveis Gharan 2020, https://arxiv.org/abs/1402.3643 | V (abstract) |
| B11 | SSI auction MiniSum bound; lower-bound example; bids | ≤ 2× optimal; ≥ 1.5× possible; ≤ |T|·|R| bids; parallel single-item unbounded | Koenig et al. 2006, https://cdn.aaai.org/AAAI/2006/AAAI06-266.pdf | V (PDF text) |
| B12 | CBBA worst-case guarantee under DMG | ≥ 50 % of optimal; convergence ∝ network diameter D | Choi, Brunet, How 2009, https://dspace.mit.edu/handle/1721.1/52330 ; https://arxiv.org/abs/2509.06481 | S (50 %), V (convergence/robustness claims in abstract) |
| B13 | Teleoperated LTV average speed vs round-trip latency (NASA JSC, Earth→Moon analogue, natural lighting, all terrains) | 0 s: 3.24 km/h; 4 s: 2.56 km/h; 6 s: 2.03 km/h; 8 s: 1.76 km/h (−21 %, −37 %, −46 %) | Litaker, Li, Beaton, Lewis, NASA TM-20240001217, https://ntrs.nasa.gov/citations/20240001217 ; PDF https://www.lpi.usra.edu/lunar/artemis/resources/LitakerEtAl_NASA-TM-20240001217_LTV%20Teleops%20Study.pdf | S (numbers from search snippet; document existence and framing V) |
| B14 | Teleoperator training to ~60 % proficiency | 20–100 h over weeks; full proficiency ≈ a year | Litaker et al. 2025 follow-up, https://ntrs.nasa.gov/citations/20240011392 | V (page text) |
| B15 | Time-delayed lunar excavator teleoperation (VR, N = 12): completion time and success rate vs delay | completion time +39 % at 1.5 s and +74 % at 3 s (reported as 139 %, 174 % of baseline); mean 319 s / 443 s vs baseline; success 91 % → 82 % → 45 %; first-rock time 149 % / 273 % | Seo, Gupta, Ham, "Evaluation of Performance and Mental Workload during Time Delayed Teleoperation for the Lunar Surface Construction", https://par.nsf.gov/servlets/purl/10479687 | V (PDF text) |
| B16 | Remote vs local teleoperated assembly of a lunar radio array | +27 % mean completion time remote vs local | Kumar et al. 2020 IEEE Aerospace, https://arxiv.org/abs/2005.08120 | V (abstract) |
| B17 | Move-and-wait strategy under delay; continuous control breaks down | subjects adopt move-and-wait at 1.0, 2.1, 3.2 s delays; completion time predictable from no-delay data and number of open-loop moves; continuous sensor-motor coordination lost already at ~0.3 s | Ferrell 1965 (MIT, Sheridan adviser), https://dspace.mit.edu/handle/1721.1/11065 ; Sheridan 1993 review, IEEE T-RA 9:592–606 (cited via https://par.nsf.gov/servlets/purl/10172199) | S |
| B18 | "Cognitive horizon" for high-cognition telepresence | one-way latency ≈ 0.25 s (~75,000 km); Gateway at ~60,000 km → ~0.4 s, noticeable but not hindering | Lester & Thronson 2011, Space Policy, https://ntrs.nasa.gov/api/citations/20110024057/downloads/20110024057.pdf ; Kumar et al. 2020 | V (abstract-level) |
| B19 | Fan-out equation and measured values | FO = AT / IT (activity time / interaction time); measured FO 1.46 / 2.94 / 5.11 (simple / bounce / planning robots, 35 % obstacles), 1.84 / 3.36 / 9.09 (22 % obstacles), 1.12 / 2.47 / 3.97 (scrolled world) | Olsen & Wood 2004, CHI, https://hci.rwth-aachen.de/materials/conferences/CHI2004/1p231.pdf | V (PDF text) |
| B20 | Operator-capacity predictions drop when wait times (loss of SA, queueing) are modelled | up to −67 %; −36 % even for management-by-exception | Cummings & Mitchell 2008, IEEE SMC-A 38(2):451–460, https://dspace.mit.edu/handle/1721.1/90280 | V (page text) |
| B21 | Mining AHS supervision ratio | one controller per shift supervises the whole fleet (Komatsu); "a good operator can typically operate up to 30 trucks" once dig/dump set up; control room of ~2 operators | https://www.komatsu.com/en-au/technology/smart-solutions/smart-mining/autonomous-haulage-system ; https://www.equipmentworld.com/how-komatsus-autonomous-haul-trucks-work-and-what-it-takes-to-implement-the-technology-at-a-working-mine/ | S |
| B22 | Autonomous haul truck availability / utilization | fleet availability 88 %, utilization 95 % vs 85 % manned; downtime+standby+delays 5 % of availability vs 20 % manual; BHP > 90 % availability via maintenance analytics | search-snippet attributions to https://doi.org/10.3390/mining6030061 and https://www.miningdoc.tech/ (not opened: 403) | S — verify before use |
| B23 | Rio Tinto AHS operating effect | +700 to +1,000 operating hours per truck per year; ~15 % lower load-and-haul unit cost; +20 % productivity | https://mining-journal.com/investment/news/1311213/rios-autonomous-fleet-hauls-billion-tonnes ; https://www.e-mj.com/breaking-news/rio-tinto-will-expand-autonomous-fleet/ | S |
| B24 | Manual vs AHS OEE (Chile) | manual OEE 14.4 % lower than AHS | https://repositorio.unab.cl/handle/ria/58582 | S |
| B25 | Mars solar-array dust degradation (proxy for lunar dust loss rates; lunar has no wind cleaning) | typical 0.2 %/sol; observed 0.05–2 %/sol | Lorenz et al. 2021, Planetary and Space Science 207, https://hal.sorbonne-universite.fr/hal-03369920 | V (abstract via search) |
| B26 | Apollo lunar-dust effects | nine categories incl. clogging, abrasion, diminished heat rejection; brushing "essentially ineffective"; LRV radiator degradation (no % given) | Gaier 2005, NASA/TM-2005-213610, https://ntrs.nasa.gov/citations/20050160460 | V (abstract-level) |
| B27 | Rover reliability as a design parameter | MER designed for 90 sols, operated > 3 years; argues for an optimal (not maximal) reliability range; no MTBF numbers given | Stancliff, Dolan, Trebi-Ollennu 2007 PerMIS, https://publications.ri.cmu.edu/planning-to-fail-reliability-as-a-design-parameter-for-planetary-rover-missions | V |
| B28 | Standard cargo interface (FLEX Universal Payload) | up to 1,600 kg per rover; > 3 m³; format "open-sourced"; Payload Interface Guide v2.0 (Nov 2022) | https://www.astrolab.space/flex-services/ ; guide PDF https://science.nasa.gov/wp-content/uploads/2024/03/mathews.pdf | V (page text) |
| B29 | Lunar interoperability scope today | LunaNet Interoperability Specification covers comms, PNT, auxiliary services only; LOGIC/LSIC targets power, comms, PNT, surveying, traffic — no mechanical cargo-interface standard yet | https://ntrs.nasa.gov/api/citations/20230013361/downloads/ICSSC-2023_LSR_paper%20rev7k.pdf ; https://www.darpa.mil/news/2023/interoperability-lunar-infrastructure ; https://www.jhuapl.edu/news/news-releases/231011b-lunar-technology-development | V |
| B30 | Fraction of cargo incompatible without shared standards | **no source found** — treat as a free parameter (e.g., 0 %, 25 %, 50 %) in the design | — | gap |
| B31 | Multi-robot cooperative transport coordination overhead | Cost of Transport rises sharply from 1 → 2 robots then plateaus (search snippet); reviews categorise push / grasp / cage strategies and centralised vs decentralised control | Pandit et al. 2026, https://arxiv.org/abs/2609.17824 (snippet only, abstract did not confirm) ; Tuci, Alkilabi, Akanyeti 2018, https://doi.org/10.3389/frobt.2018.00059 ; Farivarnejad & Berman 2022, Annu. Rev. Control Robot. Auton. Syst., https://par.nsf.gov/servlets/purl/10344132 | S / V |

**How these feed the simulator.** B13/B15/B17 give a latency-to-throughput curve: for driving, speed multiplier ≈ 1.00 / 0.79 / 0.63 / 0.54 at RTT 0 / 4 / 6 / 8 s (B13); for manipulation (load/unload), time multiplier ≈ 1.39 at 1.5 s and 1.74 at 3 s with success dropping to 45 % at 3 s (B15). Earth–Moon RTT is ~2.5–3 s (B15 text), so a *teleoperated* handling step should be modelled at ~1.6–1.8× nominal with a retry probability; an *orbital/surface* operator (0.4 s) at ~1.0–1.1×. B19–B21 bound the supervisor pool: FO ≈ AT/IT, with FO from ~1–2 (low autonomy) to ~5–9 (planning autonomy) in Olsen & Wood's studies, up to ~30 vehicles per controller in highly structured mining haulage. B22–B24 motivate availability levels 85 / 90 / 95 % and the +15 % productivity assumption for autonomy. B1–B4 give the pooling-gain band (5–30 %) that a pooled marketplace must land in to be credible. B5 gives the deadhead share (16–21 %) in-house fleets should exhibit before pooling. B9/B10 justify sweeping Δ and modelling departure (deadline) information as a factor.

---

## Part C — Recommended experimental design (Law & Kelton style)

### C1. Simulation engine and method
- Discrete-event, process-based, in **SimPy** (https://simpy.readthedocs.io/): rovers, loads, operators and comms as processes; charging bays and operator pool as `Resource`s.
- **Terminating vs steady-state.** Run as a steady-state study (continuous operations) with a warm-up, *or* as a terminating study over a fixed campaign (e.g., one lunar day = 14 Earth days). Recommend both: steady-state for mechanism comparison, terminating for mission-planning readouts. Law (WSC 2004/2023 tutorials) covers run length, warm-up and replication choices with the replication/deletion approach (https://www.informs-sim.org/wsc04papers/009.pdf ; https://www.informs-sim.org/wsc23papers/124.pdf).
- **Warm-up** via Welch's (1983) graphical procedure: average across k pilot replications, plot moving average, truncate where the curve flattens (Warwick AutoSimOA note: https://warwick.ac.uk/fac/soc/wbs/projects/autosimoa/current_work/website_warmup_methods_total_doc.pdf). Law & Kelton (1984, Operations Research 32(6):1221–1239) show variance-estimator bias matters more than point-estimator bias for CI coverage, so do not under-delete (https://ideas.repec.org/a/inm/oropre/v32y1984i6p1221-1239.html).
- **Replications.** Use the sequential procedure of Hoad, Robinson & Davies (2010, JORS 61(11):1632–1644): add replications until the 95 % CI half-width ≤ 5 % of the mean for the primary metric, with a look-ahead to confirm stability (https://wrap.warwick.ac.uk/5071/). Expect 20–50 replications per cell for fill-rate/wait metrics; budget for 100 on the thin-market cells where variance is highest.
- **Common random numbers (CRN).** Dedicated, synchronised random streams for (i) load arrival times, (ii) load origins/destinations/mass, (iii) rover failures, (iv) comms dropouts, (v) teleop handling-time noise, so every mechanism sees the *same* demand and failure sample path; compare mechanisms with **paired-t CIs** on per-replication differences. CRN only helps when streams are synchronised by purpose, not merely seeded identically (Glasserman & Yao guidelines, https://business.columbia.edu/sites/default/files-efs/pubfiles/4261/glasserman_yao_guidelines.pdf ; WSC 2001 on CRN with selection procedures, https://informs-sim.org/wsc01papers/053.PDF).
- **Design of experiments.** Following Kleijnen (2015, *Design and Analysis of Simulation Experiments*, https://www.informs-sim.org/wsc05papers/kleijnen.pdf for the short version): first a screening design (sequential bifurcation or a resolution-IV fractional factorial) over all factors to find the few that matter; then a full factorial on the 3–4 important factors × mechanisms; fit a regression metamodel; report main effects and two-way interactions.
- **Sensitivity presentation.** Tornado diagram for one-at-a-time ±range swings on the primary metric (Eschenbach 1992, Interfaces 22(6):40–46, https://pubsonline.informs.org/doi/fpi/10.1287/inte.22.6.40); spider plot for the 3–4 most important factors; CI bars on every bar.

### C2. Factors and levels

| Factor | Levels | Rationale / anchor |
|--------|--------|--------------------|
| Dispatch mechanism (treatment) | A0 in-house; A1 greedy; A2 batch-Hungarian; A3 SSI; A4 CBBA; A5 posted/hybrid; A6 rolling-horizon PDPTW | Part A |
| Market thickness: number of companies × rovers each | 2×2, 3×3, 5×4, 8×5 (N = 4 … 40 rovers) | B6, B9, B10 — thickness is the central hypothesis |
| Demand intensity (offered load) | ρ ≈ 0.4, 0.7, 0.9 of fleet capacity | utilization regime drives wild-goose-chase effects (B-A1 refs) |
| Batching window Δ (A2, A5-hybrid, A6) | 0, 5, 15, 60 min | B9, B10 |
| Deadline information | known vs unknown departure/deadline | B10 |
| Round-trip latency / operator location | 0.4 s (orbit/surface), 2.6 s (Earth, direct), 8 s (relayed/worst) | B13, B15, B18 |
| Autonomy level | teleoperated handling; supervised autonomy (FO ≈ 3–5); full autonomy (FO ≈ 30) | B19–B21 |
| Operator pool size | 1, 2, 4 per company or shared | B19–B21 |
| Rover availability | 85 %, 90 %, 95 % (MTBF/MTTR chosen to hit these) | B22–B24 |
| Dust degradation of speed/energy | 0, 0.2 %, 1 % per Earth-day of exposure | B25, B26 (proxy) |
| Cargo-interface incompatibility | 0 %, 25 %, 50 % of loads incompatible with foreign rovers | B30 (no source — explicitly a free parameter) |
| Team-lift share | 0 %, 10 %, 25 % of loads require 2 rovers | B31 |
| Gain-sharing rule (reporting only) | Shapley (MC), proportional, equal-relative-profit | A7 |

Full factorial is infeasible (7 × 4 × 3 × 4 × 2 × 3 × 3 × 3 × 3 × 3 × 3 × 3 ≈ 10⁶ cells). Plan: (1) screening with all factors at 2 levels (resolution IV, ≈ 32–64 runs × 10 replications); (2) main study: mechanism × thickness × demand × latency at full levels (7 × 4 × 3 × 3 = 252 cells × 30 reps ≈ 7,600 runs); (3) one-at-a-time tornado on the remaining factors around the central cell.

### C3. Metrics (per replication, after warm-up)

Primary: **fill rate** (loads delivered within deadline / loads offered). Secondary: mean and 95th-percentile **wait** (request → pickup) and **delivery delay**; **empty-travel share** (deadhead distance / total; baseline target 16–21 %, B5); **rover utilization** (loaded time / available time); **energy per tonne-km**; **operator utilization** and queueing delay at the operator pool; **price dispersion** (coefficient of variation of clearing price per tonne-km, A5 only); **unserved/rejected loads**; **per-company cost before and after gain sharing** (and whether every company is better off — individual rationality; core non-emptiness check if n ≤ 6); computational time per decision epoch (practicality).

### C4. Hypotheses to pre-register

H1 Pooled mechanisms (A2–A6) reduce total cost vs A0 by 5–30 % at N ≥ 10 rovers (B1–B4), with gains shrinking to < 5 % at N ≤ 4. H2 Batching (Δ > 0) beats greedy only when deadlines are known or thickness is low-to-medium (B9, B10); at ρ ≈ 0.9 batching's wait cost dominates. H3 SSI achieves ≥ 90 % of A6's distance efficiency at < 1 % of its compute (B11). H4 CBBA matches SSI within 10 % and degrades least under comms dropouts (A4). H5 Teleoperated handling at 2.6 s RTT cuts effective fleet throughput by 35–45 % relative to 0.4 s (B13, B15); supervised autonomy with FO ≥ 5 removes most of this loss. H6 Interface incompatibility ≥ 25 % erases more than half the pooling gain (free parameter; this is a design-insight output, not an empirical claim).

### C5. Validation and verification
- Verify the queueing core against M/M/c formulas at ρ = 0.7 (wait, utilization) before adding routing.
- Validate A0 against B5 (deadhead 16–21 %) and B22 (availability) at terrestrial-analogue settings; validate pooling gains against the B1–B4 band.
- Trace a single replication's event log for each mechanism (face validity); animate one lunar day.
- Report every mechanism comparison as a paired-t CI (CRN) with the number of replications, warm-up length and random-stream policy stated.

---

## Part D — Reference list (URLs as retrieved 2026-10-05)

Marketplaces, matching, thickness
1. Akbarpour, M., Li, S., Oveis Gharan, S. (2020). Thickness and Information in Dynamic Matching Markets. *J. Political Economy* 128(3):783–815. https://ideas.repec.org/a/ucp/jpolec/doi10.1086-704761.html ; arXiv https://arxiv.org/abs/1402.3643
2. Ashlagi, I., Burq, M., Dutta, C., Jaillet, P., Saberi, A., Sholley, C. (2019/2023). Edge-Weighted Online Windowed Matching. ACM EC'19; *Math. of OR* 48(2):999–1016. https://www.mit.edu/~jaillet/general/ec19.pdf ; https://ideas.repec.org/a/inm/ormoor/v48y2023i2p999-1016.html
3. Ashlagi, I., Burq, M., Jaillet, P., Manshadi, V. (2019). On Matching and Thickness in Heterogeneous Dynamic Markets. *Operations Research* 67(4):927–949. https://arxiv.org/abs/1606.03626
4. Yan, C., Zhu, H., Korolko, N., Woodard, D. (2020). Dynamic pricing and matching in ride-hailing platforms. *Naval Research Logistics*. https://www.uber.com/blog/research/dynamic-pricing-and-matching-in-ride-hailing-platforms
5. Castillo, J. C., Knoepfle, D., Weyl, E. G. (2017). Surge Pricing Solves the Wild Goose Chase. ACM EC'17 (later *Management Science*). https://conference.nber.org/conf_papers/f98620/f98620.pdf
6. Feng, G., Kong, G., Wang, Z. (2021). We Are on the Way: Analysis of On-Demand Ride-Hailing Systems. *M&SOM*. https://pubsonline.informs.org/doi/fpi/10.1287/msom.2020.0880
7. Özkan, E., Ward, A. R. (2020). Dynamic Matching for Real-Time Ride Sharing. *Stochastic Systems* 10(1):29–70. https://pubsonline.informs.org/doi/10.1287/stsy.2019.0037
8. Chen, R., Kim, S., Wang, H., Wang, X. (2021). Posted Price versus Hybrid Mechanisms in Freight Transportation Marketplaces. arXiv:2106.00923. https://arxiv.org/abs/2106.00923
9. Caplice, C., Sheffi, Y. (2003). Optimization-Based Procurement for Transportation Services. *J. Business Logistics* 24(2). https://caplice.mit.edu/wp-content/uploads/2019/08/Paper-13-CapliceSheffi_OptimizationBasedProcurement_JBL2003.pdf
10. Caplice, C., Sheffi, Y. (2006). Combinatorial Auctions for Truckload Transportation. In *Combinatorial Auctions* (MIT Press). https://caplice.mit.edu/wp-content/uploads/2019/08/Paper-12-Caplice-and-Sheffi-2006.pdf
11. Harris, A., Nguyen, T. (2025). Long-Term Relationships and the Spot Market: Evidence from US Trucking. *AEJ: Microeconomics* 17(1):308–353. https://www.aeaweb.org/doi/10.1257/mic.20210343
12. Acocella, A., Caplice, C., Sheffi, Y. (2020). Elephants or Goldfish? An Empirical Analysis of Carrier Reciprocity in Dynamic Freight Markets. *Transportation Research Part E* 142. https://arxiv.org/abs/2108.07348
13. ATRI (2024). An Analysis of the Operational Costs of Trucking (deadhead 16.3 % in 2023). https://truckingresearch.org/2024/06/new-atri-research-industry-costs-increased-more-than-6-percent-during-freight-recession/
14. Uber Marketplace — Matching (batched matching description). https://www.uber.com/us/en/marketplace/matching/

Horizontal collaboration and gain sharing
15. Cruijssen, F., Cools, M., Dullaert, W. (2007). Horizontal cooperation in logistics: Opportunities and impediments. *Transportation Research Part E* 43(2):129–142. https://research.tilburguniversity.edu/en/publications/horizontal-cooperation-in-logistics-opportunities-and-impediments/
16. Cruijssen, F., Bräysy, O., Dullaert, W., Fleuren, H., Salomon, M. (2007). Joint route planning under varying market conditions. *IJPDLM* 37(4):287–304. https://research.vu.nl/en/publications/joint-route-planning-under-varying-market-conditions/
17. Gansterer, M., Hartl, R. F. (2018). Collaborative vehicle routing: A survey. *EJOR* 268(1):1–12. https://arxiv.org/abs/1706.05254 (HTML: https://ar5iv.labs.arxiv.org/html/1706.05254)
18. Ergun, Ö., Kuyzu, G., Savelsbergh, M. (2007). Reducing Truckload Transportation Costs Through Collaboration. *Transportation Science* 41(2):206–221. https://pubsonline.informs.org/doi/10.1287/trsc.1060.0169 ; TRISTAN V abstract https://tristanconference.org/system/tristan-v/website/pdf/abstract_00026.pdf
19. Frisk, M., Göthe-Lundgren, M., Jörnsten, K., Rönnqvist, M. (2010). Cost allocation in collaborative forest transportation. *EJOR* 205(2):448–458. https://openaccess.nhh.no/nhh-xmlui/handle/11250/163867
20. Krajewska, M. A., Kopfer, H., Laporte, G., Røpke, S., Zaccour, G. (2008). Horizontal cooperation among freight carriers: request allocation and profit sharing. *JORS* 59(11):1483–1491. https://ideas.repec.org/a/pal/jorsoc/v59y2008i11d10.1057_palgrave.jors.2602489.html
21. Pan, S., Ballot, E., Fontane, F. (2013). The reduction of greenhouse gas emissions from freight transport by pooling supply chains. *IJPE* 143(1):86–94. https://ideas.repec.org/a/eee/proeco/v143y2013i1p86-94.html (percentages not retrieved)

Multi-robot task allocation
22. Gerkey, B. P., Matarić, M. J. (2004). A formal analysis and taxonomy of task allocation in multi-robot systems. *IJRR* 23(9):939–954. https://robotics.usc.edu/publications/347
23. Lagoudakis, M. G., et al. (2005). Auction-Based Multi-Robot Routing. *Robotics: Science and Systems I*, pp. 343–350. https://roboticsproceedings.org/rss01/p45.html
24. Koenig, S., Tovey, C., Lagoudakis, M., Markakis, V., Kempe, D., Keskinocak, P., Kleywegt, A., Meyerson, A., Jain, S. (2006). The Power of Sequential Single-Item Auctions for Agent Coordination. AAAI 2006, pp. 1625–1629. https://cdn.aaai.org/AAAI/2006/AAAI06-266.pdf
25. Choi, H.-L., Brunet, L., How, J. P. (2009). Consensus-Based Decentralized Auctions for Robust Task Allocation. *IEEE Trans. Robotics* 25(4):912–926. https://dspace.mit.edu/handle/1721.1/52330
26. Kuhn, H. W. (1955). The Hungarian method for the assignment problem. *Naval Research Logistics Quarterly* 2(1–2):83–97. https://doi.org/10.1002/nav.3800020109
27. Event-Driven CBBA with Reduced Communication (2025, arXiv:2509.06481) — secondary source for CBBA bounds. https://arxiv.org/abs/2509.06481

Dynamic vehicle routing
28. Pillac, V., Gendreau, M., Guéret, C., Medaglia, A. L. (2013). A review of dynamic vehicle routing problems. *EJOR* 225(1):1–11. https://doi.org/10.1016/j.ejor.2012.08.015 ; preprint https://www.cirrelt.ca/DocumentsTravail/CIRRELT-2011-62.pdf
29. Berbeglia, G., Cordeau, J.-F., Laporte, G. (2010). Dynamic pickup and delivery problems. *EJOR* 202(1):8–15. https://ideas.repec.org/a/eee/ejores/v202y2010i1p8-15.html
30. Mitrović-Minić, S., Laporte, G. (2004). Waiting strategies for the dynamic pickup and delivery problem with time windows. *Transportation Research Part B* 38(7):635–655. https://ideas.repec.org/a/eee/transb/v38y2004i7p635-655.html
31. Ichoua, S., Gendreau, M., Potvin, J.-Y. (2006). Exploiting Knowledge About Future Demands for Real-Time Vehicle Dispatching. *Transportation Science* 40(2):211–225. https://pubsonline.informs.org/doi/fpi/10.1287/trsc.1050.0114

Teleoperation, latency, supervisory control
32. Litaker, H. L., Li, Z. Q., Beaton, K. H., Lewis, J. F. (2024). Lunar Terrain Vehicle (LTV) Remote Teleoperation Studies Under Four Lunar Communication Latencies. NASA TM-20240001217. https://ntrs.nasa.gov/citations/20240001217 ; follow-up (2025) https://ntrs.nasa.gov/citations/20240011392
33. Seo, M., Gupta, S., Ham, Y. Evaluation of Performance and Mental Workload during Time Delayed Teleoperation for the Lunar Surface Construction. https://par.nsf.gov/servlets/purl/10479687
34. Kumar, A., Bell, M., Mellinkoff, B., Sandoval, A., Martin, W. B., Burns, J. (2020). A Methodology to Assess the Human Factors Associated with Lunar Teleoperated Assembly Tasks. IEEE Aerospace. https://arxiv.org/abs/2005.08120
35. Ferrell, W. R. (1965). Remote manipulation with transmission delay. MIT (adviser T. B. Sheridan). https://dspace.mit.edu/handle/1721.1/11065
36. Sheridan, T. B. (1993). Space teleoperation through time delay: review and prognosis. *IEEE Trans. Robotics and Automation* 9(5):592–606. (No open URL verified; cited in ref. 33 and https://par.nsf.gov/servlets/purl/10172199)
37. Lester, D., Thronson, H. (2011). Human space exploration and human spaceflight: Latency and the cognitive scale of the universe. *Space Policy* 27(2). https://ntrs.nasa.gov/api/citations/20110024057/downloads/20110024057.pdf
38. Olsen, D. R., Wood, S. B. (2004). Fan-out: Measuring Human Control of Multiple Robots. CHI 2004. https://hci.rwth-aachen.de/materials/conferences/CHI2004/1p231.pdf ; related: Olsen, Turner, Wood (2004) Metrics for Human Driving of Multiple Robots, https://scholarsarchive.byu.edu/facpub/1286
39. Cummings, M. L., Mitchell, P. J. (2008). Predicting Controller Capacity in Supervisory Control of Multiple UAVs. *IEEE SMC-A* 38(2):451–460. https://dspace.mit.edu/handle/1721.1/90280
40. Chen, J. Y. C., Haas, E. C., Barnes, M. J. (2007). Human performance issues and user interface design for teleoperated robots. *IEEE SMC-C* 37(6). (Not opened; listed for completeness.)

Cooperative transport
41. Tuci, E., Alkilabi, M. H. M., Akanyeti, O. (2018). Cooperative Object Transport in Multi-Robot Systems: A Review of the State-of-the-Art. *Frontiers in Robotics and AI* 5:59. https://doi.org/10.3389/frobt.2018.00059
42. Farivarnejad, H., Berman, S. (2022). Multirobot Control Strategies for Collective Transport. *Annu. Rev. Control, Robotics, and Autonomous Systems*. https://par.nsf.gov/servlets/purl/10344132
43. Pandit, B., Gadde, M. S., Shrestha, A. K., Fern, A. (2026). Learning Multi-Humanoid Pickup and Transport via Decentralized Object-Centric Control. arXiv:2609.17824. https://arxiv.org/abs/2609.17824

Reliability, dust, autonomous haulage
44. Stancliff, S. B., Dolan, J. M., Trebi-Ollennu, A. (2007). Planning to Fail — Reliability as a Design Parameter for Planetary Rover Missions. PerMIS'07. https://publications.ri.cmu.edu/planning-to-fail-reliability-as-a-design-parameter-for-planetary-rover-missions
45. Lorenz, R. D., et al. (2021). Lander and rover histories of dust accumulation on and removal from solar arrays on Mars. *Planetary and Space Science* 207. https://hal.sorbonne-universite.fr/hal-03369920
46. Gaier, J. R. (2005). The Effects of Lunar Dust on EVA Systems During the Apollo Missions. NASA/TM-2005-213610. https://ntrs.nasa.gov/citations/20050160460
47. Automated Haulage Trucks: Impact on Workplace Safety and Efficiency in Surface Mining Systems. *Mining* 6(3):61 (MDPI). https://doi.org/10.3390/mining6030061 (not opened: 403)
48. Rio Tinto AHS performance reports. https://mining-journal.com/investment/news/1311213/rios-autonomous-fleet-hauls-billion-tonnes ; https://www.e-mj.com/breaking-news/rio-tinto-will-expand-autonomous-fleet/
49. Komatsu FrontRunner AHS (single controller per shift). https://www.komatsu.com/en-au/technology/smart-solutions/smart-mining/autonomous-haulage-system ; Equipment World explainer (up to 30 trucks per operator), https://www.equipmentworld.com/how-komatsus-autonomous-haul-trucks-work-and-what-it-takes-to-implement-the-technology-at-a-working-mine/

Standards and interoperability
50. Astrolab FLEX Services / FLEX Universal Payload. https://www.astrolab.space/flex-services/ ; FLEX Payload Interface Guide v2.0 (Nov 2022), https://science.nasa.gov/wp-content/uploads/2024/03/mathews.pdf
51. Giordano, P., Swinden, R., Gramling, C., Crenshaw, J., Ventura-Traveset, J. (2023). LunaNet PNT Services and Signals (LunaNet Interoperability Specification). https://ntrs.nasa.gov/api/citations/20230013361/downloads/ICSSC-2023_LSR_paper%20rev7k.pdf
52. DARPA LOGIC (Lunar Operating Guidelines for Infrastructure Consortium) and JHU APL/LSIC. https://www.darpa.mil/news/2023/interoperability-lunar-infrastructure ; https://www.jhuapl.edu/news/news-releases/231011b-lunar-technology-development

Simulation methodology
53. Law, A. M. (2004; updated 2023). Statistical Analysis of Simulation Output Data: The Practical State of the Art. *Proc. Winter Simulation Conference*. https://www.informs-sim.org/wsc04papers/009.pdf ; https://www.informs-sim.org/wsc23papers/124.pdf
54. Law, A. M., Kelton, W. D. (1984). Confidence Intervals for Steady-State Simulations: I. A Survey of Fixed Sample Size Procedures. *Operations Research* 32(6):1221–1239. https://ideas.repec.org/a/inm/oropre/v32y1984i6p1221-1239.html (textbook: Law, *Simulation Modeling and Analysis*, 5th ed., McGraw-Hill — not linked)
55. Welch, P. D. (1983). The statistical analysis of simulation results. In Lavenberg (ed.) *Computer Performance Modeling Handbook*. Summarised in Warwick AutoSimOA warm-up methods note: https://warwick.ac.uk/fac/soc/wbs/projects/autosimoa/current_work/website_warmup_methods_total_doc.pdf
56. Hoad, K., Robinson, S., Davies, R. (2010). Automated selection of the number of replications for a discrete-event simulation. *JORS* 61(11):1632–1644. https://wrap.warwick.ac.uk/5071/
57. Kleijnen, J. P. C. (2015). *Design and Analysis of Simulation Experiments*, 2nd ed., Springer; WSC tutorial version https://www.informs-sim.org/wsc05papers/kleijnen.pdf
58. Eschenbach, T. G. (1992). Spiderplots versus Tornado Diagrams for Sensitivity Analysis. *Interfaces* 22(6):40–46. https://pubsonline.informs.org/doi/fpi/10.1287/inte.22.6.40
59. Glasserman, P., Yao, D. D. Guidelines for the use of common random numbers. https://business.columbia.edu/sites/default/files-efs/pubfiles/4261/glasserman_yao_guidelines.pdf ; WSC 2001 CRN + selection procedures https://informs-sim.org/wsc01papers/053.PDF
60. SimPy documentation. https://simpy.readthedocs.io/

---

## Part E — Honest gaps and items to re-verify

1. **No source quantifies the fraction of lunar cargo that would be incompatible across companies without a shared standard (B30).** Treat as a free design parameter and say so in the write-up. What *is* verified: FLEX Universal Payload is an open-sourced format (1,600 kg, > 3 m³); current NASA/ESA/DARPA interoperability work (LunaNet, LOGIC, LSIC) covers comms/PNT/power/surveying, not mechanical cargo interfaces.
2. **AHS availability percentages (B22) come from search snippets**; the MDPI and Springer sources returned 403. Before citing 88 %/95 %, open https://doi.org/10.3390/mining6030061 and confirm. The Rio Tinto hours/cost figures (B23) are press reports, not peer-reviewed.
3. **CBBA's 50 % guarantee and the convergence bound** were confirmed only through secondary sources (B12); the original abstract says "provable worst-case performance" without the number. Read Choi et al. §V to quote precisely.
4. **LTV speed numbers (B13)** are from a search snippet of the NASA TM; the two PDF download URLs tried returned 404. The LPI mirror URL above should be opened to confirm the table before publication.
5. **No planetary-rover MTBF figure was found** (Stancliff et al. give none). Our availability levels rest on mining-AHS analogues; flag this explicitly as an analogy.
6. **Lunar-specific dust degradation rates were not found**; the 0.2 %/sol figure is Martian solar-array obscuration and the Moon lacks wind-cleaning events, so lunar monotonic accumulation could be worse per unit of regolith disturbed. Gaier (2005) is qualitative.
7. **Pan, Ballot & Fontane (2013) CO2 percentages** were not retrieved; the entry is kept only as a pointer.
8. **Cooperative-transport overhead (B31)**: the "CoT jumps 1→2 robots then plateaus" statement appeared only in a search snippet of arXiv 2609.17824 and was not in the abstract; use the reviews (Tuci et al.; Farivarnejad & Berman) for qualitative framing and model team-lift overhead as a parameter (e.g., +30–50 % time for 2-rover tasks) to be swept, not as an empirical constant.
9. **Pseudo-code is reconstructed from the papers' descriptions**, not copied; the SSI code follows Koenig et al.'s Figure 4 description (bid = cheapest-insertion cost increase) and the CBBA code the standard two-phase description. Pricing/payment layers for SSI (e.g., second-price) are our extension, not from the sources.
10. Ride-hailing thickness results (B9, B10) are for *bilateral* matching of homogeneous agents; lunar cargo has heterogeneous compatibility, closer to Ashlagi, Burq, Jaillet & Manshadi (2019), who show that market composition (share of hard-to-match agents) changes which matching technology and prioritisation is best — a reason to include the incompatibility factor in the design.
