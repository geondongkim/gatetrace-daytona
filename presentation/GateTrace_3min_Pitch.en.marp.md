---
marp: true
theme: paperline-pitch
size: 16:9
paginate: true
header: '![Daytona](assets/daytona-glyph.svg)'
footer: 'Geondong Kim'
title: 'GateTrace · 3-Minute Hackathon Pitch'
description: 'GateTrace pitch deck showing how research inputs are validated with traceable evidence before use, demonstrated with a sensor CSV workflow.'
---

<!-- _class: cover -->

<img class="cover-hero" src="assets/gatetrace-researcher-hero.png" alt="Illustration of a researcher validating research data" />
<div class="cover-copy">
<p class="eyebrow">DAYTONA HACKSPRINT SEOUL · SOLO BUILD</p>
<h1>GateTrace</h1>
<p class="lead">Research inputs verified before use,<br>with evidence preserved for every verdict</p>
<p class="author">Geondong Kim</p>
</div>

<!--
00:00-00:15
GateTrace validates inputs before they enter a research or paper-development workflow and preserves the evidence behind every verdict. Today I will demonstrate that flow with a sensor CSV.
-->

---

<!-- _class: problem -->

<p class="eyebrow">01 · RESEARCH PROBLEM</p>

# Input errors propagate into research results

<div class="problem-grid visual-problem-grid">
<div class="problem-statement">
<p class="quote-mark">“</p>
<p>Contaminated inputs weaken analysis and training,<br>while unexplained blocking discards valid evidence.</p>
<p class="problem-detail">Researchers need to know what was checked and why an input was blocked before they use it.</p>
</div>
<figure class="research-users-visual">
<img src="assets/gatetrace-research-users.png" alt="Illustration of researchers working with experimental, survey, and machine learning data" />
<figcaption>Example users · Experimental data · Survey data · Training data</figcaption>
</figure>
</div>

<!--
00:15-00:30
Unverified inputs can distort analysis and model training. Unexplained blocking also wastes valid material, slowing research while reducing trust in the process.
-->

---

<!-- _class: solution -->

<p class="eyebrow">02 · CURRENT LIMITATION</p>

# Pass or fail alone is not enough for research

<div class="flow-strip">
<div><b>01</b><strong>Check scope</strong><span>The applied rules are unclear</span></div>
<div><b>02</b><strong>Run environment</strong><span>Inputs and verification code are mixed</span></div>
<div><b>03</b><strong>Failure reason</strong><span>Evidence is scattered across tools</span></div>
<div><b>04</b><strong>Reproducibility</strong><span>The same run is difficult to trace</span></div>
</div>

<p class="takeaway">A verdict must travel with its execution evidence.</p>

<!--
00:30-00:45
Existing checks scatter rules, execution context, and failure evidence. When generated explanations are mixed with the verdict, it is also unclear which system made the decision.
-->

---

<!-- _class: solution -->

<p class="eyebrow">03 · GATETRACE SOLUTION</p>

# Researchers only choose a goal and input

<div class="flow-strip diagram-flow">
<div><b>01</b><strong>State the goal</strong><span>Describe the intended research use</span></div>
<div><b>02</b><strong>Select a sample</strong><span>Demo: clean or contaminated sensor CSV</span></div>
<div><b>03</b><strong>Run in isolation</strong><span>Evaluate constrained gates in Daytona</span></div>
<div><b>04</b><strong>Review evidence</strong><span>Verdict, gate evidence, and trace keys</span></div>
</div>

<p class="takeaway">APPROVED or QUARANTINED, with the reason on one screen.</p>

<!--
00:45-01:00
The researcher selects a goal and an input. GateTrace connects a constrained specification, isolated verification, and traceable evidence so the approval or quarantine reason is immediately visible.
-->

---

<!-- _class: demo -->

<p class="eyebrow">04 · LIVE SENSOR CSV DEMO</p>

# A contaminated input is quarantined with evidence

<div class="demo-grid">
<div class="media-slot">
<img src="../output/playwright/gatetrace-result-contaminated-en.png" alt="English GateTrace screen showing an actual Daytona run for contaminated data" />
</div>
<div class="demo-script">
<p class="demo-index">A · INPUT</p>
<h2>Contaminated sensor CSV</h2>
<p>Tabular-data implementation example</p>
<p class="demo-index">B · VERDICT</p>
<h2>QUARANTINED</h2>
<p>Three of four gates failed</p>
<p class="demo-index">C · DAYTONA</p>
<h2>26.217s</h2>
<p>Sandbox ID and duration recorded</p>
</div>
</div>

<!--
01:00-01:15
This implementation uses a sensor CSV. The contaminated sample failed three of four gates, and an actual Daytona run quarantined it with the sandbox ID and gate evidence preserved.
-->

---

<!-- _class: integration -->

<p class="eyebrow">05 · SPONSOR INTEGRATION AND SAFETY</p>

# Generation is constrained; the verdict stays deterministic

<div class="architecture-line compact-architecture">
<div><small>INPUT</small><strong>Research goal</strong></div><i>›</i>
<div class="accent-node"><small>NOSANA</small><strong>Constrained specification</strong></div><i>›</i>
<div><small>DAYTONA</small><strong>Isolated audit</strong></div><i>›</i>
<div class="accent-node"><small>VERDICT</small><strong>APPROVED<br>QUARANTINED</strong></div><i>›</i>
<div><small>RECORD</small><strong>Evidence and trace keys</strong></div>
</div>

<div class="architecture-proof">
<p><b>Nosana</b> Maps the research goal to four allowed gates and explanations</p>
<p><b>Daytona</b> Runs the host-owned verifier in isolation, returns results, and deletes the sandbox</p>
</div>

<p class="integration-note"><strong>SAFETY BOUNDARY</strong> Nosana cannot change Daytona's deterministic verdict.</p>

<!--
01:15-01:30
Nosana produces only the constrained specification and explanation. Daytona runs the deterministic verifier, so a generated response cannot change APPROVED or QUARANTINED.
-->

---

<!-- _class: evidence -->

<p class="eyebrow">06 · VERIFIED RESULTS</p>

# Live results and reproduction paths are public

<div class="result-lines">
<div><span>LOCAL CONTRACT</span><strong>18 / 18 tests passed <small>external services mocked</small></strong></div>
<div><span>DAYTONA LIVE</span><strong>Clean APPROVED 4/4 · contaminated QUARANTINED 1/4</strong></div>
<div><span>VERCEL LIVE</span><strong>gatetrace-daytona.vercel.app</strong></div>
<div><span>PUBLIC REPOSITORY</span><strong>github.com/geondongkim/gatetrace-daytona</strong></div>
</div>

<p class="source-note">Nosana live confirmed · qwen/qwen3.8-27b · Daytona clean/contaminated runs and sandbox deletion verified</p>

<!--
01:30-01:45
Eighteen contract tests passed, and I verified clean and contaminated verdicts plus sandbox deletion. The live app and reproducible code are available on Vercel and GitHub.
-->

---

<!-- _class: impact -->

<p class="eyebrow">EXPECTED IMPACT</p>

# A verifiable adoption gate for research inputs

<div class="impact-grid">
<div><b>01</b><strong>Block contamination</strong><span>Quarantine failed inputs before analysis or training</span></div>
<div><b>02</b><strong>Review every verdict</strong><span>Preserve the request, run, and gate evidence together</span></div>
<div><b>03</b><strong>Extend adoption rules</strong><span>Apply the same gates to later datasets</span></div>
</div>

<p class="impact-roadmap"><strong>NEXT STAGE</strong> Evidence-preserving augmentation · retain provenance and accept only generated samples that pass the gates</p>
<p class="impact-boundary">This is an expected impact and extension plan. Document inputs require a dedicated verifier.</p>

<!--
01:45-02:00
GateTrace blocks contaminated inputs before use and keeps each verdict reviewable. The next stage applies the same gates to augmented data and accepts only candidates that pass.
-->
