# Lunar Surface Logistics: Literature and Numbers for a DES of Cargo Movement at the Artemis South-Pole Moon Base

Compiled 2026-10-05. Purpose: parameterize a discrete-event simulation (DES) of cargo movement on the lunar surface and support the Related Work section of a paper on a neutral, multi-operator dispatch marketplace for lunar surface cargo.

Conventions: every number carries the URL it was taken from and a confidence grade.
- **high** = read directly from the primary document (NASA PDF text extracted locally, journal/arXiv abstract page, or company page).
- **med** = from a reputable secondary report (SpacePolicyOnline, SpaceNews, Aerospace America, Wikipedia table with citations) or a primary source I could only see via a search snippet.
- **low** = single secondary source, conflicting sources, or a value I derived myself (derivations are marked "derived").

Section 0 lists what I could NOT verify so the reader is not misled.

---

## 0. Honesty note: items I could not verify or that conflict with the task brief

| Claim in brief | What I actually found |
|---|---|
| CLPS 2.0 "$6B cap" | The CLPS 2 solicitation (80JSC026R0015, proposals due 30 Jun 2026) is reported with a **$10 billion ceiling, up to $15 billion with options** (GovConWire / govcontractfinder). I found no $6B figure. CLPS 1.0 ceiling is $2.6B over 10 years. |
| NASA LTV "8 km/h" or "15 km/h" speed requirement | Not found in any source. What is documented: Moon Base guide target "large crewed and uncrewed rovers with speeds of 10 km/hr"; Astrolab CLV-1 ">6 mph on level terrain"; Lunar Outpost Pegasus ">9 mph"; SpacePolicyOnline paraphrase of LTV goals "up to 10 km/h, slopes up to 20 degrees, as many as 200 km". |
| LTV "20 km range per sortie" | Reported (Military & Aerospace Electronics, 2023 RFP coverage) as "carry at least 800 kg ... for distances up to 20 km without the need to recharge". I could not open the RFP itself; **med**. |
| Moon Base phase dates "pre-2029 / 2029–2032 / post-2032" | The extracted text of the April 2026 User's Guide PDF contains the phase table (launches, landings, kg) but the year labels appear only in graphics I could not extract. Dates come from NBC News / NASASpaceflight / Exterra coverage of the 26 May 2026 announcement: Phase 1 through 2029, Phase 2 2029–2032, Phase 3 2032 onward. **med**. |
| "~4 metric tons to south pole before 2029, 25 launches, 21 landings" | **Confirmed** in the guide: "25 LAUNCHES / 21 LANDINGS / ~4,000 KG payload to surface" for Phase 1. |
| "marketplace for lunar logistics" sentence on page 14 | **Confirmed** verbatim (see Section 2). |
| IM-1 "$118M for ~100 kg NASA payloads" | $118M confirmed (SpacePolicyOnline). NASA payload mass for IM-1 not published; Nova-C class capacity is ~100–130 kg. $/kg for IM-1 is therefore an estimate. |
| Firefly Blue Ghost "$101M" | Confirmed: $93.3M original, adjusted to $101.5M, for 10 NASA payloads totalling ~94 kg. |
| Deloitte "7% real discount rate" | Appeared in a search snippet summarizing the Deloitte report; the Fortune article I fetched did not state it. **med**. |
| Rover energy Wh/km | No published Wh/km for a modern 1-t-class lunar rover on regolith was found. I give an LRV-derived design value and a rule-of-thumb specific-energy figure, both **low**. |
| Toyota Lunar Cruiser launch year | Sources give 2029 (older) vs 2031 (NASA–JAXA 2024 agreement, not fetched here). Mass and payload are unpublished. |
| SpaceX "$100M per metric ton" lunar cargo price | Reported by multiple outlets as taken from spacex.com/humanspaceflight/moon; the page itself failed to resolve for me (DNS). **med**. |
| IDA report PDF | ida.org returned 404; findings taken from the IDA landing page / New Space Economy summaries. |

---

## 1. Parameter table (items 1–4 and 7 of the brief)

### 1A. Cargo demand and masses (NASA architecture documents)

| Parameter | Value / range | Unit | Source URL | Conf. |
|---|---|---|---|---|
| Element/cargo mass range needing surface mobility (Foundational Exploration) | 500 – 15,000 | kg | https://www.nasa.gov/wp-content/uploads/2024/06/acr24-lunar-mobility-drivers-and-needs.pdf (Summary; Key Takeaways) | high |
| Small deployed demonstrations | 500 – 2,000 | kg per asset | same, p.4 | high |
| Recurring logistics per crewed surface mission | 2,000 – 6,000 | kg per mission | same, p.4 ("logistics elements needed on a recurring basis can total 2,000 to 6,000 kg per crewed surface mission") | high |
| Habitation-class elements | 12,000 – 15,000 | kg per element | same, p.4 | high |
| Crew size / duration basis for logistics demand | 4 crew, ~30 days | – | same, p.4 | high |
| Demand–capacity mismatch | 1,000 – 15,000 kg per asset, for 50 – 5,000 m | kg; m | same, p.4 | high |
| Aggregate surface cargo demand (Foundational Exploration) | 2,000 – 10,000 (takeaway) / 2,500 – 10,000 (body text) | kg per year | https://www.nasa.gov/wp-content/uploads/2024/06/acr24-lunar-surface-cargo.pdf | high |
| Occasional large single deliveries (rovers, habitats) | up to 15,000 | kg per delivery | same | high |
| Crewed-mission cadence assumed for logistics | annual | – | same ("assumed to occur on an annual basis") | high |
| Cargo lander capability gap | 500 – 12,000 | kg | same; and https://www.nasa.gov/wp-content/uploads/2025/02/2025-ia-workshop-wp-lunar-logistics-and-mobility.pdf slide 4 | high |
| Packaging/carrier overhead on logistics items | 75 – 150 | % of base item mass | https://www.nasa.gov/wp-content/uploads/2024/01/lunar-logistics-drivers-and-needs.pdf p.3 | high |
| Composition of open-loop logistics mass | water+gases ≈50 %; food/crew consumables ≈20 %; EVA support ≈20 %; spares/utilization = remainder | % | same, p.3 | high |
| Frequency of relocation tasks | "single operations for large elements to multiple trips per year for logistics containers" | – | mobility paper p.5 | high |
| Lunar surface functions allocated to mobility (ADD Rev-B) | 22 | functions | 2025 workshop slide 5 | high |
| Lunar surface functions allocated to cargo delivery (ADD Rev-A) | 17 (9 key, 8 potential) | functions | 2025 workshop slide 3 | high |

### 1B. Distances, slopes, site geometry

| Parameter | Value / range | Unit | Source URL | Conf. |
|---|---|---|---|---|
| Landing site to point-of-use range envelope | 5 – 5,000 | m | mobility paper, Key Takeaways | high |
| Separation from lander shadowing | tens of m (paper) / >50 m (2025 slides) | m | mobility paper p.3; 2025 slides slide 7 | high |
| Separation for lander blast ejecta / ascent | >1,000 | m | mobility paper p.3 | high |
| Aggregation of elements into habitation zone from regional landing areas | up to 5,000 | m | mobility paper p.3 | high |
| LTV "standard road traversal map" | ~4 | km | 2025 slides, slide 7 | high |
| Multi-region mobility (not in scope of Foundational Exploration) | hundreds to thousands | km | 2025 slides, slide 7 | high |
| Slopes on landing-zone-to-habitation traverses | up to 20 | degrees | mobility paper p.4 | high |
| Slopes "common" at south pole | >10 | degrees | mobility paper p.5 ("analogous to unimproved mountain passes") | high |
| Habitation/hibernation points | higher elevations / ridge tops (upslope) to minimize darkness | – | mobility paper p.4 | high |
| Cooperative cargo move distance used in robotics literature | up to 5 | km | https://arxiv.org/abs/2510.18766 | high |

### 1C. Current and near-term mobility capacity (rover fleet parameters)

| Parameter | Value / range | Unit | Source URL | Conf. |
|---|---|---|---|---|
| Surface mobility capability "expressed in the architecture" | 800 | kg (uncrewed cargo) | mobility paper, Key Takeaways | high |
| Planned capability (all elements) | ~1,500 | kg | mobility paper p.2 | high |
| LTV transport capability (2025 slides) | 800 (full performance) / 1,600 (reduced performance) | kg | 2025 slides, slide 5 | high |
| Largest element any planned mobility asset can relocate | 1,600 ("No mobility assets exist that can relocate large elements") | kg | 2025 slides, slide 5 | high |
| Apollo LRV payload | 490 | kg | https://nssdc.gsfc.nasa.gov/planetary/lunar/apollo_lrv.html | high |
| NASA LTV requirement: payload | ≥800 | kg | https://www.militaryaerospace.com/home/article/14294649/nasa-seeks-industry-proposals-for-next-gen-lunar-terrain-vehicle (RFP coverage) | med |
| NASA LTV requirement: range without recharge | up to 20 | km | same | med |
| NASA LTV requirement: service life | ≥10 | years | same; https://aerospaceamerica.aiaa.org/comparing-the-artemis-moon-buggy-contenders/ | med |
| NASA LTV requirement: lunar night survival | ≥85 (min) / 125 (desired) | hours of darkness | same (M&AE) | med |
| NASA LTV requirement: crew | 2 suited astronauts + robotic arm | – | https://www.nasa.gov/press-release/nasa-pursues-lunar-terrain-vehicle-services-for-artemis-missions/ | high |
| LTVS contract ceiling | 4.6 | $B over 15 yr | Aerospace America (above); SpaceQ PwC summary | med |
| LTV goals as reported at award | up to 10 km/h; slopes up to 20°; as many as 200 km | km/h; deg; km | https://spacepolicyonline.com/news/nasa-awards-initial-moon-base-rover-and-lander-contracts/ | med |
| Moon Base Phase 1 target: large rovers speed | 10 | km/h | https://www.nasa.gov/wp-content/uploads/2026/04/moon-base-architecture-users-guide.pdf p.9 | high |
| Moon Base Phase 1 target: cargo unload/reposition | "100s of kg" (FN-M-401, FN-M-501); demo manipulation of 10 kg | kg | same, p.8 | high |
| Astrolab CLV-1 (FLEX-derived) mass | ~2,000 (≈907 kg) | lb | https://www.nasa.gov/news-release/nasa-provides-update-on-moon-base-rovers-landers-missions/ | high |
| Astrolab CLV-1 speed | >6 (≈9.7 km/h) on level terrain | mph | same | high |
| Astrolab contract value | 219 | $M | same | high |
| Lunar Outpost Pegasus speed | >9 (≈14.5 km/h); manual/autonomous/teleoperated | mph | same | high |
| Lunar Outpost Pegasus life | up to 1 | year | same | high |
| Lunar Outpost contract value | 220 | $M | same | high |
| LTV delivery (Blue Origin Mark 1 lander) | 188 + 280.4 option | $M | same | high |
| LTV delivery date | 2028 | – | same | high |
| Astrolab FLEX payload | 1,500 (2022–23 statements) / 1,600 (Aerospace America 2025) / 2,000 (astrolab.space, two top-deck interfaces) + 3 m³ underslung | kg | https://www.astrolab.space ; https://www.theregister.com/2022/03/12/astrolab_flex/ ; Aerospace America | med (conflicting) |
| Astrolab FLEX nominal speed | 15 (hoped ~18+ record) | km/h | The Register 2022 | med |
| Astrolab FLEX lunar night survival | up to 300 h total darkness | hours | The Register 2022 (company statement) | med |
| Astrolab FLEX continuous crewed driving | 8 | hours | same | med |
| Astrolab FLEX rover mass (2022 prototype statement) | ~500 | kg | VOA / Euronews 2022 coverage | low |
| Lunar Outpost MAPP | 5–10 kg rover; 15 kg payload; 0.1 m/s | kg; m/s | https://lunaroutpost.com/rovers | high |
| Lunar Outpost MAPP-Ultra | 30 kg rover; 30 kg payload; 1 m/s | kg; m/s | same | high |
| Lunar Outpost HL-MAPP | 250 kg rover; 200 kg payload; 3 m/s; night survival yes | kg; m/s | same | high |
| Lunar Outpost Eagle payload | undisclosed; Pegasus is "less than half the size of Eagle" with reduced logistics capacity | – | Aerospace America 2025; https://payloadspace.com/lunar-outpost-closes-30m-series-b-unveils-new-rover/ | med |
| Intuitive Machines Moon RACER payload | 2 crew + 400 kg on vehicle; trailer +800 kg (IM) / 1,200 kg with trailer (Aerospace America) | kg | https://www.intuitivemachines.com/post/intuitive-machines-holds-key-nasa-review-ahead-of-2025-ltv-award ; Aerospace America | med (conflicting) |
| JAXA/Toyota Lunar Cruiser | 10,000 km range; 2 crew (4 emergency); 6.0×5.2×3.8 m; 13 m³; fuel cell; launch ~2029–2031 | km; m | https://www.universetoday.com/articles/toyota-is-building-a-pressurized-lunar-rover-for-japan ; https://www.toyota-europe.com/news/2023/lunar-cruiser-future-mobility | med |
| JAXA pressurized rover cargo transport capability | TBR (to be resolved) | – | 2025 slides, slide 5 | high |
| ispace payload pricing | 1.5 (lander) / 3.5 (rover) | $M per kg | https://holistic-r.org/report/9348/ (2023 analyst report of ispace pricing) | med |
| ispace Starship capacity purchase | 500 kg for ~$50M (~$100k/kg), NET 2030 | kg; $ | https://universemagazine.com/en/lunar-logistics-moves-to-a-shared-flight-model/ | med |

### 1D. Cargo landers, Earth-to-surface cost, programme scale

| Parameter | Value / range | Unit | Source URL | Conf. |
|---|---|---|---|---|
| Moon Base Phase 1 | 25 launches; 21 landings; ~4,000 kg to surface; first crewed Moon Base mission | – | Moon Base User's Guide p.3 | high |
| Moon Base Phase 2 | 27 launches; 24 landings; ~60,000 kg; CLPS capability to 5 MT; semi-annual crewed missions; uncrewed cargo return | – | same | high |
| Moon Base Phase 3 | 29 launches; 28 landings; ~150,000 kg; CLPS capability to 8 MT; continuous crew presence; regolith manipulation/site prep | – | same | high |
| Phase dates | P1 through 2029; P2 2029–2032; P3 2032+ | – | https://www.nbcnews.com/science/space/nasa-announces-moon-missions-prepare-build-base-rcna346349 ; https://www.exterrajsc.com/p/the-moon-base-supply-chain-is-already | med |
| Phase 1 lander target | "landers with two metric ton cargo delivery capability to the lunar South Pole region" | t | Moon Base User's Guide p.10 | high |
| Phase 1 power target | 5 kW generation+storage; survive 120+ h darkness; RTG survive-the-night demo | kW; h | same, p.10 | high |
| Phase 1 comms target | >500 Mbps via second relay constellation | Mbps | same, p.8 | high |
| Moon Base funding (reported) | ~$10B Phase 1 + ~$10B Phase 2 | $ | Exterra (above) | low |
| CLPS 1.0 IDIQ ceiling | 2.6 over 10 years (through Nov 2028) | $B | https://en.wikipedia.org/wiki/Commercial_Lunar_Payload_Services | high |
| CLPS current task-order delivered mass | 0.07 – 0.475 | t | 2025 slides slide 4; surface-cargo paper Table 1 | high |
| HDL (Human-class Delivery Lander) capability | 12,000 or 15,000 | kg | surface-cargo paper Table 1 | high |
| ESA Argonaut | up to 2,100 | kg | same | high |
| Blue Moon Mark 1 payload | 3,000 | kg | https://en.wikipedia.org/wiki/Blue_Moon_(spacecraft) | med |
| Astrobotic Griffin payload | ~625 | kg | https://space.com/astrobotic-technology | med |
| Nova-C payload | ~100 – 130 | kg | https://en.Wikipedia.com/wiki/Nova-C | med |
| Moon Base II (Griffin-1 + Astrolab FLIP) cargo | ">1,100 lb" (NASA release) / ">500 kg" (Isaacman speech) | – | NASA release 26-046; https://www.nasa.gov/blogs/workforce-updates/2026/05/27/moon-base-announcement-speech-may-26-2026-administrator-isaacman-remarks/ | high |
| CLPS task orders: Peregrine M1 | 79.5 → 108 | $M | Wikipedia CLPS table | med |
| CLPS task orders: IM-1 | 77 → 118; 6 NASA payloads | $M | same; https://spacepolicyonline.com/news/a-valentines-day-launch-for-the-next-u-s-moon-mission/ | high |
| CLPS task orders: Blue Ghost M1 | 93.3 → 101.5; 10 payloads, ~94 kg → ≈$1.08M/kg (derived) | $M; kg | https://spacepolicyonline.com/news/firefly-lands-on-the-moon/ | high / derived |
| CLPS task orders: IM-2 | ~47 | $M | Wikipedia CLPS table | med |
| CLPS task orders: IM-3 | 77.5; ~92 kg → ≈$0.84M/kg (derived) | $M; kg | same | med / derived |
| CLPS task orders: Griffin M1 (VIPER delivery) | 199.5 original → 323 after 3 mods | $M | https://www.nasaspaceflight.com/… (search summary); https://democrats-science.house.gov/download/hsst-to-nasa_-viper-termination-letter | med |
| CLPS task orders: IM-5 | 180.4 | $M | https://www.exterrajsc.com/p/clps-at-30-the-revenue-math-behind | med |
| CLPS task orders: Blue Ghost M2 | 112 | $M | Wikipedia CLPS table | med |
| CLPS programme: 8 task orders combined (Feb 2024) | 984.3; avg cost growth 26 %; avg slip 14 months | $M; %; months | Exterra CLPS-at-30 (citing NASA OIG) | med |
| CLPS effective $/kg (small landers) | ~0.6 – 1.2 | $M per kg | derived from rows above; median "$1.2M/kg across nine disclosed contracts" per https://universemagazine.com/en/lunar-logistics-moves-to-a-shared-flight-model/ | low |
| CLPS 2 ceiling | 10 (15 with options); proposals due 30 Jun 2026 | $B | https://govcontractfinder.com/contracts/commercial-lunar-payload-services-clps-2-0-80jsc026clps2 ; GovConWire | med |
| SpaceX Starship lunar cargo price (published) | 100 per metric ton (= $100k/kg), cargo flights NET 2028 | $M / t | spacex.com/humanspaceflight/moon as quoted by https://universemagazine.com/en/lunar-logistics-moves-to-a-shared-flight-model/ and others | med |
| Starship HLS cargo capacity claim | up to 100 | t to lunar surface | https://spaceflightnow.com/2020/04/30/companies-release-new-details-on-human-rated-lunar-lander-concepts/ (Shotwell) | med |
| NextSTEP-2 Appendix R logistics & mobility studies | $24M; 9 companies; 27 Jan 2025 | $M | https://www.militaryaerospace.com/commercial-aerospace/article/55263422/nasa-announces-contract-awardees-for-lunar-logistics-and-mobility-tech | high |

### 1E. Operating environment and vehicle performance

| Parameter | Value / range | Unit | Source URL | Conf. |
|---|---|---|---|---|
| Apollo LRV mass / payload | 210 / 490 | kg | https://nssdc.gsfc.nasa.gov/planetary/lunar/apollo_lrv.html | high |
| LRV batteries | 2 × 36 V, 121 Ah Ag-Zn (non-rechargeable) → ≈8.7 kWh total (derived) | V; Ah; kWh | same; https://en.wikipedia.org/wiki/Lunar_Roving_Vehicle | high / derived |
| LRV design range | 92 | km | Wikipedia LRV | high |
| LRV design top speed / record | 10 / 18 (Apollo 17) | km/h | same | high |
| LRV average moving speed (derived) | A15: 27.8 km in 3 h 02 min ≈ 9.2; A16: 26.7 km in 3 h 26 min ≈ 7.8; A17: 35.9 km in 4 h 26 min ≈ 8.1 | km/h | NSSDC distances + Wikipedia drive times | derived, med |
| LRV max distance from LM | 5.0 / 4.5 / 7.6 (A15/16/17) | km | NSSDC | high |
| LRV slope capability | 20–23° favorable conditions; 25° max; 30 cm obstacle; 70 cm crevasse | deg; cm | https://www.nasa.gov/wp-content/uploads/static/history/alsj/LRVSysHndbkA15RevA.pdf (via search summary) | med |
| LRV drive motors | 4 × 0.19 kW (0.25 hp) | kW | NSSDC | high |
| LRV design energy intensity (derived) | ≈95 (8.7 kWh / 92 km) for ~700 kg gross | Wh/km | derived | low |
| Rule-of-thumb locomotion specific energy | ~1 J/(kg·m) (≈278 Wh/km per tonne gross) | J/(kg·m) | https://arxiv.org/abs/1706.05356 (per search summary; not confirmed in abstract) | low |
| VIPER speed | 10–20 cm/s traversing; 5–10 cm/s science; 1 cm/s mission average ("waiting 90 % of time") | cm/s | https://science.nasa.gov/mission/viper/lunar-operations/ ; https://www.nasa.gov/wp-content/uploads/2022/05/overview_of_mission_planning_for_the_viper_rover.pdf | high |
| VIPER slope limit | 15 nominal; 25–30 when necessary | degrees | same | high |
| VIPER distance goal / mission | 20 km; 100+ days; 10 cm obstacles | km; days | VIPER mission-planning deck | high |
| VIPER darkness endurance | 50 h min-power; ~9.5 h working in shadow with drill | hours | same | high |
| VIPER planning uncertainties (Monte Carlo) | speed 20–50 % below CBE; power draw +20 % CBE; activity duration +20 %; start delay σ=2 h; battery −20 % | – | same, slide 28 | high |
| Modern autonomous rover speeds | 0.1 m/s (MAPP); 1 m/s (MAPP-Ultra); 3 m/s (HL-MAPP); 1.1 m/s avg target (GMV RAPID, ESA) | m/s | lunaroutpost.com/rovers ; https://gmv.com/en/node/7687 | high / med |
| Lunokhod top speed | ~0.5 | m/s | https://arxiv.org/pdf/2306.02167 (via search summary) | low |
| Synodic month (lunar day) | 29.53 → night ≈14.77 Earth days at equator | days | https://nssdc.gsfc.nasa.gov/planetary/factsheet/moonfact.html | high |
| Surface temperature (equatorial) | 95 – 390 | K | same | high |
| Surface gravity | 1.62 | m/s² | same | high |
| South-pole darkness design targets | 85 h min / 125 h desired (LTV RFP); 120+ h (Moon Base Phase 1 power); 300 h (Astrolab claim); ≤50 h (VIPER site criterion) | hours | rows above | med–high |
| Illumination: Shackleton rim | some sites ~94 % of lunar year; two points 8 km apart "combined ~94 %"; three rim points collectively >90 % | % | https://en.wikipedia.org/wiki/Peak_of_eternal_light ; https://www.lroc.asu.edu/images/1105 | med |
| Illumination: Shackleton–de Gerlache connecting ridge | up to ~90 %, nowhere permanent | % | LROC "Islands in the Dark" | med |
| PSR temperatures | as low as −203 °C (~70 K) surface (NASA); ~38 K subsurface at LCROSS site (Diviner) | °C; K | https://www.nasa.gov/reference/moonbase-environment/ ; Paige et al. 2010, Science 330:479, doi:10.1126/science.1187726 | high |
| Earth–Moon one-way light time | ~1.3 (1.255 at mean distance, derived) | s | https://www.rmg.co.uk/stories/space-astronomy/how-far-away-moon | high |
| Round-trip light time | ~2.6 | s | https://ar5iv.arxiv.org/html/1710.01254 (Mellinkoff et al. 2018) | high |
| Realistic one-way latency incl. protocol processing (Artemis) | "up to 10 s one way" | s | https://ntrs.nasa.gov/citations/20250000703 (via search summary) | med |
| Effect of 2.6 s latency on telerobotic exploration time | +150 % | % | Mellinkoff et al. 2018 (above) | high |
| NASA LTV teleoperation study delays | 0, 4, 6, 8 s; target 6 km in 24 h; 20–100 h operator training; workload rises significantly vs 0 s | s; km/day | https://ntrs.nasa.gov/citations/20240001217 ; https://ntrs.nasa.gov/citations/20240011392 | high (numbers of effective speed not released) |
| VIPER Earth-contact blackout | "two full weeks a month" (libration / Earth below horizon) | – | science.nasa.gov VIPER lunar operations | high |
| Dust effects (Apollo catalogue) | 9 categories: vision obscuration, false instrument readings, coating/contamination, loss of traction, clogging of mechanisms, abrasion, thermal control, seal failures, inhalation | – | https://ntrs.nasa.gov/citations/20050160460 (Gaier 2005) | high |
| Dust incidents on LRV | fender extension lost (A16), damaged & field-repaired (A17) | – | Wikipedia LRV | high |
| Dust quantitative degradation rates for mechanisms | none published | – | – | n/a |
| Moon Base guide environmental statements | Sun low on horizon; "prolonged periods of extreme cold and dark"; "new shadows cast by emplaced infrastructure" | – | Moon Base guide p.7 | high |

---

## 2. Key verbatim passages for citation

**NASA Moon Base Architecture User's Guide (NP-2026-04-6806-HQ, April 2026)**, https://www.nasa.gov/wp-content/uploads/2026/04/moon-base-architecture-users-guide.pdf

- p.3 table: "PHASE 01 — 25 LAUNCHES — 21 LANDINGS — ~4,000 KG payload to surface — Achieve high-rate, reliable surface access. Establish ground truth for Moon Base landing sites. Technology Experiment and test capabilities. First crewed Moon Base mission." / "PHASE 02 — 27 LAUNCHES — 24 LANDINGS — ~60,000 KG — Establish initial lunar surface infrastructure. Increase CLPS payload mass capability to 5MT. Uncrewed cargo demonstrations. Semi-annual Crewed Missions." / "PHASE 03 — 29 LAUNCHES — 28 LANDINGS — ~150,000 KG — Regolith manipulation and site preparation. Increase CLPS payload mass capability to 8MT. [cargo] return capabilities. Continuous Crew Presence."
- p.6 (Market Enablers): "NASA will use bulk buys and multiple awards to enable cost savings in long lead parts purchases, reassurance of capital investments, and diffusion of base costs. This economy of scale offers sustained business cases to industry partners, empowering the development of a lunar marketplace and economy, while assuring effective allocation of taxpayer investments in civil space."
- p.6: "NASA and its partners can start building scalable, shared systems for power, logistics, communications, and navigation."
- p.7 (Interoperability): "The Moon Base will comprise systems developed and built by many providers across government, industry, academia, and the international community. Ensuring compatibility of the interfaces between these systems will accelerate progress..."
- p.8 (Autonomous Systems and Robotics, Phase 1 targets): "Demonstration of capabilities to unload and manipulate cargo (10kg) on the surface." Functional gaps: "FN-A-104 Perform robotic manipulation of payloads, logistics, and/or equipment on the lunar surface. FN-A-105 Interface robotic system(s) with logistics carriers on the lunar surface. FN-A-401 Command and control asset(s) from Earth on the lunar surface during uncrewed periods. FN-M-401 Unload a limited amount of cargo (100s of kg) on the lunar surface. FN-M-501 Reposition a limited amount of cargo (100s of kg) in the south pole region on the lunar surface."
- p.9 (Logistics Systems): "Systems and capabilities related to the packaging, handling, transportation, staging, storage, tracking, and transfer of items and cargo for the Moon Base."
- p.9 (Mobility Systems, Phase 1 targets): "Deployment of small utility rovers and hoppers to conduct science, reconnaissance, and resource discovery. Deployment of large crewed and uncrewed rovers with speeds of 10 km/hr." Gaps: "FN-M-302 Enable local unpressurized surface mobility in sunlit areas and non-PSRs ... FN-M-304 Enable local unpressurized surface mobility in PSRs at the south pole region."
- p.10 (Power): "Demonstrate 5 kW power generation and storage, as well as survival through 120+ hours of darkness." (Transportation): "Deployment of landers with two metric ton cargo delivery capability to the lunar South Pole region." Gaps FN-T-201 "100s of kg", FN-T-202 "1000s of kg".
- p.13 (Tech gaps): "Moving Logistics — Manipulating and transferring lunar surface logistics requires robotic systems for off-loading and manipulating payloads, as well as long-duration packaging systems for protecting cargo." "Manipulating Regolith — ... large-scale excavation and construction." "Wireless Charging — Demonstrating wireless charging for rovers..." "Electrical [Mating] — ... dust-tolerant connections."
- p.14 (Mars-forward, Logistics Strategies): "Long-term habitation at the Moon Base means developing long-term strategies for deep space logistics. **Fostering a marketplace for lunar logistics will empower government and industry to develop the capabilities and operational competencies needed to support crewed missions to the Red Planet.**"
- p.15 (Partnership priorities): "SURFACE HABITATION / LOGISTICS SERVICES / SMALL MOBILITY AND ROBOTICS / HIGH CAPACITY MOBILITY SYSTEMS / LARGE CARGO DELIVERY AND RETURN / RESOURCE MAPPING AND RECONNAISSANCE / SAMPLE STORAGE AND CONDITIONING / ADVANCED NAVIGATION CAPABILITIES".

**NASA "Lunar Mobility Drivers and Needs" (2024 Architecture Concept Review white paper)**, https://www.nasa.gov/wp-content/uploads/2024/06/acr24-lunar-mobility-drivers-and-needs.pdf

- "Current capabilities planned for lunar surface operations are limited to transporting approximately 1,500 kg of cargo."
- "One of the largest drivers of mobility needs on the lunar surface is moving cargo from its landing site to its point of use. ... Separation from lander shadowing (tens of meters); Lander blast ejecta constraints (>1,000 m) ...; Support for aggregation of elements in ideal habitation zones from available regional landing areas (up to 5,000 m)."
- "Traverses from landing zones to habitation zones could encounter slopes of up to 20 degrees."
- "Smaller deployed demonstrations are estimated in the 500-to-2,000 kg range. However, logistics elements needed on a recurring basis can total 2,000 to 6,000 kg per crewed surface mission. Further, ... habitation systems ... could deploy in the 12,000-to-15,000 kg range."
- "the LTV ... is limited to 800 kg of uncrewed cargo mass. The Apollo-era Lunar Roving Vehicle (LRV) was designed to hold a payload of an additional 490 kg. ... current demand and mobility capacity are mismatched on the order of 1,000 to 15,000 kg per asset for ranges of 50 to 5,000 m."
- "mobility assets will require sufficient autonomy and/or tele-robotic operation capability to operate throughout the year."
- "Slopes of more than 10 degrees are common at the lunar South Pole ... Wheel and soil interactions for large mobility systems do not scale linearly with transported mass ... Transportation becomes exponentially more difficult at the upper end of the mass range."
- "A stated capability for mass relocation means little if the interfaces between the mobility element and the cargo are incompatible. Establishing shared standards that support autonomy would empower mission planners to better stage cargo and assets prior to crew arrival ... The ability of mobility systems to manipulate cargo elements will be a key factor. Access to offload cargo landers, leveling to support surface docking of multiple elements, and support to mated power or other types of connectors could be key drivers ... **The ability of multiple robotic mobility systems to work together may also be an enabling feature for future systems.**"
- Key takeaways: "ranges of 5 to 5,000 m"; "limited to 800 kg ... as massive as 12,000 kg or more"; "Large-scale mobility is not simply scaled up small-scale mobility."

**NASA "Lunar Logistics, Mobility, and Cargo" workshop slides (K. Goodliff, ESDMD-SAO, Feb 2025)**, https://www.nasa.gov/wp-content/uploads/2025/02/2025-ia-workshop-wp-lunar-logistics-and-mobility.pdf
- "Mobility mass demand ranges are similar to those of landed cargo demand, but capabilities are not available for cargo or assets greater than 1,600 kg; No mobility assets exist that can relocate large elements (e.g., initial surface habitat)."
- "NASA anticipates an aggregate demand for lunar surface cargo on the order of 2,000 to 10,000 kg per year."

**NextSTEP-2 Appendix R awards (27 Jan 2025, $24M, 9 companies)** — topic areas: logistical carriers; logistics handling and offloading; logistics transfer; staging, storage, and tracking; trash management; surface cargo and mobility; integrated strategies. Companies: Blue Origin; Intuitive Machines; Leidos; Lockheed Martin; MDA Space; Moonprint; Pratt Miller Defense; Sierra Space; Special Aerospace Services. Source: https://www.militaryaerospace.com/commercial-aerospace/article/55263422/nasa-announces-contract-awardees-for-lunar-logistics-and-mobility-tech (NASA release URL returned 404 at time of access).

---

## 3. Annotated bibliography (items 5, 6, 8) — 45 entries

Format: Authors (Year). Title. Venue. URL. — Contribution.

### 3A. Space logistics modeling and lunar surface operations (item 5)

1. de Weck, O. L., Simchi-Levi, D., et al. (2006). *Interplanetary Supply Chain Management and Logistics Architectures* (NASA-funded MIT/JPL/Payload Systems/USA project, $3.8M, 2005–2007). Project summary: https://news.mit.edu/2007/spacenet — Established the "interplanetary supply chain" framing: a network of nodes (Earth, LEO, lunar orbit, lunar surface) and arcs with time-varying costs; produced the SpaceNet tool.
2. Gralla, E. L., Shull, S., & de Weck, O. L. (2006). A Modeling Framework for Interplanetary Supply Chains. *AIAA SPACE 2006*. https://www.researchgate.net/publication/228656529_A_Modeling_Framework_for_Interplanetary_Supply_Chains — Defines nodes, elements, commodities and processes for exploration logistics; the conceptual basis of SpaceNet.
3. Shull, S. A. (2007). *Integrated Modeling and Simulation of Lunar Exploration Campaign Logistics*. S.M. thesis, MIT (advisor de Weck). https://dspace.mit.edu/handle/1721.1/39711 — Applies SpaceNet to lunar outpost build-up; finds sustainable lunar missions need uncrewed cargo resupply and ~90 days of consumables reserve at the base. Treats the surface as a single node.
4. Taylor, C., Song, M., Klabjan, D., de Weck, O. L., & Simchi-Levi, D. (2007). Modeling Interplanetary Logistics: A Mathematical Model for Mission Planning. *AIAA SpaceOps 2006 / AIAA 2006-5735*. https://research.polyu.edu.hk/en/publications/modeling-interplanetary-logistics-a-mathematical-model-for-missio/ — Time-expanded network MILP for mission-level commodity flows (first of the MCNF line).
5. Lee, G., Jordan, E., Shishko, R., de Weck, O., Armar, N., & Siddiqi, A. (2008). SpaceNet: Modeling and Simulating Space Logistics. *AIAA SPACE 2008*. https://www.academia.edu/103335757/SpaceNet_Modeling_and_Simulating_Space_Logistics — Describes SpaceNet v1.3/2.0: discrete-event simulation of campaigns, process groups, nested elements and cargo sharing; identifies logistical infeasibilities. (Author list from memory of AIAA 2008-7747; venue verified, author list not re-verified.)
6. Ho, K. (2015). *Dynamic Network Modeling for Spaceflight Logistics with Time-Expanded Networks*. Ph.D. thesis, MIT (advisor de Weck). https://dspace.mit.edu/handle/1721.1/98557 — Time-expanded, multi-commodity flow MILP for campaign design; shows 45–50 % IMLEO reductions from propulsion/ISRU combinations.
7. Ho, K., de Weck, O. L., Hoffman, J. A., & Shishko, R. (2014). Dynamic Modeling and Optimization for Space Logistics Using Time-Expanded Networks. *Acta Astronautica* 105(2), 428–443. (Not fetched; citation from memory — verify DOI 10.1016/j.actaastro.2014.10.026.) — Journal version of the time-expanded network approach applied to human Mars/lunar campaigns.
8. Ishimatsu, T., de Weck, O. L., Hoffman, J. A., Ohkami, Y., & Shishko, R. (2016). Generalized Multicommodity Network Flow Model for the Earth–Moon–Mars Logistics System. *Journal of Spacecraft and Rockets* 53(1), 25–38. https://dspace.mit.edu/handle/1721.1/110236 — Generalized MCNF with commodity transformations (ISRU, propellant); the standard cislunar logistics optimization reference.
9. Jagannatha, B. B., & Ho, K. (2020). Event-Driven Network Model for Space Mission Optimization with High-Thrust and Low-Thrust Spacecraft. *Journal of Spacecraft and Rockets* 57(3). https://arxiv.org/abs/1904.09364 — Event-driven (not uniformly time-stepped) MILP; case study is a cislunar propellant resupply chain supporting multiple lunar surface access missions.
10. Chen, H., Sarton du Jonchay, T., Hou, L., & Ho, K. (2021). Multi-Fidelity Space Mission Planning and Infrastructure Design Framework for Space Resource Logistics. *Journal of Spacecraft and Rockets* 58(2). https://arxiv.org/abs/1910.04265 — Couples ISRU infrastructure sizing with network logistics at multiple fidelities for lunar campaigns.
11. Gollins, N., & Ho, K. (2024). Hierarchical Framework for Space Exploration Campaign Schedule Optimization. *Journal of Spacecraft and Rockets*. https://repository.gatech.edu/entities/publication/df3da1fb-62d8-4307-b12d-e6b2e7a0e5fb — GA over campaign schedules, each evaluated by a time-expanded MCNF MILP; Artemis case studies on vehicle availability and launch windows.
12. Gkaravela, E., Lee, H. W., & Chen, H. (2025). Distributed Space Resource Logistics Architecture Optimization under Economies of Scale. *Journal of Spacecraft and Rockets* (accepted). https://arxiv.org/abs/2504.16385 — Piecewise-linear cost MILP comparing distributed vs centralized ISRU in cislunar space; introduces economies of scale into space logistics network design.
13. Jones, C., Clark, M., Pensado, A., Ivanco, M., Reeves, D., Judd, E., & Klovstad, J. (2019). Cost Breakeven Analysis of Lunar ISRU for Human Lunar Surface Architectures. *IAC-19, D4.5*. https://iafastro.directory/iac/archive/browse/IAC-19/D4/5/49197/ — Parametric model of lunar-produced vs Earth-delivered propellant/consumables; breakeven driven by lunar campaign scale and ISRU system lifetime (>5 yr autonomous operation).
14. Johnson, A. W. (2010). *An Integrated Traverse Planner and Analysis Tool for Future Lunar Surface Exploration* (SEXTANT). S.M. thesis, MIT. https://dspace.mit.edu/handle/1721.1/59560 — Single-agent (astronaut or rover) path optimization over lunar DEMs minimizing distance, time or energy with sun-position-dependent thermal/power modeling.
15. (Authors not verified; TU Munich group) (2020). Lunar Traverse Planning with Integrated Thermal Simulation (TherMoS X). *ICES 2020*. https://ttu-ir.tdl.org/items/120e9fdb-39fe-4ad8-aee3-7fd0dbad0c28 — A*-based rover traverse optimization at two south-polar sites with full energy and thermal state simulation.
16. (Authors not verified) (2026). Dynamic Illumination-Constrained Spatio-Temporal A* (DIC3D-A*) path planning for polar rovers. *Remote Sensing* 18(2), 310. https://doi.org/10.3390/rs18020310 — Joint slope/distance/illumination cost in a time-dependent 3-D search for south-polar rover routing.
17. Shirley, M., & Balaban, E. (2022). An Overview of Mission Planning for the VIPER Rover. NASA presentation, 2 Jun 2022. https://www.nasa.gov/wp-content/uploads/2022/05/overview_of_mission_planning_for_the_viper_rover.pdf — Strategic/tactical traverse planning with MCTS over macro-actions and Monte-Carlo stress testing (speed, power, DSN availability uncertainties); the best public example of stochastic planning parameters for a polar rover.
18. Litaker, H. L., Li, Z. Q., Beaton, K. H., & Lewis, J. F. (2024/2025). Lunar Terrain Vehicle (LTV) Remote Teleoperation Studies Under Four Lunar Communication Latencies. NASA NTRS. https://ntrs.nasa.gov/citations/20240001217 ; https://ntrs.nasa.gov/citations/20240011392 — Earth-based operators drove a simulated LTV under 0/4/6/8 s delays against a 6 km-per-24 h goal; all succeeded but workload rose sharply; 20–100 h training recommended.
19. Mellinkoff, B. J., Bailey, W., Spydell, M. M., & Burns, J. O. (2018). Quantifying Operational Constraints of Low-Latency Telerobotics for Planetary Surface Operations. https://ar5iv.arxiv.org/html/1710.01254 — 2.6 s round-trip latency increased exploration time by 150 % relative to near-real-time control.
20. Krawciw, A., Antonyshyn, L., Lilge, S., Olmedo, N., Rehmatullah, F., Desjardins-Goulet, M., Toupin, P., & Barfoot, T. D. (2025, rev. 2026). Sharing the Load: Autonomous Multi-Rover Cargo Transport. arXiv:2510.18766. https://arxiv.org/abs/2510.18766 — Two 800 kg path-to-flight rovers jointly carry a 475 kg shared payload up to 5 km via distributed MPC and lidar teach-and-repeat; mean separation error 9.2 cm. Motivated explicitly by Artemis habitat relocation.
21. Mishra, A., Neppel, E., Santra, S., Jonquières, A., Naufal, M. A., Uno, K., & Yoshida, K. (2026). Distributed Multi Robot Lunar Cargo Transportation via Phase Decomposed Reinforcement Learning. *IROS 2026*. https://arxiv.org/abs/2607.00160 — Lift/transport/place phases learned as joint-state policies for modular wheel-arm units; field tests at a JAXA facility.
22. Zhang, Y., Li, C., Zheng, Z., Ouyang, C., Sun, P., Guo, Y., Li, S., & Jing, H. (2024). Research on Task Allocation Method for Multi-Agent Systems on the Moon with a Distributed Architecture. *IAC-24, A3.IP.160*. https://iafastro.directory/iac/archive/browse/IAC-24/A3/IP/86984/ — Improved CBAA for lunar transport/construction robots with payload-dependent speed and energy, task priorities and collision radii; single-owner cooperative fleet, no economic layer.
23. Martinez Rocamora, B., Kilic, C., Tatsch, C., Pereira, G. A. S., & Gross, J. N. (2023). Multi-robot cooperation for lunar In-Situ resource utilization. *Frontiers in Robotics and AI*. https://www.frontiersin.org/journals/robotics-and-ai/articles/10.3389/frobt.2023.1149080/full — Centralized task planner + decentralized controllers for 2 scouts, 2 excavators, 2 haulers in NASA Space Robotics Challenge Phase 2.
24. Lamassoure, E. (2001). *A Framework to Account for Flexibility in Modeling the Value of On-Orbit Servicing for Space Systems*. S.M. thesis, MIT. https://dspace.mit.edu/handle/1721.1/32522 — Customer-side vs provider-side price overlap test for whether an on-orbit servicing market can exist; a template for "is there a feasible price band" analysis of a lunar logistics market.
25. Sullivan, B. R. (2005). *Technical and Economic Feasibility of Telerobotic On-Orbit Satellite Servicing*. Ph.D. thesis, Univ. of Maryland. https://drum.lib.umd.edu/handle/1903/2330 — Economic model of a servicing marketplace with demand uncertainty; precedent for space-services market feasibility studies.

### 3B. Multi-robot task allocation and market-based coordination (item 6)

26. Gerkey, B. P., & Matarić, M. J. (2004). A Formal Analysis and Taxonomy of Task Allocation in Multi-Robot Systems. *International Journal of Robotics Research* 23(9), 939–954. https://robotics.usc.edu/publications/347 — ST/MT × SR/MR × IA/TA taxonomy; links MRTA to assignment and scheduling theory. Lunar heavy-cargo moves are MR (multi-robot) tasks under this taxonomy.
27. Dias, M. B., Zlot, R., Kalra, N., & Stentz, A. (2006). Market-Based Multirobot Coordination: A Survey and Analysis. *Proceedings of the IEEE* 94(7), 1257–1270. https://www.ri.cmu.edu/publications/market-based-multirobot-coordination-a-survey-and-analysis-2 — Survey of auction/market mechanisms for robot teams; notes most "markets" are cooperative single-owner constructs, not true multi-owner economies.
28. Choi, H.-L., Brunet, L., & How, J. P. (2009). Consensus-Based Decentralized Auctions for Robust Task Allocation. *IEEE Transactions on Robotics* 25(4), 912–926. https://dspace.mit.edu/handle/1721.1/52330 — CBAA and CBBA: decentralized auction + consensus guaranteeing conflict-free assignment; the baseline decentralized dispatcher in most later lunar MRTA work.
29. Korsah, G. A., Stentz, A., & Dias, M. B. (2013). A Comprehensive Taxonomy for Multi-Robot Task Allocation. *International Journal of Robotics Research* 32(12), 1495–1512. https://www.ri.cmu.edu/publications/a-comprehensive-taxonomy-for-multi-robot-task-allocation — iTax: adds interrelated utilities and constraints (ND/ID/XD/CD) to the Gerkey–Matarić axes.
30. Khamis, A., Hussein, A., & Elmogy, A. (2015). Multi-robot Task Allocation: A Review of the State-of-the-Art. *Studies in Computational Intelligence* 604, 31–51, Springer. https://pure.kfupm.edu.sa/en/publications/multi-robot-task-allocation-a-review-of-the-state-of-the-art/ — Reviews optimization-based vs market-based MRTA with open problems.
31. Nunes, E., Manner, M., Mitiche, H., & Gini, M. (2017). A Taxonomy for Task Allocation Problems with Temporal and Ordering Constraints. *Robotics and Autonomous Systems* 90, 55–70. https://www-users.cs.umn.edu/~gini/papers/NunesRAS.pdf — Organizes MRTA with time windows and precedence, drawing on vehicle routing and scheduling; directly relevant to lander-arrival-driven cargo tasks.
32. Rizk, Y., Awad, M., & Tunstel, E. W. (2019). Cooperative Heterogeneous Multi-Robot Systems: A Survey. *ACM Computing Surveys* 52(2), Art. 29. https://scholarworks.aub.edu.lb/items/2ca4c068-f8fa-49b0-905b-a84744415147 — Survey of heterogeneous teams incl. task allocation, coalition formation and communication constraints.
33. Aziz, H., Pal, A., Pourmiri, A., Ramezani, F., & Sims, B. (2022). Task Allocation Using a Team of Robots. *Current Robotics Reports*. https://arxiv.org/abs/2207.09650 — Unified formal model of MRTA variants; surveys optimization and market-based approaches.
34. Chakraa, H., Guérin, F., Leclercq, E., & Lefebvre, D. (2023). Optimization Techniques for Multi-Robot Task Allocation Problems: Review on the State-of-the-Art. *Robotics and Autonomous Systems* 168, 104492. — Up-to-date review of exact, heuristic and learning methods for MRTA.
35. Karam, R., Nguyen, A. A., Lin, R., Martin, D. R., Morales, D., Butler, B. A., & Egerstedt, M. (2026). Collaboration in Multi-Robot Systems: Taxonomy and Survey over Frameworks for Collaboration. arXiv:2603.23898. https://arxiv.org/abs/2603.23898 — Distinguishes cooperation/coordination/collaboration; argues collaboration (joint capability) is under-formalized.
36. Caplice, C., & Sheffi, Y. (2003). Optimization-Based Procurement for Transportation Services. *Journal of Business Logistics* 24(2). https://caplice.mit.edu/wp-content/uploads/2019/08/Paper-13-CapliceSheffi_OptimizationBasedProcurement_JBL2003.pdf — Shipper-run combinatorial auctions for truckload lanes; carriers bid bundles reflecting economies of scope.
37. Sheffi, Y. (2004). Combinatorial Auctions in the Procurement of Transportation Services. *Interfaces* 34(4), 245–252. https://ideas.repec.org/a/inm/orinte/v34y2004i4p245-252.html — Practice-oriented account of why TL freight suits combinatorial auctions.
38. Caplice, C., & Sheffi, Y. (2006). Combinatorial Auctions for Truckload Transportation. In Cramton, Shoham & Steinberg (eds.), *Combinatorial Auctions*, MIT Press. https://caplice.mit.edu/wp-content/uploads/2019/08/Paper-12-Caplice-and-Sheffi-2006.pdf — Canonical reference for freight procurement auction design (annual strategic, not spot dispatch).
39. Arslan, A. M., Agatz, N., Kroon, L., & Zuidwijk, R. (2019). Crowdsourced Delivery — A Dynamic Pickup and Delivery Problem with Ad Hoc Drivers. *Transportation Science* 53(1). https://pubsonline.informs.org/doi/10.1287/trsc.2017.0803 — Rolling-horizon matching of parcels to ad hoc drivers; template for multi-operator dynamic dispatch.
40. Ekbatani, F., Niazadeh, R., Golari, M., et al. (2026). Non-Exclusive Notifications for Ride-Hailing at Lyft II: Simulations and Marketplace Analysis. arXiv:2603.21531. https://arxiv.org/abs/2603.21531 — Large-scale discrete-event marketplace simulator calibrated on Lyft traces to compare dispatch protocols; methodological precedent for DES of a dispatch marketplace (but with dense supply).

### 3C. Market and demand studies (item 8)

41. PwC (Jan 2026). *Building the Lunar Economy: Sectorial Forecasts and Market Opportunity*. Summary: https://spaceq.ca/pwc-report-lunar-economy-projected-to-generate-up-to-us127-billion-by-2050/ — Cumulative revenue US$93.9–127.3B (2026–2050) across mobility, communication, habitation, energy, water; infrastructure investment US$72.7–88.5B; transportation 70–80 % of infrastructure cost 2026–2035 falling to 50–60 % by 2046–2050; cites LTVS contract value US$4.6B.
42. Deloitte (28 Aug 2026). *Building the Lunar Economy*. Summary: https://fortune.com/2026/08/28/deloitte-sees-a-566-billion-lunar-economy-by-2050/ — Cumulative value US$343B (conservative) to US$566B (accelerated) through 2050 (NPV in 2026 dollars, 7 % real discount per secondary summaries); core infrastructure US$282B of which transportation US$206B; governments as "anchor investors and customers".
43. Colvin, T. J., Crane, K. W., Lindbergh, R., & Lal, B. (2020). *Demand Drivers of the Lunar and Cislunar Economy*. IDA Science and Technology Policy Institute, D-13219, for NASA. https://ida.org/research-and-publications/publications/all/d/de/demand-drivers-of-the-lunar-and-cislunar-economy — Through 2040, "private demand alone appeared insufficient to support most companies whose revenue depended entirely on lunar customers"; two dominant variables: government expenditures and Earth–cislunar–surface transport cost.
44. NASA (27 Jan 2025). NASA Awards $24 Million for Lunar Logistics and Mobility Studies (NextSTEP-2 Appendix R). Coverage: https://www.militaryaerospace.com/commercial-aerospace/article/55263422/nasa-announces-contract-awardees-for-lunar-logistics-and-mobility-tech — Nine firms study carriers, handling/offloading, transfer, staging/storage/tracking, trash, surface cargo & mobility, integrated strategies. Signals that offloading and surface cargo movement are unsolved procurement gaps.
45. Analysys Mason (2025–2026). 'Moon-as-a-service' business models: the next leap for commercial space players. https://www.analysysmason.com/research/content/articles/moon-economy-space-nsi015/ — Argues for service-based (not asset-sale) lunar business models; government procurement is the only dependable near-term demand.

Primary NASA documents used as sources (not numbered above): Moon Base Architecture User's Guide (Apr 2026); Lunar Mobility Drivers and Needs (2024); Lunar Surface Cargo (2024); Lunar Logistics Drivers and Needs (2023); Lunar Logistics, Mobility, and Cargo workshop slides (Feb 2025); NASA release 26-046 (26 May 2026); Isaacman Moon Base speech (26 May 2026); Gaier (2005) NASA/TM-2005-213610 dust effects.

---

## 4. Gaps in prior work (one page)

**What exists.** Three mature literatures touch the problem. (i) *Campaign-level space logistics* (SpaceNet; Ho/de Weck time-expanded multi-commodity network flow; Jagannatha & Ho; Gollins & Ho) optimizes Earth–orbit–surface commodity flows over months to years. The lunar surface is one node; intra-surface movement is at most a fixed "surface transfer" process with no fleet, terrain, lighting or dispatch model. (ii) *Multi-robot task allocation* (Gerkey & Matarić; Korsah et al.; CBBA; Nunes et al.; recent surveys) provides taxonomies and decentralized auction algorithms, and a handful of lunar-specific variants (Zhang et al. IAC-24 improved CBAA; NASA Space Robotics Challenge teams). All assume a single owner with a common objective; "market" is a metaphor for a cooperative heuristic, and economic quantities (prices, revenue, provider profit) are absent. (iii) *Cooperative cargo transport control* (Krawciw et al. 2025; Mishra et al. 2026) solves the vehicle-level problem of two rovers carrying one 475 kg load up to 5 km, but not which rovers, when, for which lander, at what price. Separately, *terrestrial freight marketplaces* (Caplice & Sheffi auctions; crowdsourced delivery; ride-hailing DES) assume dense supply, cheap repositioning and no 14-day blackouts; and *lunar economy studies* (PwC, Deloitte, IDA) are top-down revenue forecasts with no operational model.

**What nobody has modeled (as far as this search found):**

1. **A neutral, multi-operator dispatch marketplace for lunar surface cargo.** NASA's own guide calls for "fostering a marketplace for lunar logistics" and for shared "scalable, shared systems for power, logistics, communications, and navigation", and the mobility white paper says "the ability of multiple robotic mobility systems to work together may also be an enabling feature". No paper simulates a platform where several rover operators (Astrolab, Lunar Outpost, Intuitive Machines, JAXA, ispace) with heterogeneous vehicles bid on or are dispatched to cargo jobs generated by landers from different providers. The IDA finding that private demand alone cannot sustain lunar-only firms makes shared utilization of sparse fleets a first-order economic question, yet no bottom-up model links fleet size, utilization, wait time and $/kg-km surface haul price.
2. **Sparse-fleet regime.** Phase 1–2 of the Moon Base implies 2–6 large rovers serving ~4 t then ~60 t of landed cargo (21 → 24 landings) with per-asset masses of 500–15,000 kg against 800–1,600 kg vehicle capacity. This is the opposite of the ride-hailing/freight regime: jobs routinely exceed any single vehicle (MR tasks requiring coalitions), vehicle count is comparable to job count, and idle repositioning is energy-expensive. No MRTA or marketplace study has characterized mechanism performance in this regime.
3. **Lunar-specific stochastic environment in a fleet DES.** Lander arrivals are lumpy (CLPS schedule slip averages 14 months), lighting windows and 85–300 h darkness periods gate operations, Earth-visibility blackouts ("two full weeks a month" at some sites) interrupt teleoperation, slopes to 20° and dust degrade speed and energy, and effective speed varies 20–50 % below best estimate (VIPER planning assumptions). Traverse planners (SEXTANT, TherMoS, DIC3D-A*) handle one vehicle on one path; campaign MILPs are deterministic. A DES that combines these at the fleet level with an explicit dispatch mechanism does not exist in the literature found.
4. **Interface/offloading as a scheduling resource.** NASA repeatedly lists cargo offloading, standard interfaces, leveling and power mating as gaps (FN-A-104/105, FN-M-401/501; Appendix R topics). No model treats offloading capability (cranes, arms, interface compatibility between a given lander and a given rover) as a constraint on who can serve which job.
5. **Mechanism comparison under multi-owner incentives.** Comparing centralized optimal assignment, decentralized consensus auctions (CBBA), posted-price first-come dispatch, and combinatorial spot auctions — on both system efficiency (ton-km delivered per lunar day, cargo dwell time at the pad) and provider outcomes (utilization fairness, revenue) — has not been done for any planetary surface setting.

**Data gaps the paper should state openly:** no published Wh/km for ≥1 t rovers on regolith (only an LRV-derived ~95 Wh/km and a ~1 J/(kg·m) rule of thumb); no published offloading durations; no failure or dust-degradation rates for rover mechanisms; NASA LTV teleoperation effective speeds under 4–8 s latency were measured but not released; LTV requirements (800 kg, 20 km, 10 yr, 85–125 h night) are known only through RFP press coverage; CLPS 2 pricing per kg is not yet observable. These should be treated as sensitivity parameters rather than point estimates in the DES.
