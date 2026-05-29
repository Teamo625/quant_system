你是5.5 Controller。
请读取：
- AGENTS.md
- coordination/CONTEXT_SNAPSHOT.md
- coordination/TASK_BOARD.md
- coordination/PROJECT_STATE.md
- coordination/ROADMAP.md
- coordination/reviews/TASK-037_REVIEW.md
- coordination/integrations/TASK-037_INTEGRATION.md
- coordination/PHASE_GATE.md

请基于当前状态完成 TASK-037 收口，并按 coordination/PHASE_GATE.md 判断：
- 若当前 phase 已完成，则进入下一 phase 并派发下一 phase 的首个可执行任务；
- 若当前 phase 未完成，则派发当前 phase 的下一个可执行任务。

请完成后写入：
- coordination/handoffs/{NEXT_HANDOFF_FILE}.md
- coordination/TASK_BOARD.md
- coordination/PROJECT_STATE.md
- coordination/CONTEXT_SNAPSHOT.md
- coordination/ROADMAP.md

完成后告诉我：
- 是否切换 phase（YES/NO）
- 新派发的 handoff 文件名
