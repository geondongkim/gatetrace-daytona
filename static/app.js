"use strict";

const LANGUAGE_STORAGE_KEY = "gatetrace.language";
const DEFAULT_LANGUAGE = "both";
const SUPPORTED_LANGUAGES = new Set(["ko", "en", "both"]);

const translations = {
  languageKo: { ko: "한국어", en: "Korean" },
  languageEn: { ko: "영어", en: "English" },
  languageBoth: { ko: "한영", en: "KO·EN" },
  languageSelector: { ko: "언어 선택", en: "Language selector" },
  productDescriptor: { ko: "연구 데이터 검증", en: "Research data validation" },
  workflowLabel: { ko: "검증 워크플로", en: "Verification workflow" },
  workflowTitle: { ko: "현재 단계와 다음 행동", en: "Current stage and next action" },
  navWelcome: { ko: "시작", en: "Start" },
  navWelcomeHint: { ko: "목표와 흐름 확인", en: "Review the goal and flow" },
  navGoal: { ko: "목표와 데이터셋", en: "Goal & dataset" },
  navGoalHint: { ko: "데모 데이터 선택", en: "Choose demo data" },
  navGates: { ko: "게이트 명세", en: "Gate specification" },
  navGatesHint: { ko: "4개 검사 기준 확인", en: "Review four checks" },
  navRun: { ko: "격리 실행", en: "Isolated run" },
  navRunHint: { ko: "실행 흐름과 요청", en: "Run flow and request" },
  navVerdict: { ko: "판정", en: "Verdict" },
  navVerdictHint: { ko: "결과와 근거 확인", en: "Review results and evidence" },
  navAugmentation: { ko: "증강 실험실", en: "Augmentation lab" },
  navAugmentationHint: { ko: "후보 생성과 계보", en: "Candidates and lineage" },
  openNavigation: { ko: "워크플로 메뉴 열기", en: "Open workflow navigation" },
  currentStageLabel: { ko: "현재 단계", en: "Current stage" },
  demoDataLabel: { ko: "MVP 데모 · 센서 CSV 예시", en: "MVP demo · sensor CSV example" },
  demoBadge: { ko: "데모", en: "Demo" },
  fourGateLabel: { ko: "4개 품질 게이트", en: "Four quality gates" },
  nextActionLabel: { ko: "다음 행동", en: "Next action" },
  nextActionTitle: { ko: "검증할 데모 데이터셋을 선택하세요.", en: "Choose the demo dataset to verify." },
  nextActionDescription: { ko: "정상 또는 데이터 오염 샘플을 선택한 뒤 동일한 4개 게이트를 실행합니다.", en: "Choose the clean or contaminated sample, then run the same four gates." },
  nextActionButton: { ko: "데이터셋 선택", en: "Choose dataset" },
  previousStep: { ko: "이전 단계", en: "Previous step" },
  reviewGatesAction: { ko: "게이트 명세 확인", en: "Review gate specification" },
  prepareRunAction: { ko: "격리 실행 준비", en: "Prepare isolated run" },
  runAnotherAction: { ko: "다른 데모 데이터 검증", en: "Verify another demo dataset" },
  requiredLabel: { ko: "필수", en: "Required" },
  chooseOneLabel: { ko: "하나 선택", en: "Choose one" },
  systemReady: { ko: "검증 시스템 준비", en: "Verification system ready" },
  systemReadyHint: { ko: "요청 전 결과 미정", en: "No verdict before a request" },
  eyebrow: { ko: "연구 데이터 검증 게이트", en: "Research data validation gate" },
  heroTitle: { ko: "연구에 쓰기 전에, 데이터를 증명합니다.", en: "Prove the data before using it in research." },
  heroCopy: {
    ko: "GateTrace는 논문·연구에 사용할 데이터를 제한 명세로 검사하고, Daytona 격리 실행의 판정과 근거를 하나의 기록으로 남깁니다. 이번 MVP는 센서 CSV로 실증합니다.",
    en: "GateTrace validates data for research and paper development against a constrained specification, then preserves the Daytona isolated-run verdict and evidence in one record. This MVP demonstrates the workflow with sensor CSV files."
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
  contaminatedDataset: { ko: "데이터 오염 샘플", en: "Contaminated data" },
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
  stepSandbox: { ko: "Nosana 제한 명세 생성", en: "Nosana constrained specification" },
  stepSandboxDescription: { ko: "연구 목표를 허용된 4개 게이트로 변환", en: "Map the research goal to four allowed gates" },
  stepEvaluate: { ko: "Daytona 격리 검증", en: "Daytona isolated audit" },
  stepEvaluateDescription: { ko: "샌드박스에서 4개 게이트 평가", en: "Evaluate four gates in the sandbox" },
  stepAttest: { ko: "근거 기록", en: "Evidence record" },
  stepAttestDescription: { ko: "Daytona 판정과 Nosana 한영 설명 결합", en: "Combine the Daytona verdict with the Nosana bilingual explanation" },
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
  verdictPassTitle: { ko: "연구 사용 가능", en: "Ready for research use" },
  verdictFailTitle: { ko: "연구 사용 차단", en: "Blocked from research use" },
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
  gateSpecTitle: { ko: "판정을 만드는 4개 검사", en: "Four checks that form the verdict" },
  gateSpecHint: { ko: "선택한 데모 데이터셋에 같은 기준을 적용합니다.", en: "The same criteria are applied to the selected demo dataset." },
  gateRequiredDescription: { ko: "학습에 필요한 센서 열이 모두 있는지 확인합니다.", en: "Confirms that every required sensor column is present." },
  gateMissingDescription: { ko: "특성값 결측 비율이 허용 상한 이내인지 확인합니다.", en: "Checks whether feature missingness stays within the allowed maximum." },
  gateTimeDescription: { ko: "센서 관측 시간이 올바른 순서인지 확인합니다.", en: "Checks whether sensor observations are in chronological order." },
  gateLeakageDescription: { ko: "미래 정보를 노출하는 금지 열이 없는지 확인합니다.", en: "Checks for forbidden columns that expose future information." },
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
  runActionTitle: { ko: "선택한 데이터로 검증을 시작하세요.", en: "Start verification with the selected data." },
  runActionDescription: { ko: "요청은 한 번만 전송되며 처리 중에는 중복 실행이 비활성화됩니다.", en: "The request is sent once, and duplicate runs are disabled while it is processing." },
  honestResultNote: { ko: "응답이 없거나 유효하지 않으면 결과를 추정하지 않고 오류로 표시합니다.", en: "Missing or invalid responses are shown as errors; no result is inferred." },
  verdictSectionTitle: { ko: "판정과 실행 근거", en: "Verdict and execution evidence" },
  verdictStatusLabel: { ko: "현재 판정", en: "Current verdict" },
  emptyAction: { ko: "데모 데이터셋 선택으로 이동", en: "Go to demo dataset selection" },
  nosanaModelLabel: { ko: "Nosana 모델", en: "Nosana model" },
  sandboxIdLabel: { ko: "Daytona 샌드박스 ID", en: "Daytona sandbox ID" },
  exitCodeLabel: { ko: "종료 코드", en: "Exit code" },
  durationLabel: { ko: "실행 시간", en: "Duration" },
  notProvided: { ko: "제공되지 않음", en: "Not provided" },
  footerText: { ko: "연구 데이터 · 격리 실행 · 추적 가능한 판정", en: "Research data · isolated execution · traceable verdict" },
  augmentationTitle: { ko: "증거가 남는 데이터 증강", en: "Evidence-preserving data augmentation" },
  augmentationHint: { ko: "데이터가 부족할 때 후보를 만들되, 같은 4개 게이트를 통과한 묶음만 채택합니다.", en: "When data is scarce, generate candidates but adopt only a batch that passes the same four gates." },
  augmentationProtocol: { ko: "채택 프로토콜", en: "Adoption protocol" },
  trainingOnly: { ko: "학습 파티션 전용", en: "Training partition only" },
  augmentationStepSpec: { ko: "Nosana 제한 명세", en: "Nosana constrained spec" },
  augmentationStepSpecHint: { ko: "허용 변환·수량·시드 제한", en: "Bound transform, count, and seed" },
  augmentationStepGenerate: { ko: "Daytona 후보 생성", en: "Daytona candidate generation" },
  augmentationStepGenerateHint: { ko: "호스트 소유 코드로 제한된 jitter 실행", en: "Run bounded jitter with host-owned code" },
  augmentationStepValidate: { ko: "동일 게이트 재검증", en: "Same-gate re-validation" },
  augmentationStepValidateHint: { ko: "스키마·결측·시간·누수 검사", en: "Schema, missingness, time, and leakage checks" },
  augmentationStepAdopt: { ko: "통과 묶음만 채택", en: "Adopt passing batch only" },
  augmentationStepAdoptHint: { ko: "하나라도 실패하면 전체 격리", en: "Quarantine the batch if any gate fails" },
  lineageLabel: { ko: "보존되는 계보", en: "Preserved lineage" },
  evidenceExtensionLabel: { ko: "기능 확장", en: "Feature extension" },
  augmentationActionTitle: { ko: "선택한 데모 데이터로 후보를 생성합니다.", en: "Generate candidates from the selected demo data." },
  augmentationActionDescription: { ko: "현재 선택된 정상 또는 데이터 오염 샘플을 사용합니다. 판정은 Daytona 결과만 따릅니다.", en: "Uses the currently selected clean or contaminated sample. Only the Daytona result controls adoption." },
  runAugmentation: { ko: "증강 후보 생성·검증", en: "Generate and validate candidates" },
  runningAugmentation: { ko: "증강 실행 중", en: "Running augmentation" },
  augmentationEmpty: { ko: "아직 증강 실행 기록이 없습니다.", en: "No augmentation run has been recorded yet." },
  augmentationRunning: { ko: "격리 환경에서 후보를 생성하고 재검증하고 있습니다.", en: "Generating and re-validating candidates in isolation." },
  augmentationError: { ko: "증강을 완료하지 못했습니다. 결과를 추정하거나 로컬로 우회하지 않습니다.", en: "Augmentation could not be completed. No result is inferred and no local fallback is used." },
  augmentationAdopted: { ko: "후보 채택", en: "Candidates adopted" },
  augmentationQuarantined: { ko: "후보 격리", en: "Candidates quarantined" },
  sourceRowsLabel: { ko: "원본", en: "Source" },
  candidateRowsLabel: { ko: "후보", en: "Candidates" },
  adoptedRowsLabel: { ko: "채택", en: "Adopted" },
  postGateLabel: { ko: "사후 게이트", en: "Post-generation gates" },
  lineagePreviewLabel: { ko: "계보 예시", en: "Lineage sample" }
};

const gateDefinitions = [
  { id: "required_columns", labelKey: "gateRequiredColumns" },
  { id: "missing_rate", labelKey: "gateMissingRate" },
  { id: "time_order", labelKey: "gateTimeOrder" },
  { id: "forbidden_columns", labelKey: "gateLeakageColumns" }
];

const workflowStageKeys = {
  welcome: "navWelcome",
  goal: "navGoal",
  gates: "navGates",
  run: "navRun",
  verdict: "navVerdict",
  augmentation: "navAugmentation"
};

const workflowHashStages = {
  "#welcome": "welcome",
  "#goal-dataset": "goal",
  "#gate-spec": "gates",
  "#isolated-run": "run",
  "#verdict": "verdict",
  "#augmentation-lab": "augmentation"
};

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
  duration: document.querySelector("#duration"),
  navToggle: document.querySelector("#nav-toggle"),
  currentStage: document.querySelector("#current-stage"),
  workflowLinks: document.querySelectorAll("[data-workflow-stage]")
};

Object.assign(elements, {
  augmentationButton: document.querySelector("#augmentation-button"),
  augmentationStatus: document.querySelector("#augmentation-status"),
  augmentationResult: document.querySelector("#augmentation-result"),
  augmentationVerdict: document.querySelector("#augmentation-verdict"),
  augmentationVerdictTitle: document.querySelector("#augmentation-verdict-title"),
  augmentationSourceRows: document.querySelector("#augmentation-source-rows"),
  augmentationCandidateRows: document.querySelector("#augmentation-candidate-rows"),
  augmentationAdoptedRows: document.querySelector("#augmentation-adopted-rows"),
  augmentationGateStatus: document.querySelector("#augmentation-gate-status"),
  augmentationLineage: document.querySelector("#augmentation-lineage"),
  augmentationModel: document.querySelector("#augmentation-model"),
  augmentationSandbox: document.querySelector("#augmentation-sandbox")
});

let currentLanguage = readStoredLanguage();
let currentResult = null;
let currentErrorKey = null;
let currentErrorSuffix = "";
let isRunning = false;
let currentWorkflowStage = "welcome";
let currentAugmentation = null;
let augmentationState = "idle";

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
  updateWorkflowStageLabel();
  updateRunButton();
  updateAugmentationButton();
  updateTimelineLabels();
  if (currentErrorKey) renderErrorMessage();
  if (currentResult) renderResult(currentResult);
  renderAugmentationState();
}

function updateWorkflowStageLabel() {
  elements.currentStage.replaceChildren(translationFragment(workflowStageKeys[currentWorkflowStage]));
}

function setWorkflowStage(stage) {
  if (!workflowStageKeys[stage]) return;
  currentWorkflowStage = stage;
  document.body.dataset.activeStage = stage;
  elements.workflowLinks.forEach((link) => {
    if (link.dataset.workflowStage === stage) link.setAttribute("aria-current", "step");
    else link.removeAttribute("aria-current");
  });
  updateWorkflowStageLabel();
}

function closeWorkflowNavigation() {
  document.body.classList.remove("nav-open");
  elements.navToggle.setAttribute("aria-expanded", "false");
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

function updateAugmentationButton() {
  const running = augmentationState === "running";
  const text = elements.augmentationButton.querySelector("span");
  text.replaceChildren(translationFragment(running ? "runningAugmentation" : "runAugmentation"));
  elements.augmentationButton.disabled = running;
}

function renderAugmentationState() {
  elements.augmentationStatus.hidden = augmentationState === "result";
  elements.augmentationResult.hidden = augmentationState !== "result";
  if (augmentationState !== "result") {
    const key = augmentationState === "running" ? "augmentationRunning" : augmentationState === "error" ? "augmentationError" : "augmentationEmpty";
    const paragraph = elements.augmentationStatus.querySelector("p");
    paragraph.replaceChildren(translationFragment(key));
    return;
  }
  if (!currentAugmentation) return;
  const adopted = currentAugmentation.verdict === "ADOPTED";
  elements.augmentationVerdict.className = adopted ? "is-adopted" : "is-quarantined";
  elements.augmentationVerdict.textContent = currentAugmentation.verdict;
  elements.augmentationVerdictTitle.replaceChildren(translationFragment(adopted ? "augmentationAdopted" : "augmentationQuarantined"));
  elements.augmentationSourceRows.textContent = displayValue(currentAugmentation.source_rows);
  elements.augmentationCandidateRows.textContent = displayValue(currentAugmentation.candidate_rows);
  elements.augmentationAdoptedRows.textContent = displayValue(currentAugmentation.adopted_rows);
  const passed = Array.isArray(currentAugmentation.gates) ? currentAugmentation.gates.filter((gate) => gate.status === "PASS").length : 0;
  const total = Array.isArray(currentAugmentation.gates) ? currentAugmentation.gates.length : 0;
  elements.augmentationGateStatus.textContent = `${passed} / ${total} PASS`;
  const lineage = Array.isArray(currentAugmentation.lineage) ? currentAugmentation.lineage[0] : null;
  elements.augmentationLineage.textContent = lineage ? `${lineage.source_row_ids.join("+")} → ${lineage.derived_row_id}` : translatedValue("notProvided");
  elements.augmentationModel.textContent = displayValue(currentAugmentation.nosana_model_id);
  elements.augmentationSandbox.textContent = displayValue(currentAugmentation.sandbox_id);
}

function resetAugmentationState() {
  currentAugmentation = null;
  augmentationState = "idle";
  elements.augmentationVerdict.textContent = "";
  elements.augmentationVerdictTitle.replaceChildren();
  elements.augmentationSourceRows.textContent = "";
  elements.augmentationCandidateRows.textContent = "";
  elements.augmentationAdoptedRows.textContent = "";
  elements.augmentationGateStatus.textContent = "";
  elements.augmentationLineage.textContent = "";
  elements.augmentationModel.textContent = "";
  elements.augmentationSandbox.textContent = "";
  updateAugmentationButton();
  renderAugmentationState();
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
      else if (mode === "error" && index === 0) state = "error";
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
  updateTimeline("error");
  setVisibleState("error");
  setWorkflowStage("verdict");
  window.history.replaceState(null, "", "#verdict");
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
  setWorkflowStage("run");

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
    setWorkflowStage("verdict");
    window.history.replaceState(null, "", "#verdict");
  } catch (_error) {
    showError("errorNetwork");
  } finally {
    isRunning = false;
    updateRunButton();
  }
}

async function runAugmentation() {
  if (augmentationState === "running") return;
  const selected = elements.form.elements.dataset.value;
  currentAugmentation = null;
  augmentationState = "running";
  updateAugmentationButton();
  renderAugmentationState();

  try {
    const response = await fetch("/api/augmentations", {
      method: "POST",
      headers: { "Content-Type": "application/json", "Accept": "application/json" },
      body: JSON.stringify({
        dataset_id: selected,
        research_goal: "Expand the training partition while preserving lineage and data quality."
      })
    });
    if (!response.ok) {
      augmentationState = "error";
      return;
    }
    const payload = await response.json();
    if (!payload || !["ADOPTED", "QUARANTINED"].includes(payload.verdict) || !Array.isArray(payload.lineage)) {
      augmentationState = "error";
      return;
    }
    currentAugmentation = payload;
    augmentationState = "result";
  } catch (_error) {
    augmentationState = "error";
  } finally {
    updateAugmentationButton();
    renderAugmentationState();
  }
}

document.querySelectorAll(".language-button").forEach((button) => {
  button.addEventListener("click", () => setLanguage(button.dataset.language));
});

elements.navToggle.addEventListener("click", () => {
  const isOpen = document.body.classList.toggle("nav-open");
  elements.navToggle.setAttribute("aria-expanded", String(isOpen));
});

elements.workflowLinks.forEach((link) => {
  link.addEventListener("click", () => {
    setWorkflowStage(link.dataset.workflowStage);
    closeWorkflowNavigation();
  });
});

elements.form.querySelectorAll('input[name="dataset"]').forEach((input) => {
  input.addEventListener("change", () => {
    currentResult = null;
    currentErrorKey = null;
    currentErrorSuffix = "";
    updateTimeline("idle");
    setVisibleState("empty");
    resetAugmentationState();
  });
});

window.addEventListener("keydown", (event) => {
  if (event.key === "Escape") closeWorkflowNavigation();
});

window.addEventListener("hashchange", () => {
  setWorkflowStage(workflowHashStages[window.location.hash] || "welcome");
});

const stageObserver = new IntersectionObserver(
  (entries) => {
    const visible = entries
      .filter((entry) => entry.isIntersecting)
      .sort((a, b) => b.intersectionRatio - a.intersectionRatio)[0];
    if (visible) setWorkflowStage(visible.target.dataset.pageStage);
  },
  { rootMargin: "-20% 0px -60% 0px", threshold: [0, 0.1, 0.5] }
);

document.querySelectorAll("[data-page-stage]").forEach((section) => stageObserver.observe(section));

elements.form.addEventListener("submit", (event) => {
  event.preventDefault();
  runAudit();
});
elements.retryButton.addEventListener("click", runAudit);
elements.augmentationButton.addEventListener("click", runAugmentation);

updateTimeline("idle");
setWorkflowStage(workflowHashStages[window.location.hash] || "welcome");
translateStaticUi();
