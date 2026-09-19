#!/usr/bin/env bash
set -euo pipefail

GATETRACE_UI_PORT="${GATETRACE_UI_PORT:-8876}"
GATETRACE_UI_SESSION="gatetrace-ui-${RANDOM}"
GATETRACE_UI_LOG="$(mktemp -t gatetrace-ui.XXXXXX)"
GATETRACE_PWCLI=(npx --yes --package @playwright/cli playwright-cli "-s=${GATETRACE_UI_SESSION}")

cleanup() {
  "${GATETRACE_PWCLI[@]}" close >/dev/null 2>&1 || true
  if [[ -n "${GATETRACE_SERVER_PID:-}" ]]; then
    kill "${GATETRACE_SERVER_PID}" >/dev/null 2>&1 || true
    wait "${GATETRACE_SERVER_PID}" >/dev/null 2>&1 || true
  fi
  rm -f "${GATETRACE_UI_LOG}"
}
trap cleanup EXIT

.venv/bin/python -m uvicorn app:app --host 127.0.0.1 --port "${GATETRACE_UI_PORT}" >"${GATETRACE_UI_LOG}" 2>&1 &
GATETRACE_SERVER_PID=$!

for _attempt in {1..40}; do
  if curl --fail --silent "http://127.0.0.1:${GATETRACE_UI_PORT}/api/health" >/dev/null; then
    break
  fi
  sleep 0.25
done
curl --fail --silent "http://127.0.0.1:${GATETRACE_UI_PORT}/api/health" >/dev/null

"${GATETRACE_PWCLI[@]}" open "http://127.0.0.1:${GATETRACE_UI_PORT}/#augmentation-lab" >/dev/null
"${GATETRACE_PWCLI[@]}" resize 1366 768 >/dev/null

GATETRACE_MOCK_RESPONSE='{"run_id":"layout-check","status":"COMPLETED","verdict":"ADOPTED","dataset_id":"clean","sandbox_id":"sandbox-layout","nosana_model_id":"demo/model","duration_ms":1000,"source_rows":24,"candidate_rows":6,"adopted_rows":6,"gates":[{"id":"required_columns","status":"PASS"},{"id":"missing_rate","status":"PASS"},{"id":"time_order","status":"PASS"},{"id":"forbidden_columns","status":"PASS"}],"lineage":[{"derived_row_id":"aug-20260919-011","source_row_ids":["source-row-011"]}]}'
"${GATETRACE_PWCLI[@]}" route '**/api/augmentations' --body "${GATETRACE_MOCK_RESPONSE}" --content-type application/json >/dev/null

"${GATETRACE_PWCLI[@]}" run-code '
  async (page) => {
  await page.getByRole("button", { name: /증강 후보 생성·검증/ }).click();
  const metrics = await page.evaluate(() => {
    const section = document.querySelector("#augmentation-lab");
    const main = document.querySelector(".main-content");
    const footer = document.querySelector("footer");
    return {
      bodyWidth: document.body.scrollWidth,
      viewportWidth: innerWidth,
      sectionScrollHeight: section.scrollHeight,
      viewportHeight: innerHeight,
      mainClientHeight: main.clientHeight,
      sectionBottom: section.getBoundingClientRect().bottom,
      footerTop: footer.getBoundingClientRect().top,
    };
  });
  if (metrics.bodyWidth > metrics.viewportWidth || metrics.sectionScrollHeight > metrics.viewportHeight || metrics.sectionScrollHeight > metrics.mainClientHeight || metrics.sectionBottom > metrics.footerTop) {
    throw new Error(`augmentation layout overflow: ${JSON.stringify(metrics)}`);
  }
  await page.getByRole("link", { name: /목표와 데이터셋/ }).click();
  await page.getByRole("radio", { name: /데이터 오염 샘플/ }).click();
  await page.getByRole("link", { name: /증강 실험실/ }).click();
  const stale = await page.evaluate(() => ({
    resultHidden: document.querySelector("#augmentation-result").hidden,
    verdict: document.querySelector("#augmentation-verdict").textContent,
  }));
  if (!stale.resultHidden || stale.verdict !== "") {
    throw new Error(`stale augmentation result: ${JSON.stringify(stale)}`);
  }
  }
'

"${GATETRACE_PWCLI[@]}" resize 320 812 >/dev/null
"${GATETRACE_PWCLI[@]}" run-code '
  async (page) => {
  const horizontalOverflow = await page.evaluate(() => document.body.scrollWidth > innerWidth);
  if (horizontalOverflow) throw new Error("mobile horizontal overflow");
  }
'

echo "augmentation UI layout and stale-state checks passed"
