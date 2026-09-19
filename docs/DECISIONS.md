# GateTrace 결정 기록

## 확정 사항

- 제품 범위: 논문·연구 과정에 사용할 데이터의 검증과 근거 보존
- 현재 실증: 정상/오염 표 형식 센서 CSV
- UI 언어: `한국어`, `English`, `한영`; 기본 `한영`
- 판정: Daytona 실행 결과만 사용
- Nosana 역할: 제한 명세와 한영 설명 생성
- 데스크톱: 1440×900, 1366×768 주요 상태에서 문서 스크롤과 오른쪽 오버플로우 금지
- 발표: 8장, 장당 약 15초, 마지막 장은 `EXPECTED IMPACT`
- 시각 방향: `/Users/geondongkim/AI-for-Good/DESIGN.md`의 밝고 정돈된 데이터 플랫폼 스타일
- 공개 저장소: https://github.com/geondongkim/gatetrace-daytona
- Vercel 프로덕션: https://gatetrace-daytona.vercel.app
- 증강 확장: 별도 `POST /api/augmentations`, 명시적 `training` 파티션의 제한형 `bounded_jitter`, validation/test 미증강, 원본/파생 계보와 `adopted_candidates` 보존, 기존 네 게이트 전부 통과 시에만 묶음 채택
- 증강 판정: Daytona 구조화 결과만 사용하며 실패 시 로컬 우회 금지

## 계획으로만 표시할 사항

- 실제 연구 데이터 통합
- Vercel에서 증강 엔드포인트 E2E 확인
- 실제 연구 데이터에서 증강 유효성 평가
- 문서·이미지·비정형 데이터 전용 검증기
- 사용자 인증

## 변경 규칙

제품 범위나 발표 주장이 바뀌면 다음 순서로 갱신합니다.

1. `docs/PRODUCT_SPEC.md`
2. API·UI 구현과 테스트
3. `README.md`와 `DEMO_CHECKLIST.md`
4. `presentation/GateTrace_3min_Pitch.marp.md`

확인되지 않은 동작은 `확인됨`으로 쓰지 않고 계획 또는 미확인으로 구분합니다.
