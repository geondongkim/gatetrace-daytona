"use strict";

const LANGUAGE_STORAGE_KEY = "gatetrace.language";
const DEFAULT_LANGUAGE = "both";
const SUPPORTED_LANGUAGES = new Set(["ko", "en", "both"]);

const translations = {
  languageKo: { ko: "한국어", en: "Korean" },
  languageEn: { ko: "영어", en: "English" },
  languageBoth: { ko: "한영", en: "KO·EN" },
  languageSelector: { ko: "언어 선택", en: "Language selector" },
  systemReady: { ko: "검증 시스템 준비", en: "Verification system ready" },
  eyebrow: { ko: "산업 AI 데이터 게이트", en: "Industrial AI data gate" },
  heroTitle: { ko: "학습 전에, 데이터를 증명합니다.", en: "Prove the data before it trains the model." },
  heroCopy: {
    ko: "GateTrace는 센서 데이터셋을 격리된 Daytona 샌드박스에서 검사하고, Nosana 모델의 판단과 실행 근거를 하나의 추적 가능한 기록으로 제공합니다.",
    en: "GateTrace inspects sensor datasets in an isolated Daytona sandbox and returns a traceable record of the Nosana model decision and runtime evidence."
  },
  workspaceTitle: { ko: "검증 실행", en: "Run verification" },
  workspaceHint: { ko: "1시간 내 설비 고장 예측을 위한 결정론적 데모입니다.", en: "A deterministic demo for equipment failure prediction within one hour." },
  scenarioLabel: { ko: "시나리오", en: "Scenario" },
  scenarioTitle: { ko: "1시간 내 설비 고장 예측", en: "Equipment failure within one hour" },
  scenarioDescription: { ko: "시계열 센서 데이터 · 이진 분류", en: "Time-series sensor data · binary classification" },
  fixedScenario: { ko: "고정", en: "Fixed" },
  datasetLabel: { ko: "데모 데이터셋", en: "Demo dataset" },
  cleanDataset: { ko: "정상 데이터", en: "Clean data" },
  cleanDatasetDescription: { ko: "정렬되고 완전한 센서 관측값", en: "Ordered, complete sensor observations" },
  contaminatedDataset: { ko: "오염 데이터", en: "Contaminated data" },
  contaminatedDatasetDescription: { ko: "결측, 시간 역전, 미래 라벨 누수", en: "Missing values, time reversal, future-label leakage" },
  expectedPass: { ko: "예상 PASS", en: "Expected PASS" },
  expectedFail: { ko: "예상 FAIL", en: "Expected FAIL" },
  runAudit: { ko: "4개 게이트 검증 실행", en: "Run four-gate audit" },
  runningButton: { ko: "검증 요청 중", en: "Requesting audit" },
  privacyNote: { ko: "데이터는 격리된 실행 환경에서 처리됩니다.", en: "Data is processed in an isolated execution environment." },
  protocolLabel: { ko: "검증 프로토콜", en: "Verification protocol" },
  protocolTitle: { ko: "4단계 실행 흐름", en: "Four-step run flow" },
  stepIntake: { ko: "요청 접수", en: "Request intake" },
  stepIntakeDescription: { ko: "데이터셋과 시나리오 확인", en: "Dataset and scenario check" },
  stepSandbox: { ko: "Nosana 게이트 설계", en: "Nosana gate design" },
  stepSandboxDescription: { ko: "연구 목표에서 검증 규칙 생성", en: "Derive checks from the research goal" },
  stepEvaluate: { ko: "Daytona 격리 검증", en: "Daytona isolated audit" },
  stepEvaluateDescription: { ko: "샌드박스에서 4개 게이트 평가", en: "Evaluate four gates in the sandbox" },
  stepAttest: { ko: "근거 기록", en: "Evidence record" },
  stepAttestDescription: { ko: "Nosana 판단과 실행 정보 결합", en: "Nosana decision and runtime evidence" },
  stateWaiting: { ko: "대기", en: "Waiting" },
  stateProcessing: { ko: "처리 중", en: "Processing" },
  stateComplete: { ko: "완료", en: "Complete" },
  stateError: { ko: "오류", en: "Error" },
  stateUnavailable: { ko: "확인 불가", en: "Unavailable" },
  emptyTitle: { ko: "아직 실행된 검증이 없습니다.", en: "No audit has run yet." },
  emptyDescription: { ko: "데이터셋을 선택하고 검증을 시작하면 실제 API 결과가 여기에 표시됩니다.", en: "Choose a dataset and start the audit; the actual API response will appear here." },
  runningTitle: { ko: "격리된 검증을 실행하고 있습니다.", en: "Running the isolated audit." },
  runningDescription: { ko: "응답이 도착할 때까지 결과를 추정하지 않습니다.", en: "No result is assumed before the response arrives." },
  errorTitle: { ko: "검증을 완료하지 못했습니다.", en: "The audit could not be completed." },
  errorNetwork: { ko: "서버에 연결할 수 없습니다. 연결 상태를 확인한 뒤 다시 시도하세요.", en: "The server could not be reached. Check the connection and try again." },
  errorHttp: { ko: "서버가 검증 요청을 거절했습니다.", en: "The server rejected the audit request." },
  errorInvalid: { ko: "서버 응답에서 유효한 검증 결과를 확인할 수 없습니다.", en: "The server response did not contain a valid audit result." },
  retryButton: { ko: "다시 시도", en: "Try again" },
  verdictPass: { ko: "PASS", en: "PASS" },
  verdictFail: { ko: "FAIL", en: "FAIL" },
  verdictUnknown: { ko: "미확인", en: "UNKNOWN" },
  verdictPassTitle: { ko: "학습 사용 가능", en: "Ready for training" },
  verdictFailTitle: { ko: "학습 사용 차단", en: "Blocked from training" },
  verdictUnknownTitle: { ko: "판정 확인 불가", en: "Verdict unavailable" },
  runIdLabel: { ko: "실행 ID", en: "Run ID" },
  runStatusLabel: { ko: "실행 상태", en: "Run status" },
  gateResultsLabel: { ko: "품질 게이트", en: "Quality gates" },
  gateResultsTitle: { ko: "게이트별 판정", en: "Gate-by-gate verdict" },
  gateResultsHint: { ko: "표시된 판정과 근거는 API 응답에서만 가져옵니다.", en: "Displayed verdicts and evidence come only from the API response." },
  gateRequiredColumns: { ko: "필수 스키마", en: "Required schema" },
  gateMissingRate: { ko: "결측률", en: "Missing rate" },
  gateTimeOrder: { ko: "시간 순서", en: "Time order" },
  gateLeakageColumns: { ko: "누수 열", en: "Leakage columns" },
  gateEvidenceMissing: { ko: "근거가 제공되지 않았습니다.", en: "No evidence was provided." },
  evidenceRequired: { ko: "필수 열", en: "Required columns" },
  evidencePresent: { ko: "확인된 열", en: "Present columns" },
  evidenceMissing: { ko: "누락 열", en: "Missing columns" },
  evidenceColumn: { ko: "검사 열", en: "Checked column" },
  evidenceMissingCount: { ko: "결측 개수", en: "Missing count" },
  evidenceRowCount: { ko: "행 개수", en: "Row count" },
  evidenceMissingRate: { ko: "결측률", en: "Missing rate" },
  evidenceMaxRate: { ko: "허용 상한", en: "Allowed maximum" },
  evidenceTimeColumn: { ko: "시간 열", en: "Time column" },
  evidenceGroupBy: { ko: "그룹 기준", en: "Group by" },
  evidenceViolations: { ko: "순서 위반", en: "Order violations" },
  evidenceForbiddenColumns: { ko: "금지 열", en: "Forbidden columns" },
  evidenceFound: { ko: "탐지된 열", en: "Detected columns" },
  evidenceAdditional: { ko: "추가 근거", en: "Additional evidence" },
  evidenceLabel: { ko: "실행 근거", en: "Execution evidence" },
  evidenceTitle: { ko: "격리 실행 기록", en: "Isolated run record" },
  nosanaModelLabel: { ko: "Nosana 모델", en: "Nosana model" },
  sandboxIdLabel: { ko: "Daytona 샌드박스 ID", en: "Daytona sandbox ID" },
  exitCodeLabel: { ko: "종료 코드", en: "Exit code" },
  durationLabel: { ko: "실행 시간", en: "Duration" },
  notProvided: { ko: "제공되지 않음", en: "Not provided" },
  footerText: { ko: "검증 가능한 데이터 · 격리된 실행 · 추적 가능한 판단", en: "Verifiable data · isolated execution · traceable decisions" }
};

const gateDefinitions = [
  { id: "required_columns", labelKey: "gateRequiredColumns" },
  { id: "missing_rate", labelKey: "gateMissingRate" },
  { id: "time_order", labelKey: "gateTimeOrder" },
  { id: "leakage_columns", labelKey: "gateLeakageColumns" }
];

const elements = {
  form: document.querySelector("#run-form"),
  runButton: document.querySelector("#run-button"),
  retryButton: document.querySelector("#retry-button"),
  empty: document.querySelector("#empty-state"),
  loading: document.querySelector("#loading-state"),
  error: document.querySelector("#error-state"),
  result: document.querySelector("#result-state"),
  errorMessage: document.querySelector("#error-message"),
  timeline: document.querySelector("#timeline"),
  timelineProgress: document.querySelector("#timeline-progress"),
  verdictBadge: document.querySelector("#verdict-badge"),
  verdictTitle: document.querySelector("#verdict-title"),
  summary: document.querySelector("#result-summary"),
  runId: document.querySelector("#run-id"),
  runStatus: document.querySelector("#run-status"),
  gateGrid: document.querySelector("#gate-grid"),
  nosanaModel: document.querySelector("#nosana-model"),
  sandboxId: document.querySelector("#sandbox-id"),
  exitCode: document.querySelector("#exit-code"),
  duration: document.querySelector("#duration")
};

let currentLanguage = readStoredLanguage();
let currentResult = null;
let currentErrorKey = null;
let currentErrorSuffix = "";
let isRunning = false;

function readStoredLanguage() {
  try {
    const stored = window.localStorage.getItem(LANGUAGE_STORAGE_KEY);
    return SUPPORTED_LANGUAGES.has(stored) ? stored : DEFAULT_LANGUAGE;
  } catch (_error) {
    return DEFAULT_LANGUAGE;
  }
}

function writeStoredLanguage(language) {
  try {
    window.localStorage.setItem(LANGUAGE_STORAGE_KEY, language);
  } catch (_error) {
    // Language switching still works when storage is blocked.
  }
}

function translatedValue(key, language = currentLanguage) {
  const entry = translations[key];
  if (!entry) return key;
  if (language === "en") return entry.en;
  return entry.ko;
}

function translationFragment(key) {
  const entry = translations[key];
  const fragment = document.createDocumentFragment();
  if (!entry) {
    fragment.append(document.createTextNode(key));
    return fragment;
  }
  if (currentLanguage !== "both") {
    fragment.append(document.createTextNode(entry[currentLanguage]));
    return fragment;
  }
  fragment.append(document.createTextNode(entry.ko));
  const secondary = document.createElement("span");
  secondary.className = "i18n-secondary";
  secondary.lang = "en";
  secondary.textContent = entry.en;
  fragment.append(secondary);
  return fragment;
}

function translateStaticUi() {
  document.documentElement.lang = currentLanguage === "en" ? "en" : "ko";
  document.querySelectorAll("[data-i18n]").forEach((node) => {
    node.replaceChildren(translationFragment(node.dataset.i18n));
  });
  document.querySelectorAll("[data-i18n-aria]").forEach((node) => {
    node.setAttribute("aria-label", translatedValue(node.dataset.i18nAria));
  });
  document.querySelectorAll(".language-button").forEach((button) => {
    const language = button.dataset.language;
    const key = language === "ko" ? "languageKo" : language === "en" ? "languageEn" : "languageBoth";
    button.textContent = translations[key][language === "both" ? "ko" : language];
    button.setAttribute("aria-pressed", String(language === currentLanguage));
  });
  updateRunButton();
  updateTimelineLabels();
  if (currentErrorKey) renderErrorMessage();
  if (currentResult) renderResult(currentResult);
}

function setLanguage(language) {
  if (!SUPPORTED_LANGUAGES.has(language)) return;
  currentLanguage = language;
  writeStoredLanguage(language);
  translateStaticUi();
}

function updateRunButton() {
  const text = elements.runButton.querySelector("span");
  text.replaceChildren(translationFragment(isRunning ? "runningButton" : "runAudit"));
  elements.runButton.disabled = isRunning;
}

function setVisibleState(name) {
  elements.empty.hidden = name !== "empty";
  elements.loading.hidden = name !== "loading";
  elements.error.hidden = name !== "error";
  elements.result.hidden = name !== "result";
}

function updateTimeline(mode, timeline = null) {
  const serverStates = new Map();
  if (Array.isArray(timeline)) {
    timeline.forEach((step) => {
      if (step && typeof step.key === "string") serverStates.set(step.key, String(step.status || "").toLowerCase());
    });
  }

  let completed = 0;
  elements.timeline.querySelectorAll("li").forEach((item, index) => {
    let state = serverStates.get(item.dataset.step);
    if (!state) {
      if (mode === "complete" && (serverStates.size === 0 || item.dataset.step === "client.intake")) state = "complete";
      else if (mode === "running" && index === 0) state = "processing";
      else state = "waiting";
    }
    const isError = state === "error";
    const isComplete = ["complete", "completed", "done", "pass", "fail"].includes(state);
    const isActive = ["active", "processing", "running"].includes(state);
    item.classList.toggle("is-complete", isComplete);
    item.classList.toggle("is-active", isActive);
    item.classList.toggle("is-error", isError);
    item.dataset.state = isError ? "error" : isComplete ? "complete" : isActive ? "processing" : "waiting";
    if (isComplete || isError) completed += 1;
  });
  elements.timelineProgress.textContent = `${completed} / 4`;
  updateTimelineLabels();
}

function updateTimelineLabels() {
  elements.timeline.querySelectorAll("li").forEach((item) => {
    const key = item.dataset.state === "error" ? "stateError" : item.dataset.state === "complete" ? "stateComplete" : item.dataset.state === "processing" ? "stateProcessing" : "stateWaiting";
    item.querySelector(".step-state").replaceChildren(translationFragment(key));
  });
}

function normalizeVerdict(value) {
  const normalized = String(value || "").trim().toLowerCase();
  if (["pass", "passed", "approved", "true"].includes(normalized)) return "pass";
  if (["fail", "failed", "quarantined", "false"].includes(normalized)) return "fail";
  return "unknown";
}

function normalizeGateCollection(payload) {
  const source = payload.gates ?? {};
  if (Array.isArray(source)) {
    return new Map(source.filter(Boolean).map((gate) => [String(gate.id ?? gate.name ?? "").toLowerCase(), gate]));
  }
  if (source && typeof source === "object") {
    return new Map(Object.entries(source).map(([id, gate]) => [id.toLowerCase(), typeof gate === "object" ? gate : { verdict: gate }]));
  }
  return new Map();
}

function pickLocalized(value, fallbackKey = "notProvided") {
  if (typeof value === "string" && value.trim()) return { ko: value, en: value };
  if (value && typeof value === "object") {
    return {
      ko: String(value.ko ?? value.korean ?? "").trim() || translations[fallbackKey].ko,
      en: String(value.en ?? value.english ?? "").trim() || translations[fallbackKey].en
    };
  }
  return { ...translations[fallbackKey] };
}

function normalizeResponse(payload) {
  if (!payload || typeof payload !== "object" || Array.isArray(payload)) throw new Error("invalid-response");
  const verdict = normalizeVerdict(payload.verdict);
  const summary = pickLocalized(payload.summary);

  return {
    runId: payload.run_id,
    status: payload.status,
    verdict,
    summary,
    gates: normalizeGateCollection(payload),
    timeline: payload.timeline,
    nosanaModel: payload.nosana_model_id,
    sandboxId: payload.sandbox_id,
    exitCode: undefined,
    durationMs: payload.duration_ms
  };
}

function displayValue(value, suffix = "") {
  if (value === undefined || value === null || value === "") return translatedValue("notProvided");
  return `${String(value)}${suffix}`;
}

function appendLocalizedParagraphs(container, localized) {
  container.replaceChildren();
  const add = (language, className) => {
    const paragraph = document.createElement("p");
    paragraph.className = className;
    paragraph.lang = language;
    paragraph.textContent = localized[language];
    container.append(paragraph);
  };
  if (currentLanguage === "ko") add("ko", "summary-ko");
  else if (currentLanguage === "en") add("en", "summary-en");
  else {
    add("ko", "summary-ko");
    add("en", "summary-en");
  }
}

const evidenceLabelKeys = {
  required: "evidenceRequired",
  present: "evidencePresent",
  missing: "evidenceMissing",
  column: "evidenceColumn",
  missing_count: "evidenceMissingCount",
  row_count: "evidenceRowCount",
  missing_rate: "evidenceMissingRate",
  max_rate: "evidenceMaxRate",
  time_column: "evidenceTimeColumn",
  group_by: "evidenceGroupBy",
  violations: "evidenceViolations",
  forbidden_columns: "evidenceForbiddenColumns",
  found: "evidenceFound"
};

function formatEvidenceValue(value, name = "") {
  if (value === null || value === undefined || value === "") return translatedValue("notProvided");
  if (Array.isArray(value)) return value.length ? value.map((item) => formatEvidenceValue(item)).join(", ") : "—";
  if (typeof value === "object") return JSON.stringify(value);
  if (typeof value === "number" && ["missing_rate", "max_rate"].includes(name)) return `${Math.round(value * 10000) / 100}%`;
  return String(value);
}

function renderGateEvidence(container, evidence) {
  container.replaceChildren();
  const entries = evidence && typeof evidence === "object" && !Array.isArray(evidence) ? Object.entries(evidence) : [];
  if (entries.length === 0) {
    container.append(translationFragment("gateEvidenceMissing"));
    return;
  }
  entries.forEach(([name, value]) => {
    const row = document.createElement("p");
    const label = document.createElement("span");
    label.className = "gate-evidence-label";
    label.replaceChildren(translationFragment(evidenceLabelKeys[name] || "evidenceAdditional"));
    const data = document.createElement("code");
    data.textContent = formatEvidenceValue(value, name);
    row.append(label, data);
    container.append(row);
  });
}

function renderGateCards(result) {
  elements.gateGrid.replaceChildren();
  gateDefinitions.forEach((definition, index) => {
    const gate = result.gates.get(definition.id) ?? {};
    const verdict = normalizeVerdict(gate.verdict ?? gate.status ?? gate.passed);
    const card = document.createElement("article");
    card.className = `gate-card is-${verdict}`;

    const topline = document.createElement("div");
    topline.className = "gate-topline";
    const number = document.createElement("span");
    number.className = "gate-number";
    number.textContent = `G${String(index + 1).padStart(2, "0")}`;
    const status = document.createElement("span");
    status.className = "gate-status";
    status.textContent = translatedValue(verdict === "pass" ? "verdictPass" : verdict === "fail" ? "verdictFail" : "verdictUnknown");
    topline.append(number, status);

    const title = document.createElement("h4");
    title.replaceChildren(translationFragment(definition.labelKey));
    const detail = document.createElement("div");
    detail.className = "gate-evidence";
    renderGateEvidence(detail, gate.evidence);
    card.append(topline, title, detail);
    elements.gateGrid.append(card);
  });
}

function renderResult(result) {
  const verdictKey = result.verdict === "pass" ? "verdictPass" : result.verdict === "fail" ? "verdictFail" : "verdictUnknown";
  const titleKey = result.verdict === "pass" ? "verdictPassTitle" : result.verdict === "fail" ? "verdictFailTitle" : "verdictUnknownTitle";
  elements.verdictBadge.className = `verdict-badge is-${result.verdict}`;
  elements.verdictBadge.textContent = translatedValue(verdictKey);
  elements.verdictTitle.replaceChildren(translationFragment(titleKey));
  appendLocalizedParagraphs(elements.summary, result.summary);
  elements.runId.textContent = displayValue(result.runId);
  elements.runStatus.textContent = result.status === "COMPLETED" ? translatedValue("stateComplete") : displayValue(result.status);
  elements.nosanaModel.textContent = displayValue(result.nosanaModel);
  elements.sandboxId.textContent = displayValue(result.sandboxId);
  elements.exitCode.textContent = displayValue(result.exitCode);
  elements.duration.textContent = displayValue(result.durationMs, result.durationMs === undefined || result.durationMs === null ? "" : " ms");
  renderGateCards(result);
}

function renderErrorMessage() {
  elements.errorMessage.replaceChildren(translationFragment(currentErrorKey));
  if (currentErrorSuffix) elements.errorMessage.append(document.createTextNode(` (${currentErrorSuffix})`));
}

function showError(key, suffix = "") {
  currentErrorKey = key;
  currentErrorSuffix = suffix;
  renderErrorMessage();
  updateTimeline("idle");
  setVisibleState("error");
}

async function runAudit() {
  if (isRunning) return;
  const selected = elements.form.elements.dataset.value;
  isRunning = true;
  currentResult = null;
  currentErrorKey = null;
  updateRunButton();
  updateTimeline("running");
  setVisibleState("loading");

  try {
    const response = await fetch("/api/runs", {
      method: "POST",
      headers: { "Content-Type": "application/json", "Accept": "application/json" },
      body: JSON.stringify({
        dataset_id: selected,
        research_goal: "Validate sensor data for one-hour equipment failure prediction."
      })
    });
    if (!response.ok) {
      showError("errorHttp", `HTTP ${response.status}`);
      return;
    }
    let payload;
    try {
      payload = await response.json();
    } catch (_error) {
      showError("errorInvalid");
      return;
    }
    currentResult = normalizeResponse(payload);
    renderResult(currentResult);
    updateTimeline("complete", currentResult.timeline);
    setVisibleState("result");
  } catch (_error) {
    showError("errorNetwork");
  } finally {
    isRunning = false;
    updateRunButton();
  }
}

document.querySelectorAll(".language-button").forEach((button) => {
  button.addEventListener("click", () => setLanguage(button.dataset.language));
});

elements.form.addEventListener("submit", (event) => {
  event.preventDefault();
  runAudit();
});
elements.retryButton.addEventListener("click", runAudit);

updateTimeline("idle");
translateStaticUi();
