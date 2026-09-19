---
marp: true
theme: paperline-pitch
size: 16:9
paginate: true
header: '![Daytona](assets/daytona-glyph.svg)'
footer: '김건동'
title: 'GateTrace · 3분 해커톤 발표'
description: '연구·논문 개발에 사용할 입력과 데이터의 검증 근거를 추적하며, 센서 CSV 구현 사례를 시연하는 GateTrace 해커톤 발표 자료'
---

<!-- _class: cover -->

<img class="cover-hero" src="assets/gatetrace-researcher-hero.png" alt="연구 데이터를 검증하는 연구자 일러스트" />
<div class="cover-copy">
<p class="eyebrow">DAYTONA 서울 해커톤 · 개인 프로젝트</p>
<h1>GateTrace</h1>
<p class="lead">연구·논문 워크플로의 입력을 사용 전에 검증하고,<br>판정 근거를 남기는 연구 데이터 게이트</p>
<p class="author">김건동</p>
</div>

<!--
00:00-00:15
GateTrace는 연구와 논문에 투입할 입력과 데이터를 사용 전에 검증하고, 판정 근거를 남깁니다. 오늘은 센서 CSV 구현으로 그 흐름을 보여드립니다.
-->

---

<!-- _class: problem -->

<p class="eyebrow">01 · 연구 문제</p>

# 입력의 오류는 연구 결과로 전파됩니다

<div class="problem-grid visual-problem-grid">
<div class="problem-statement">
<p class="quote-mark">“</p>
<p>데이터 오염은 분석·학습의 신뢰를 흔들고,<br>근거 없는 차단은 유효한 자료를 버립니다.</p>
<p class="problem-detail">연구자는 사용 전에 무엇을 검사했고 왜 막혔는지 확인해야 합니다.</p>
</div>
<figure class="research-users-visual">
<img src="assets/gatetrace-research-users.png" alt="실험, 설문, 머신러닝 데이터를 다루는 세 연구자 일러스트" />
<figcaption>사용자 예시 · 실험 데이터 · 설문 데이터 · 학습 데이터</figcaption>
</figure>
</div>

<!--
00:15-00:30
검증되지 않은 입력은 분석과 학습 결과를 흔듭니다. 반대로 근거 없는 차단은 쓸 수 있는 자료를 버리게 해 연구 속도와 신뢰를 함께 낮춥니다.
-->

---

<!-- _class: solution -->

<p class="eyebrow">02 · 현재 검증의 한계</p>

# ‘통과 / 실패’만으로는 연구에 쓸 수 없습니다

<div class="flow-strip">
<div><b>01</b><strong>검사 범위</strong><span>어떤 규칙을 적용했는지 불명확</span></div>
<div><b>02</b><strong>실행 환경</strong><span>입력과 검증 코드가 섞여 있음</span></div>
<div><b>03</b><strong>실패 이유</strong><span>게이트별 근거가 흩어져 있음</span></div>
<div><b>04</b><strong>재현 정보</strong><span>같은 실행을 추적하기 어려움</span></div>
</div>

<p class="takeaway">판정과 실행 근거가 함께 남아야 다시 검토할 수 있습니다.</p>

<!--
00:30-00:45
기존 검증은 규칙과 실행 환경, 실패 이유가 흩어져 재검토가 어렵습니다. 생성형 설명이 판정과 섞이면 누가 결정을 내렸는지도 불분명해집니다.
-->

---

<!-- _class: solution -->

<p class="eyebrow">03 · GateTrace 해결 방식</p>

# 연구자는 목표와 입력만 선택합니다

<div class="flow-strip diagram-flow">
<div><b>01</b><strong>목표 입력</strong><span>검증하려는 연구 목적을 작성</span></div>
<div><b>02</b><strong>샘플 선택</strong><span>오늘 구현: 정상·데이터 오염 센서 CSV</span></div>
<div><b>03</b><strong>격리 실행</strong><span>제한 명세에 따라 Daytona에서 검사</span></div>
<div><b>04</b><strong>결과 검토</strong><span>판정 · 근거 · 실행 추적 키</span></div>
</div>

<p class="takeaway">APPROVED 또는 QUARANTINED와 그 이유를 한 화면에서 확인합니다.</p>

<!--
00:45-01:00
연구자는 목표와 입력을 선택하고 실행합니다. GateTrace는 제한 명세, 격리 검증, 판정 근거를 한 흐름으로 연결해 승인과 격리 이유를 바로 보여줍니다.
-->

---

<!-- _class: demo -->

<p class="eyebrow">04 · 센서 CSV 라이브 데모</p>

# 데이터 오염은 근거와 함께 격리됩니다

<div class="demo-grid">
<div class="media-slot">
<img src="../output/playwright/gatetrace-result-contaminated-en.png" alt="GateTrace 영문 오염 데이터 실제 Daytona 실행 결과" />
</div>
<div class="demo-script">
<p class="demo-index">A · 입력</p>
<h2>데이터 오염 샘플</h2>
<p>오늘의 표형 데이터 구현 사례</p>
<p class="demo-index">B · 판정</p>
<h2>QUARANTINED</h2>
<p>4개 중 3개 게이트 실패</p>
<p class="demo-index">C · Daytona</p>
<h2>26.217초</h2>
<p>샌드박스 ID와 실행 시간 기록</p>
</div>
</div>

<!--
01:00-01:15
오늘 구현 예시는 센서 CSV입니다. 데이터 오염 샘플은 네 게이트 중 세 곳에서 실패했고, 실제 Daytona 실행 결과 QUARANTINED로 격리됐습니다.
-->

---

<!-- _class: integration -->

<p class="eyebrow">05 · 스폰서 연동과 안전 경계</p>

# 생성은 제한하고, 판정은 결정론적으로 실행합니다

<div class="architecture-line compact-architecture">
<div><small>입력</small><strong>연구 목표</strong></div><i>›</i>
<div class="accent-node"><small>NOSANA</small><strong>제한 명세</strong></div><i>›</i>
<div><small>DAYTONA</small><strong>격리 검증</strong></div><i>›</i>
<div class="accent-node"><small>판정</small><strong>APPROVED<br>QUARANTINED</strong></div><i>›</i>
<div><small>기록</small><strong>근거와 추적 키</strong></div>
</div>

<div class="architecture-proof">
<p><b>Nosana</b> 연구 목표를 허용된 4개 게이트와 설명으로 변환</p>
<p><b>Daytona</b> 호스트 소유 검증기를 격리 실행하고 결과 회수·삭제</p>
</div>

<p class="integration-note"><strong>안전 경계</strong> Nosana의 생성 결과는 Daytona의 결정론적 판정값을 바꿀 수 없습니다.</p>

<!--
01:15-01:30
Nosana는 제한 명세와 설명만 만들고, Daytona의 결정론적 검증기가 판정합니다. 생성 모델은 APPROVED나 QUARANTINED를 바꿀 수 없습니다.
-->

---

<!-- _class: evidence -->

<p class="eyebrow">06 · 확인된 결과</p>

# 라이브 결과와 재현 경로를 공개했습니다

<div class="result-lines">
<div><span>로컬 계약</span><strong>18 / 18 테스트 통과 <small>외부 서비스는 대역</small></strong></div>
<div><span>DAYTONA 실연동</span><strong>정상 APPROVED 4/4 · 데이터 오염 QUARANTINED 1/4</strong></div>
<div><span>VERCEL 라이브</span><strong>gatetrace-daytona.vercel.app</strong></div>
<div><span>공개 저장소</span><strong>github.com/geondongkim/gatetrace-daytona</strong></div>
</div>

<p class="source-note">Nosana 실연동 확인 · qwen/qwen3.8-27b · Daytona 정상/데이터 오염 실행과 샌드박스 삭제 확인</p>

<!--
01:30-01:45
열여덟 개 계약 테스트와 정상·데이터 오염 판정, 삭제를 확인했습니다. 앱과 재현 코드는 Vercel과 공개 저장소에서 확인할 수 있습니다.
-->

---

<!-- _class: impact -->

<p class="eyebrow">기대효과</p>

# 검증 가능한 연구 입력 채택 체계

<div class="impact-grid">
<div><b>01</b><strong>데이터 오염 차단</strong><span>실패 입력을 분석·학습 전에 격리</span></div>
<div><b>02</b><strong>판정 재검토</strong><span>요청·실행·게이트 근거를 함께 보존</span></div>
<div><b>03</b><strong>채택 기준 확장</strong><span>같은 게이트를 후속 데이터에도 적용</span></div>
</div>

<p class="impact-roadmap"><strong>다음 단계</strong> 근거 보존형 데이터 증강 · 생성 이력과 검증 근거를 보존하고 통과분만 채택</p>
<p class="impact-boundary">기대효과 및 확장 계획입니다. 문서형 입력은 별도 검증기 구현 후 확장합니다.</p>

<!--
01:45-02:00
GateTrace는 데이터 오염을 사전에 막고 판정 근거를 재검토 가능하게 만듭니다. 다음 단계는 증강 데이터에도 같은 게이트를 적용해 통과분만 채택하는 것입니다.
-->
