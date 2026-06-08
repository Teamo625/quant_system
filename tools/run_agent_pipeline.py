#!/usr/bin/env python3
"""Run the local Codex role pipeline for the active coordination task."""

from __future__ import annotations

import argparse
import dataclasses
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import threading
from typing import Iterable, Sequence


REPO_ROOT = Path(__file__).resolve().parents[1]
TASK_BOARD = REPO_ROOT / "coordination" / "TASK_BOARD.md"
RUN_DIR = REPO_ROOT / "coordination" / "agent_runs"
STATUS_FILE = RUN_DIR / "PIPELINE_STATUS.md"
EXCLUDED_DIFF_PATHS = [
    "coordination/agent_runs/**",
    ".pytest_cache/**",
    "**/__pycache__/**",
    "**/.DS_Store",
]
CHECKPOINT_ADD_PATHSPEC = [
    ".",
]
EXECUTION_REVIEW_MODEL = "gpt-5.4"
EXECUTION_REVIEW_REASONING_EFFORT = "high"
ROLE_MODEL_OVERRIDES = {
    "EXECUTION": EXECUTION_REVIEW_MODEL,
    "REVIEW": EXECUTION_REVIEW_MODEL,
}
ROLE_REASONING_EFFORT_OVERRIDES = {
    "EXECUTION": EXECUTION_REVIEW_REASONING_EFFORT,
    "REVIEW": EXECUTION_REVIEW_REASONING_EFFORT,
}
CONTROLLER_FILES = [
    REPO_ROOT / "AGENTS.md",
    REPO_ROOT / "coordination" / "TASK_BOARD.md",
    REPO_ROOT / "coordination" / "PROJECT_STATE.md",
    REPO_ROOT / "coordination" / "CONTEXT_SNAPSHOT.md",
    REPO_ROOT / "coordination" / "ROADMAP.md",
]
CONTEXT_HYGIENE_INSTRUCTIONS = """上下文使用约束：
- 不要读取 `coordination/agent_runs/**`，除非本次任务明确要求诊断 pipeline 工具或历史 agent 日志。
- 搜索仓库时必须排除 `coordination/agent_runs/**`、`.pytest_cache/**`、`**/__pycache__/**`。
- 优先读取本角色职责所需的指定文件；只有发现矛盾、缺口或风险时，才扩大范围。
"""
TARGETED_DIFF_INSTRUCTIONS = """代码改动检查约束：
- 先用 `git status --short` 和 `git diff --stat` 判断范围。
- 再只读取本轮新增/修改的相关源码、测试、报告片段。
- 只有当 stat、报告或关键文件片段不足以判断风险时，才读取完整 `git diff` 或 diff 日志。
"""
ROLE_GIT_BOUNDARY_INSTRUCTIONS = """Git 边界：
- 不要运行 `git add`、`git commit`、`git reset`、`git checkout` 或任何会改写 git 状态的命令。
- 本地 pipeline 父脚本会在任务完整收口后统一创建 git checkpoint。
"""


class PipelineError(RuntimeError):
    """Raised for a pipeline stop condition."""


@dataclasses.dataclass(frozen=True)
class ActiveTask:
    task_id: str
    title: str
    status: str
    handoff: Path
    report: Path
    review: Path
    integration: Path | None


@dataclasses.dataclass
class GitSnapshot:
    status_short: str
    diff_stat: str
    diff: str
    staged_diff_stat: str
    staged_diff: str
    untracked_files: str
    untracked_diff: str

    @property
    def is_clean(self) -> bool:
        return not self.status_short.strip()


def now_local() -> dt.datetime:
    return dt.datetime.now().astimezone()


def clock() -> str:
    return now_local().strftime("%H:%M")


def rel(path: Path) -> str:
    try:
        return path.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def print_progress(message: str) -> None:
    print(f"[{clock()}] {message}", flush=True)


def run_capture(args: Sequence[str], *, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        cwd=REPO_ROOT,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def git_output(args: Sequence[str]) -> str:
    result = run_capture(["git", *args])
    if result.returncode != 0:
        return f"[git {' '.join(args)} failed with {result.returncode}]\n{result.stderr.strip()}\n"
    return result.stdout


def git_head() -> str:
    result = run_capture(["git", "rev-parse", "HEAD"])
    if result.returncode != 0:
        return ""
    return result.stdout.strip()


def require_success(args: Sequence[str], description: str) -> subprocess.CompletedProcess[str]:
    result = run_capture(args)
    if result.returncode != 0:
        message = redact((result.stderr or result.stdout).strip())
        raise PipelineError(f"{description} failed with exit code {result.returncode}: {message}")
    return result


def full_git_status_short() -> str:
    return git_output(["status", "--short"])


def diff_pathspec_args() -> list[str]:
    return ["--", ".", *[f":(exclude){path}" for path in EXCLUDED_DIFF_PATHS]]


def git_snapshot() -> GitSnapshot:
    return GitSnapshot(
        status_short=git_output(["status", "--short", *diff_pathspec_args()]),
        diff_stat=git_output(["diff", "--stat", *diff_pathspec_args()]),
        diff=git_output(["diff", "--no-ext-diff", *diff_pathspec_args()]),
        staged_diff_stat=git_output(["diff", "--cached", "--stat", *diff_pathspec_args()]),
        staged_diff=git_output(["diff", "--cached", "--no-ext-diff", *diff_pathspec_args()]),
        untracked_files=git_output(["ls-files", "--others", "--exclude-standard", *diff_pathspec_args()]),
        untracked_diff=untracked_diff(),
    )


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def untracked_diff() -> str:
    files = [
        line.strip()
        for line in git_output(["ls-files", "--others", "--exclude-standard", *diff_pathspec_args()]).splitlines()
    ]
    chunks: list[str] = []
    for name in files:
        path = REPO_ROOT / name
        if not path.is_file():
            continue
        try:
            if path.stat().st_size > 1_000_000:
                chunks.append(f"diff --git a/{name} b/{name}\n[untracked file omitted: larger than 1 MB]\n")
                continue
        except OSError as exc:
            chunks.append(f"diff --git a/{name} b/{name}\n[untracked file omitted: {exc}]\n")
            continue
        result = run_capture(["git", "diff", "--no-index", "--", "/dev/null", name])
        if result.returncode in (0, 1):
            chunks.append(result.stdout)
        else:
            chunks.append(f"diff --git a/{name} b/{name}\n[untracked diff failed]\n{result.stderr}\n")
    return "\n".join(chunk for chunk in chunks if chunk.strip())


def strip_md_cell(value: str) -> str:
    value = value.strip()
    if value.startswith("`") and value.endswith("`"):
        value = value[1:-1]
    return value.strip()


def strip_md_path_cell(value: str) -> str:
    matches = re.findall(r"`([^`]+)`", value)
    if matches:
        return matches[-1].strip()
    return strip_md_cell(value)


def optional_path_cell(value: str) -> str:
    stripped = strip_md_path_cell(value)
    if stripped.upper().startswith("N/A"):
        return ""
    return stripped


def parse_markdown_table_row(line: str) -> list[str]:
    cells = line.strip().strip("|").split("|")
    return [cell.strip() for cell in cells]


def parse_active_task(board_text: str) -> ActiveTask:
    in_active = False
    headers: list[str] | None = None
    for raw_line in board_text.splitlines():
        line = raw_line.strip()
        if line == "## Active":
            in_active = True
            headers = None
            continue
        if in_active and line.startswith("## "):
            break
        if not in_active or not line.startswith("|"):
            continue
        cells = parse_markdown_table_row(line)
        if not cells:
            continue
        if cells[0].lower() == "task":
            headers = [cell.lower() for cell in cells]
            continue
        if cells[0].startswith("---") or headers is None:
            continue
        row = dict(zip(headers, cells))
        task_id = strip_md_cell(row.get("task", ""))
        if not re.fullmatch(r"TASK-\d{3,}", task_id):
            continue
        required = ["handoff", "report", "review"]
        missing = [name for name in required if not strip_md_path_cell(row.get(name, ""))]
        if missing:
            raise PipelineError(f"Active task {task_id} is missing columns: {', '.join(missing)}")
        integration_cell = optional_path_cell(row.get("integration", ""))
        return ActiveTask(
            task_id=task_id,
            title=strip_md_cell(row.get("title", "")),
            status=strip_md_cell(row.get("status", "")),
            handoff=REPO_ROOT / strip_md_path_cell(row["handoff"]),
            report=REPO_ROOT / strip_md_path_cell(row["report"]),
            review=REPO_ROOT / strip_md_path_cell(row["review"]),
            integration=(REPO_ROOT / integration_cell) if integration_cell else None,
        )
    raise PipelineError("Could not parse an Active task from coordination/TASK_BOARD.md")


def task_from_markdown_row(headers: Sequence[str], cells: Sequence[str]) -> ActiveTask | None:
    row = dict(zip(headers, cells))
    task_id = strip_md_cell(row.get("task", ""))
    if not re.fullmatch(r"TASK-\d{3,}", task_id):
        return None
    required = ["handoff", "report", "review"]
    missing = [name for name in required if not strip_md_path_cell(row.get(name, ""))]
    if missing:
        raise PipelineError(f"Task {task_id} is missing columns: {', '.join(missing)}")
    integration_cell = optional_path_cell(row.get("integration", ""))
    return ActiveTask(
        task_id=task_id,
        title=strip_md_cell(row.get("title", "")),
        status=strip_md_cell(row.get("status", "")),
        handoff=REPO_ROOT / strip_md_path_cell(row["handoff"]),
        report=REPO_ROOT / strip_md_path_cell(row["report"]),
        review=REPO_ROOT / strip_md_path_cell(row["review"]),
        integration=(REPO_ROOT / integration_cell) if integration_cell else None,
    )


def parse_task_by_id(board_text: str, requested_task_id: str) -> ActiveTask:
    headers: list[str] | None = None
    for raw_line in board_text.splitlines():
        line = raw_line.strip()
        if not line.startswith("|"):
            continue
        cells = parse_markdown_table_row(line)
        if not cells:
            continue
        if cells[0].lower() == "task":
            headers = [cell.lower() for cell in cells]
            continue
        if cells[0].startswith("---") or headers is None:
            continue
        task = task_from_markdown_row(headers, cells)
        if task is not None and task.task_id == requested_task_id:
            return task
    raise PipelineError(f"Could not find {requested_task_id} in coordination/TASK_BOARD.md")


def current_active_task() -> ActiveTask:
    if not TASK_BOARD.exists():
        raise PipelineError("coordination/TASK_BOARD.md does not exist")
    return parse_active_task(read_text(TASK_BOARD))


def task_by_id(task_id: str) -> ActiveTask:
    if not TASK_BOARD.exists():
        raise PipelineError("coordination/TASK_BOARD.md does not exist")
    return parse_task_by_id(read_text(TASK_BOARD), task_id)


def prompt_path(task_id: str, role: str) -> Path:
    return RUN_DIR / f"{task_id}_{role.upper()}_PROMPT.md"


def log_path(task_id: str, role: str) -> Path:
    return RUN_DIR / f"{task_id}_{role.upper()}.log"


def controller_packet_path(task: ActiveTask) -> Path:
    return RUN_DIR / f"{task.task_id}_CONTROLLER_PACKET.md"


def status_update(
    *,
    task: ActiveTask | None,
    role: str,
    started_at: dt.datetime,
    latest_result: str,
    next_step: str,
    dry_run: bool,
) -> None:
    task_line = "N/A" if task is None else f"{task.task_id} - {task.title}"
    content = "\n".join(
        [
            "# Agent Pipeline Status",
            "",
            f"- mode: {'dry-run' if dry_run else 'run'}",
            f"- current_task: {task_line}",
            f"- current_role: {role}",
            f"- started_at: {started_at.isoformat(timespec='seconds')}",
            f"- updated_at: {now_local().isoformat(timespec='seconds')}",
            f"- latest_result: {latest_result}",
            f"- next_step: {next_step}",
            "",
        ]
    )
    write_text(STATUS_FILE, content)


def execution_prompt(task: ActiveTask) -> str:
    return f"""你是5.3 Execution。
{CONTEXT_HYGIENE_INSTRUCTIONS}
{ROLE_GIT_BOUNDARY_INSTRUCTIONS}
请读取：
- AGENTS.md
- coordination/CONTEXT_SNAPSHOT.md
- {rel(task.handoff)}

请完成代码与测试后写入：
- {rel(task.report)}

报告请使用短模板，不要复述 handoff 或长段源码；除非任务异常复杂，否则控制在 120 行以内，必须包含：
- files changed
- tests run
- default network behavior
- live-enabled PASS/SKIP/FAIL result and root-cause evidence for real-source tasks
- deviations
- risks/follow-up

完成后请告知，并按照如下格式输出内容（作为另一角色的提示词），写入这轮 {rel(task.handoff)} 和 {rel(task.report)} 的名称：
你是Review Agent。
请读取：
- AGENTS.md
- coordination/CONTEXT_SNAPSHOT.md
- {rel(task.handoff)}
- {rel(task.report)}
- 本轮代码改动

请审查后写入：
- {rel(task.review)}
"""


def diff_log_file(task: ActiveTask) -> Path:
    return RUN_DIR / f"{task.task_id}_DIFF.md"


def markdown_section(text: str, heading: str, *, max_chars: int = 4000) -> str:
    pattern = re.compile(
        rf"^##\s+{re.escape(heading)}\s*$([\s\S]*?)(?=^##\s+|\Z)",
        re.MULTILINE,
    )
    match = pattern.search(text)
    if not match:
        return ""
    section = match.group(1).strip()
    if len(section) <= max_chars:
        return section
    return section[:max_chars].rstrip() + "\n\n[truncated]"


def compact_file_digest(path: Path, headings: Sequence[str], *, max_chars: int = 6000) -> str:
    if not path.exists():
        return f"[missing: {rel(path)}]"
    text = read_text(path)
    chunks: list[str] = []
    for heading in headings:
        section = markdown_section(text, heading, max_chars=max_chars // max(1, len(headings)))
        if section:
            chunks.append(f"### {heading}\n\n{section}")
    if chunks:
        digest = "\n\n".join(chunks)
    else:
        digest = text.strip()
    if len(digest) <= max_chars:
        return digest
    return digest[:max_chars].rstrip() + "\n\n[truncated]"


def build_controller_packet(task: ActiveTask) -> Path:
    """Write a compact controller handoff packet so closure does not need wide repo scans."""
    project_state = REPO_ROOT / "coordination" / "PROJECT_STATE.md"
    task_board = REPO_ROOT / "coordination" / "TASK_BOARD.md"
    roadmap = REPO_ROOT / "coordination" / "ROADMAP.md"
    phase_gate = REPO_ROOT / "coordination" / "PHASE_GATE.md"
    context_snapshot = REPO_ROOT / "coordination" / "CONTEXT_SNAPSHOT.md"

    status = git_output(["status", "--short", *diff_pathspec_args()]).strip() or "(clean)"
    stat = git_output(["diff", "--stat", *diff_pathspec_args()]).strip() or "(no tracked diff)"
    content = [
        f"# {task.task_id} Controller Packet",
        "",
        "Generated by `tools/run_agent_pipeline.py` after Review.",
        "",
        "Use this packet as the first-pass evidence index for controller closure. Read source files only when this packet is insufficient or contradictory.",
        "",
        "## Context Hygiene",
        "",
        "- Do not read `coordination/agent_runs/**` unless diagnosing the pipeline tool itself.",
        "- Do not redo implementation-level code review; the Review record is the source of that judgment.",
        "",
        "## Task",
        "",
        f"- task_id: `{task.task_id}`",
        f"- title: {task.title}",
        f"- handoff: `{rel(task.handoff)}`",
        f"- report: `{rel(task.report)}`",
        f"- review: `{rel(task.review)}`",
        "- integration: disabled",
        "",
        "## Required Source Files",
        "",
        f"- `{rel(project_state)}`",
        f"- `{rel(task_board)}`",
        f"- `{rel(roadmap)}`",
        f"- `{rel(context_snapshot)}`",
        f"- `{rel(phase_gate)}`",
        "",
        "## Current Git Evidence",
        "",
        "### git status --short",
        "",
        "```text",
        status,
        "```",
        "",
        "### git diff --stat",
        "",
        "```text",
        stat,
        "```",
        "",
        "## Project State Snapshot",
        "",
        compact_file_digest(project_state, ["Current Phase", "Phase Gate Decision", "Next Task"], max_chars=5000),
        "",
        "## Active Task Board Snapshot",
        "",
        compact_file_digest(task_board, ["Active", "Backlog"], max_chars=4500),
        "",
        "## Review Digest",
        "",
        compact_file_digest(
            task.review,
            ["Decision", "Closure Readiness", "Findings (ordered by severity)", "Residual Risk", "Follow-up Requirements"],
            max_chars=4000,
        ),
        "",
        "## Phase Gate Rules",
        "",
        compact_file_digest(phase_gate, ["Completion Criteria", "Phase Transition Rules", "Controller Requirements"], max_chars=5000),
        "",
    ]
    path = controller_packet_path(task)
    write_text(path, redact("\n".join(content)))
    return path


def review_change_instruction(task: ActiveTask, diff_context: str, inline_diff_context: bool) -> str:
    if inline_diff_context:
        return f"""本轮代码改动如下：

{diff_context}
"""
    return f"""{TARGETED_DIFF_INSTRUCTIONS}

如需完整本轮 diff 日志，可读取 {rel(diff_log_file(task))}。
"""


def review_prompt(task: ActiveTask, diff_context: str, inline_diff_context: bool) -> str:
    next_role_block = f"""Review 文件必须包含机器可读的 `Closure Status` 区块，格式必须完全使用这些 key：

## Closure Status

- decision: accepted|rejected_or_blocked
- controller_closure_allowed: yes|no
- default_tests_offline_safe: yes|no
- live_enabled_result: PASS|SKIP|FAIL|N/A
- rework_required: yes|no

Review 文件还必须包含简短的 `Closure Readiness` 区块，明确：
- 是否可由 Controller 收口
- 默认测试是否离线安全
- live-enabled 结果为 PASS/SKIP/FAIL；如 SKIP/FAIL，是否需要 rework
- 是否存在 phase/scope/contract/test 阻塞项

完成后请告知，并按照如下格式输出内容（作为另一角色的提示词），写入这轮 {rel(task.handoff)}、{rel(task.report)}、{rel(task.review)} 和 {task.task_id} 的名称：
你是5.5 Controller。
请读取：
- AGENTS.md
- coordination/CONTEXT_SNAPSHOT.md
- coordination/TASK_BOARD.md
- coordination/PROJECT_STATE.md
- coordination/ROADMAP.md
- {rel(task.review)}
- coordination/PHASE_GATE.md

请基于 Review 的 Closure Readiness 完成 {task.task_id} 收口，并按 phase gate 派发下一步。
"""
    return f"""你是Review Agent。
{CONTEXT_HYGIENE_INSTRUCTIONS}
{ROLE_GIT_BOUNDARY_INSTRUCTIONS}
请读取：
- AGENTS.md
- coordination/CONTEXT_SNAPSHOT.md
- {rel(task.handoff)}
- {rel(task.report)}
- 本轮代码改动

{review_change_instruction(task, diff_context, inline_diff_context)}

请审查后写入：
- {rel(task.review)}

Review 文件请保持短小，不要复述报告全文或 handoff；优先写 findings、decision、closure readiness、required follow-up。

{next_role_block}
"""


def controller_prompt(task: ActiveTask, packet: Path | None = None) -> str:
    packet_lines = []
    if packet is not None:
        packet_lines = [
            f"- {rel(packet)}",
            "",
            "请优先以 controller packet 作为 TASK 收口证据索引；只有 packet 与源文件矛盾或信息不足时，才读取更大范围文件。",
        ]
    else:
        packet_lines = [
            "- 本次 dry-run 尚未生成 controller packet；请按下列源文件生成计划即可。",
        ]
    packet_block = "\n".join(packet_lines)
    return f"""你是5.5 Controller。
{CONTEXT_HYGIENE_INSTRUCTIONS}
{ROLE_GIT_BOUNDARY_INSTRUCTIONS}
请读取：
{packet_block}

必要源文件：
- AGENTS.md
- coordination/CONTEXT_SNAPSHOT.md
- coordination/TASK_BOARD.md
- coordination/PROJECT_STATE.md
- coordination/ROADMAP.md
- {rel(task.review)}
- coordination/PHASE_GATE.md

职责边界：
- 不要重新做实现级代码审查；代码正确性由 Review Agent 的本地记录负责。
- 不要读取 `coordination/agent_runs/**` 中的历史 prompt、log、diff，除非你正在诊断 pipeline 工具。

请基于当前状态完成 {task.task_id} 收口，并按 coordination/PHASE_GATE.md 判断：
- 若当前 phase 已完成，则进入下一 phase 并派发下一 phase 的首个可执行任务；
- 若当前 phase 未完成，则派发当前 phase 的下一个可执行 capability cluster handoff。

当前 phase 未完成时的派发硬性规则：
- Controller 必须优先读取 DataHub readiness 的 `follow_up_batches`；若尚无批量字段，则读取相邻/同域/同主题的 `follow_up_queue` 项并合并。
- 普通 hardening handoff 应覆盖一个 coherent capability cluster，通常包含 2-6 个相关 capability/follow-up items。
- 如果只派发单个 follow-up item，必须在 coordination/PROJECT_STATE.md 和 coordination/CONTEXT_SNAPSHOT.md 说明不能合并的原因。
- 单 item handoff 只适用于 Review rework、live FAIL/SKIP 诊断、paid credential/owner waiver blocker、跨 phase/module 边界、多个不相关 domain、schema 变更风险过大，或确实没有相邻可合并项。
- 不重写历史 handoff；当前已经 Active 的 TASK-126 不强行扩大，从 TASK-126 收口后的下一次派发开始应用能力簇策略。

请完成后写入：
- AGENTS.md（若当前 implementation phase 或 allowed implementation target 发生变化）
- coordination/handoffs/{{NEXT_HANDOFF_FILE}}.md
- coordination/TASK_BOARD.md
- coordination/PROJECT_STATE.md
- coordination/CONTEXT_SNAPSHOT.md
- coordination/ROADMAP.md

完成后告诉我：
- 是否切换 phase（YES/NO）
- 新派发的 handoff 文件名
"""


def controller_rework_prompt(task: ActiveTask) -> str:
    return f"""你是5.5 Controller。
{CONTEXT_HYGIENE_INSTRUCTIONS}
{ROLE_GIT_BOUNDARY_INSTRUCTIONS}
请读取：
- AGENTS.md
- coordination/CONTEXT_SNAPSHOT.md
- coordination/TASK_BOARD.md
- coordination/PROJECT_STATE.md
- coordination/ROADMAP.md
- {rel(task.handoff)}
- {rel(task.report)}
- {rel(task.review)}
- coordination/PHASE_GATE.md

Review Agent 已经拒绝或阻塞当前结果。

请基于 Review findings 和当前项目状态派发一个 rework handoff。

职责边界：
- 不要重新做完整实现级代码审查；只围绕 Review findings 派发最小 rework。
- Review rework 必须保持最小任务，不得与 readiness `follow_up_batches` 或其他普通 hardening items 合并。
- 不要读取 `coordination/agent_runs/**` 中的历史 prompt、log、diff，除非你正在诊断 pipeline 工具。

硬性要求：
- 不得关闭当前 task。
- 不得调度 Integration Agent。
- 不得把当前 task 标记为 Done。
- 必须派发一个新的 Active rework handoff，让下一轮 5.3 Execution 可以继续修复。
- 必须保持 phase 边界和 AGENTS.md 规则。

请完成后写入：
- AGENTS.md（若当前 implementation phase 或 allowed implementation target 发生变化）
- coordination/handoffs/{{REWORK_HANDOFF_FILE}}.md
- coordination/TASK_BOARD.md
- coordination/PROJECT_STATE.md
- coordination/CONTEXT_SNAPSHOT.md
- coordination/ROADMAP.md

完成后告诉我：
- rework handoff 文件名
- 新的 Active task
"""


def redact(text: str) -> str:
    patterns = [
        (re.compile(r"(?i)(token|api[_-]?key|secret|password|cookie)(\s*[:=]\s*)([^\s]+)"), r"\1\2[REDACTED]"),
        (re.compile(r"(?i)(authorization:\s*bearer\s+)([^\s]+)"), r"\1[REDACTED]"),
    ]
    for pattern, replacement in patterns:
        text = pattern.sub(replacement, text)
    return text


def diff_context(task: ActiveTask, baseline: GitSnapshot) -> str:
    current = git_snapshot()
    patch_path = RUN_DIR / f"{task.task_id}_DIFF.patch"
    patch_content = "\n".join(
        part
        for part in [current.diff, current.staged_diff, current.untracked_diff]
        if part.strip()
    )
    write_text(patch_path, redact(patch_content))
    header = [
        f"# {task.task_id} Code Change Context",
        "",
        "Generated by `tools/run_agent_pipeline.py` after Execution.",
        "This file is intentionally compact. Read the listed source/test/report files first; use the full patch only if needed.",
        "",
        f"Full patch, if genuinely needed: `{rel(patch_path)}`",
        "",
    ]
    if baseline.is_clean:
        header.extend(
            [
                "Baseline worktree was clean, so the diff below is treated as this pipeline task's code change set.",
                "",
            ]
        )
    else:
        header.extend(
            [
                "Baseline worktree was not clean before Execution.",
                "A reliable task-relative patch cannot be derived without discarding or stashing user changes, so this file records baseline and current git evidence.",
                "",
                "## Baseline `git status --short`",
                "",
                "```text",
                baseline.status_short.strip() or "(clean)",
                "```",
                "",
                "## Baseline `git diff --stat`",
                "",
                "```text",
                baseline.diff_stat.strip() or "(no tracked diff)",
                "```",
                "",
                "## Baseline staged `git diff --cached --stat`",
                "",
                "```text",
                baseline.staged_diff_stat.strip() or "(no staged diff)",
                "```",
                "",
                "## Baseline untracked files",
                "",
                "```text",
                baseline.untracked_files.strip() or "(none)",
                "```",
                "",
            ]
        )
    header.extend(
        [
            "## Current `git status --short`",
            "",
            "```text",
            current.status_short.strip() or "(clean)",
            "```",
            "",
            "## Current `git diff --stat`",
            "",
            "```text",
            current.diff_stat.strip() or "(no tracked diff)",
            "```",
            "",
            "## Current staged `git diff --cached --stat`",
            "",
            "```text",
            current.staged_diff_stat.strip() or "(no staged diff)",
            "```",
            "",
            "## Current untracked files",
            "",
            "```text",
            current.untracked_files.strip() or "(none)",
            "```",
            "",
        ]
    )
    content = redact("\n".join(header))
    write_text(RUN_DIR / f"{task.task_id}_DIFF.md", content)
    return content


def role_model(role: str, cli_model: str | None) -> str | None:
    if cli_model:
        return cli_model
    return ROLE_MODEL_OVERRIDES.get(role.upper())


def role_reasoning_effort(role: str) -> str | None:
    return ROLE_REASONING_EFFORT_OVERRIDES.get(role.upper())


def build_codex_command(codex_bin: str, role: str, model: str | None) -> list[str]:
    cmd = [codex_bin, "exec", "-C", str(REPO_ROOT)]
    selected_model = role_model(role, model)
    selected_reasoning_effort = role_reasoning_effort(role)
    if selected_model:
        cmd.extend(["--model", selected_model])
    if selected_reasoning_effort:
        cmd.extend(["-c", f'model_reasoning_effort="{selected_reasoning_effort}"'])
    cmd.append("-")
    return cmd


def role_env(args: argparse.Namespace) -> dict[str, str]:
    env = os.environ.copy()
    if args.live_tests is True:
        env["QUANT_SYSTEM_LIVE_TESTS"] = "1"
    elif args.live_tests is False:
        env.pop("QUANT_SYSTEM_LIVE_TESTS", None)
    return env


def run_codex_role(
    *,
    task: ActiveTask,
    role: str,
    prompt: str,
    args: argparse.Namespace,
    started_at: dt.datetime,
) -> None:
    role_upper = role.upper()
    write_text(prompt_path(task.task_id, role), prompt)
    command = build_codex_command(args.codex_bin, role, args.model)
    if args.dry_run:
        write_text(
            log_path(task.task_id, role),
            "DRY RUN: codex was not executed.\n\nCommand preview:\n"
            + " ".join(command)
            + "\nPrompt saved separately in "
            + rel(prompt_path(task.task_id, role))
            + "\n",
        )
        print_progress(f"{task.task_id} {role_upper} dry-run prompt written")
        return

    status_update(
        task=task,
        role=role_upper,
        started_at=started_at,
        latest_result="started",
        next_step="waiting for codex exec to finish",
        dry_run=False,
    )
    with log_path(task.task_id, role).open("w", encoding="utf-8") as log_file:
        log_file.write(f"$ {' '.join(command)} < {rel(prompt_path(task.task_id, role))}\n\n")
        log_file.flush()
        proc = subprocess.Popen(
            command,
            cwd=REPO_ROOT,
            env=role_env(args),
            text=True,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        assert proc.stdout is not None
        assert proc.stdin is not None
        stdin_errors: list[str] = []

        def send_prompt() -> None:
            try:
                assert proc.stdin is not None
                proc.stdin.write(prompt)
                proc.stdin.close()
            except BrokenPipeError:
                stdin_errors.append("codex process closed stdin before receiving the full prompt")

        stdin_thread = threading.Thread(target=send_prompt, daemon=True)
        stdin_thread.start()
        for line in proc.stdout:
            clean = redact(line)
            log_file.write(clean)
            log_file.flush()
        stdin_thread.join()
        for stdin_error in stdin_errors:
            log_file.write(f"[stdin] {stdin_error}\n")
            log_file.flush()
        return_code = proc.wait()
        log_file.write(f"\n[exit_code] {return_code}\n")
    if return_code != 0:
        raise PipelineError(f"{task.task_id} {role_upper} failed: codex exec returned {return_code}")


def ensure_file(path: Path, description: str) -> None:
    if not path.exists():
        raise PipelineError(f"Expected {description} was not generated: {rel(path)}")


def contains_any(text: str, needles: Iterable[str]) -> bool:
    lowered = text.lower()
    return any(needle.lower() in lowered for needle in needles)


def review_markdown_section(text: str, heading: str) -> str:
    pattern = re.compile(rf"(?ims)^#{{1,6}}\s*{re.escape(heading)}\b[^\n]*\n(?P<body>.*?)(?=^#{{1,6}}\s|\Z)")
    match = pattern.search(text)
    if match is None:
        return ""
    return match.group("body")


def review_decision_result(text: str) -> str:
    decision = review_markdown_section(text, "Decision")
    if not decision:
        return REVIEW_UNKNOWN

    if re.search(
        r"\b(rejected|reject|blocked|changes[_ -]?requested|rework[_ -]?required)\b",
        decision,
        flags=re.IGNORECASE,
    ):
        return REVIEW_REJECTED_OR_BLOCKED
    if re.search(r"\b(accepted|accept)\b", decision, flags=re.IGNORECASE):
        return REVIEW_ACCEPTED
    return REVIEW_UNKNOWN


REVIEW_ACCEPTED = "accepted"
REVIEW_REJECTED_OR_BLOCKED = "rejected_or_blocked"
REVIEW_UNKNOWN = "unknown"
REVIEW_CLOSURE_STATUS_SECTION = "Closure Status"


def normalize_review_status_value(value: str) -> str:
    value = value.strip().strip("`").strip("*").strip()
    return value.lower()


def review_closure_status_values(text: str) -> dict[str, str]:
    section = review_markdown_section(text, REVIEW_CLOSURE_STATUS_SECTION)
    if not section:
        return {}
    values: dict[str, str] = {}
    for line in section.splitlines():
        match = re.match(r"^\s*[-*]\s*([A-Za-z0-9_ -]+)\s*:\s*(.+?)\s*$", line)
        if match is None:
            continue
        key = match.group(1).strip().lower().replace("-", "_").replace(" ", "_")
        values[key] = normalize_review_status_value(match.group(2))
    return values


def review_closure_status_result(text: str) -> str:
    values = review_closure_status_values(text)
    if not values:
        return REVIEW_UNKNOWN
    decision = values.get("decision", "")
    if decision == REVIEW_ACCEPTED:
        return REVIEW_ACCEPTED
    if decision == REVIEW_REJECTED_OR_BLOCKED:
        return REVIEW_REJECTED_OR_BLOCKED
    return REVIEW_UNKNOWN


def classify_review_result(task: ActiveTask) -> str:
    ensure_file(task.review, "review file")
    text = read_text(task.review)
    if review_markdown_section(text, REVIEW_CLOSURE_STATUS_SECTION):
        return review_closure_status_result(text)

    decision_result = review_decision_result(text)
    if decision_result != REVIEW_UNKNOWN:
        return decision_result

    bad = [
        "rejected",
        "blocked",
        "reject",
        "changes requested",
        "changes_requested",
        "rework required",
        "rework_required",
    ]
    allowed_phrases = [
        "no blocking finding",
        "no blocking findings",
        "no blockers",
        "not rejected",
        "no rejection",
        "no rejected",
    ]
    accepted = ["accepted", "accept"]
    if contains_any(text, bad) and not contains_any(text, allowed_phrases):
        return REVIEW_REJECTED_OR_BLOCKED
    if contains_any(text, accepted):
        return REVIEW_ACCEPTED
    return REVIEW_UNKNOWN


def check_review(task: ActiveTask) -> None:
    review_result = classify_review_result(task)
    if review_result == REVIEW_REJECTED_OR_BLOCKED:
        raise PipelineError(f"{task.task_id} review appears to reject or block the task: {rel(task.review)}")
    if review_result != REVIEW_ACCEPTED:
        raise PipelineError(f"{task.task_id} review file does not contain an obvious acceptance signal")


def file_hash(path: Path) -> str:
    if not path.exists():
        return ""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def first_nonempty_line(text: str) -> str:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped:
            return stripped
    return ""


def phase_marker(text: str) -> str:
    match = re.search(r"\bPhase\s+([0-9]+(?:\.[0-9]+)?)\b", text, flags=re.IGNORECASE)
    if not match:
        return ""
    return f"phase {match.group(1)}"


def project_state_current_phase(project_state: Path) -> str:
    phase_section = review_markdown_section(read_text(project_state), "Current Phase")
    return first_nonempty_line(phase_section)


def agents_current_phase(agents_file: Path) -> str:
    match = re.search(
        r"(?im)^Current implementation phase:\s*(?P<phase>.+?)\s*$",
        read_text(agents_file),
    )
    if match is None:
        return ""
    return match.group("phase").strip()


def ensure_agents_phase_consistent() -> None:
    agents_file = REPO_ROOT / "AGENTS.md"
    project_state = REPO_ROOT / "coordination" / "PROJECT_STATE.md"
    if not agents_file.exists() or not project_state.exists():
        return

    project_phase = project_state_current_phase(project_state)
    agents_phase = agents_current_phase(agents_file)
    project_marker = phase_marker(project_phase)
    agents_marker = phase_marker(agents_phase)

    if not project_marker or not agents_marker:
        raise PipelineError(
            "Could not verify phase consistency between AGENTS.md and coordination/PROJECT_STATE.md"
        )
    if project_marker != agents_marker:
        raise PipelineError(
            "AGENTS.md current implementation phase does not match coordination/PROJECT_STATE.md: "
            f"AGENTS.md has '{agents_phase}', PROJECT_STATE.md has '{project_phase}'"
        )


def controller_hashes() -> dict[Path, str]:
    return {path: file_hash(path) for path in CONTROLLER_FILES}


def task_board_or_project_state_changed(before_hashes: dict[Path, str]) -> bool:
    watched = [
        REPO_ROOT / "coordination" / "TASK_BOARD.md",
        REPO_ROOT / "coordination" / "PROJECT_STATE.md",
    ]
    return any(file_hash(path) != before_hashes.get(path, "") for path in watched)


def phase_complete_signal() -> bool:
    project_state = REPO_ROOT / "coordination" / "PROJECT_STATE.md"
    if project_state.exists():
        current_decision = review_markdown_section(read_text(project_state), "Phase Gate Decision")
        if current_decision:
            if contains_any(current_decision, ["Phase switch: NO", "STAY_IN_", "not complete"]):
                return False
            return contains_any(
                current_decision,
                [
                    "Phase switch: YES",
                    "phase switched",
                    "PHASE_SWITCHED_TO_",
                    "current phase is complete",
                ],
            )

    texts = []
    for path in [REPO_ROOT / "coordination" / "CONTEXT_SNAPSHOT.md", TASK_BOARD]:
        if path.exists():
            texts.append(read_text(path))
    combined = "\n".join(texts)
    return contains_any(
        combined,
        [
            "Phase switch: YES",
            "phase switched",
            "PHASE_SWITCHED_TO_",
            "Phase 2 is complete",
            "Phase 2 completed",
            "current phase is complete",
        ],
    )


def check_controller(task: ActiveTask, before_hashes: dict[Path, str]) -> ActiveTask | None:
    if not task_board_or_project_state_changed(before_hashes):
        raise PipelineError("Controller did not update coordination/TASK_BOARD.md or coordination/PROJECT_STATE.md")
    ensure_agents_phase_consistent()
    try:
        next_task = current_active_task()
    except PipelineError:
        next_task = None
    if next_task is not None and not (next_task.task_id == task.task_id and next_task.handoff == task.handoff):
        ensure_file(next_task.handoff, "next active handoff file")
        return next_task
    if phase_complete_signal():
        return None
    if next_task is None:
        raise PipelineError("Controller did not dispatch a next Active task and no phase-complete signal was found")
    raise PipelineError(f"Controller left the same Active task ({task.task_id}) without a phase-complete signal")


def check_controller_rework(task: ActiveTask, before_hashes: dict[Path, str]) -> ActiveTask:
    if not task_board_or_project_state_changed(before_hashes):
        raise PipelineError("Controller rework did not update coordination/TASK_BOARD.md or coordination/PROJECT_STATE.md")
    ensure_agents_phase_consistent()
    try:
        next_task = current_active_task()
    except PipelineError:
        raise PipelineError("Controller rework did not dispatch a new Active task")
    if next_task.handoff == task.handoff:
        raise PipelineError(f"Controller rework left the same handoff active: {rel(task.handoff)}")
    ensure_file(next_task.handoff, "rework active handoff file")
    return next_task


def dispatch_rework(task: ActiveTask, args: argparse.Namespace, started_at: dt.datetime) -> ActiveTask | None:
    before_controller = controller_hashes()
    print_progress(f"{task.task_id} Controller rework started")
    status_update(
        task=task,
        role="CONTROLLER_REWORK",
        started_at=started_at,
        latest_result="review rejected_or_blocked",
        next_step="dispatch rework handoff",
        dry_run=args.dry_run,
    )
    run_codex_role(
        task=task,
        role="CONTROLLER_REWORK",
        prompt=controller_rework_prompt(task),
        args=args,
        started_at=started_at,
    )
    if args.dry_run:
        print_progress(f"{task.task_id} Controller rework dry-run prompt ready")
        return None
    next_task = check_controller_rework(task, before_controller)
    print_progress(f"Controller dispatched rework {next_task.task_id}")
    status_update(
        task=next_task,
        role="complete",
        started_at=started_at,
        latest_result="rework handoff dispatched",
        next_step=f"next Active task {next_task.task_id}",
        dry_run=False,
    )
    create_git_checkpoint(task, args)
    return next_task


def checkpoint_message(task: ActiveTask, args: argparse.Namespace) -> str:
    return f"{args.checkpoint_message_prefix}: {task.task_id} pipeline closure"


def git_dir() -> Path:
    result = require_success(["git", "rev-parse", "--git-dir"], "git directory check")
    path = Path(result.stdout.strip())
    if path.is_absolute():
        return path
    return REPO_ROOT / path


def checkpoint_state_dir() -> Path:
    return git_dir() / "quant_system_pipeline"


def checkpoint_baseline_marker_path(task: ActiveTask) -> Path:
    return checkpoint_state_dir() / f"{task.task_id}_checkpoint_baseline.json"


def checkpoint_baseline_marker_payload(task: ActiveTask, baseline_head: str) -> dict[str, str]:
    return {
        "task_id": task.task_id,
        "baseline_head": baseline_head,
        "handoff": rel(task.handoff),
        "report": rel(task.report),
        "review": rel(task.review),
        "started_at": now_local().isoformat(timespec="seconds"),
    }


def write_checkpoint_baseline_marker(task: ActiveTask, baseline_head: str) -> None:
    path = checkpoint_baseline_marker_path(task)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(checkpoint_baseline_marker_payload(task, baseline_head), ensure_ascii=False, indent=2)
        + "\n",
        encoding="utf-8",
    )


def read_checkpoint_baseline_marker(task: ActiveTask) -> dict[str, str]:
    path = checkpoint_baseline_marker_path(task)
    if not path.exists():
        raise PipelineError(
            f"{task.task_id} cannot resume automatic git checkpoint from a dirty worktree because "
            f"the checkpoint baseline marker is missing: {path}. "
            "Rerun with --no-git-checkpoint and commit manually, or clean unrelated changes first."
        )
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise PipelineError(
            f"{task.task_id} checkpoint baseline marker is unreadable: {path} ({exc}). "
            "Rerun with --no-git-checkpoint and commit manually, or clean unrelated changes first."
        ) from exc
    if not isinstance(payload, dict):
        raise PipelineError(
            f"{task.task_id} checkpoint baseline marker is invalid: {path}. "
            "Rerun with --no-git-checkpoint and commit manually, or clean unrelated changes first."
        )
    return {str(key): str(value) for key, value in payload.items()}


def clear_checkpoint_baseline_marker(task: ActiveTask) -> None:
    try:
        checkpoint_baseline_marker_path(task).unlink(missing_ok=True)
    except OSError:
        return


def validate_checkpoint_baseline_marker(task: ActiveTask, current_head: str) -> None:
    payload = read_checkpoint_baseline_marker(task)
    marker_task_id = payload.get("task_id", "")
    marker_head = payload.get("baseline_head", "")
    if marker_task_id != task.task_id:
        raise PipelineError(
            f"{task.task_id} checkpoint baseline marker belongs to {marker_task_id or '(unknown task)'}. "
            "Rerun with --no-git-checkpoint and commit manually, or clean unrelated changes first."
        )
    if not marker_head or marker_head != current_head:
        raise PipelineError(
            f"{task.task_id} checkpoint baseline marker HEAD does not match current HEAD. "
            "Rerun with --no-git-checkpoint and commit manually, or clean unrelated changes first."
        )


def ensure_clean_checkpoint_baseline(task: ActiveTask, args: argparse.Namespace) -> None:
    if not args.commit_after_task or args.dry_run:
        return
    status = full_git_status_short()
    current_head = git_head()
    if not status.strip():
        write_checkpoint_baseline_marker(task, current_head)
        return
    if args.resume_from is not None:
        validate_checkpoint_baseline_marker(task, current_head)
        return
    if status.strip():
        raise PipelineError(
            f"{task.task_id} cannot create an automatic git checkpoint because the worktree is already dirty. "
            "Commit or clear existing changes first so the checkpoint does not include unrelated work.\n"
            + status.strip()
        )


def ensure_no_role_git_commit(task: ActiveTask, args: argparse.Namespace, baseline_head: str) -> None:
    if not args.commit_after_task or args.dry_run:
        return
    current_head = git_head()
    if baseline_head and current_head and current_head != baseline_head:
        raise PipelineError(
            f"{task.task_id} changed git HEAD before the parent pipeline checkpoint. "
            "Execution/Review/Controller roles must not create commits; rerun through "
            "tools/run_agent_pipeline.py with git commits left to the parent checkpoint."
        )


def create_git_checkpoint(task: ActiveTask, args: argparse.Namespace) -> None:
    if not args.commit_after_task or args.dry_run:
        return
    status = full_git_status_short()
    if not status.strip():
        print_progress(f"{task.task_id} checkpoint skipped, no git changes to commit")
        clear_checkpoint_baseline_marker(task)
        return

    print_progress(f"{task.task_id} checkpoint staging changes")
    require_success(["git", "add", "-A", "--", *CHECKPOINT_ADD_PATHSPEC], f"{task.task_id} checkpoint git add")
    staged_stat = require_success(["git", "diff", "--cached", "--stat"], f"{task.task_id} checkpoint staged stat")
    if not staged_stat.stdout.strip():
        print_progress(f"{task.task_id} checkpoint skipped, no staged changes")
        clear_checkpoint_baseline_marker(task)
        return
    print_progress(f"{task.task_id} checkpoint staged changes ready")
    staged = run_capture(["git", "diff", "--cached", "--quiet"])
    if staged.returncode == 0:
        print_progress(f"{task.task_id} checkpoint skipped, no staged changes")
        clear_checkpoint_baseline_marker(task)
        return
    if staged.returncode not in (0, 1):
        raise PipelineError(f"{task.task_id} checkpoint staged-diff check failed: {redact(staged.stderr.strip())}")

    message = checkpoint_message(task, args)
    result = require_success(["git", "commit", "-m", message], f"{task.task_id} checkpoint git commit")
    commit_hash = git_output(["rev-parse", "--short", "HEAD"]).strip()
    print_progress(f"{task.task_id} checkpoint committed {commit_hash or '(hash unavailable)'}")
    if result.stdout.strip():
        print_progress(f"{task.task_id} checkpoint commit recorded")
    clear_checkpoint_baseline_marker(task)


def current_active_task_or_none() -> ActiveTask | None:
    try:
        return current_active_task()
    except PipelineError:
        return None


def review_file_result(task: ActiveTask) -> str:
    if not task.review.exists():
        return REVIEW_UNKNOWN
    return classify_review_result(task)


def handoff_supersedes_review(task: ActiveTask) -> bool:
    if not task.handoff.exists() or not task.review.exists():
        return False
    if "REWORK" in task.handoff.name.upper():
        return True
    try:
        return task.handoff.stat().st_mtime > task.review.stat().st_mtime
    except OSError:
        return False


def resolve_start_stage(task: ActiveTask, args: argparse.Namespace) -> str:
    if args.resume_from is None:
        return "execution"
    if args.resume_from != "auto":
        return args.resume_from
    if handoff_supersedes_review(task):
        return "execution"
    if not task.report.exists():
        return "execution"

    review_result = review_file_result(task)
    if review_result == REVIEW_REJECTED_OR_BLOCKED:
        return "controller_rework"
    if review_result == REVIEW_ACCEPTED:
        active = current_active_task_or_none()
        if active is not None and active.task_id != task.task_id:
            return "complete"
        return "controller"
    return "review"


def validate_resume_prerequisites(task: ActiveTask, stage: str, args: argparse.Namespace) -> None:
    if stage in {"review", "controller", "controller_rework", "complete"}:
        ensure_file(task.report, "execution report")
    if stage in {"controller", "controller_rework", "complete"}:
        ensure_file(task.review, "review file")
    if stage in {"controller", "complete"}:
        review_result = classify_review_result(task)
        if review_result != REVIEW_ACCEPTED:
            raise PipelineError(
                f"{task.task_id} cannot resume at {stage}; review result is not accepted: {rel(task.review)}"
            )


def resumed_diff_context(task: ActiveTask) -> str:
    baseline = git_snapshot()
    if diff_log_file(task).exists():
        return read_text(diff_log_file(task))
    return diff_context(task, baseline)


def preflight(args: argparse.Namespace) -> None:
    if not args.dry_run and not shutil.which(args.codex_bin):
        raise PipelineError(
            f"codex exec is not available at '{args.codex_bin}'. "
            "Install Codex CLI or pass --codex-bin /path/to/codex."
        )
    if args.commit_after_task and not args.dry_run:
        require_success(["git", "rev-parse", "--is-inside-work-tree"], "git repository check")
        require_success(["git", "config", "user.name"], "git user.name check")
        require_success(["git", "config", "user.email"], "git user.email check")
    if not TASK_BOARD.exists():
        raise PipelineError("coordination/TASK_BOARD.md is missing")
    ensure_agents_phase_consistent()


def run_one_task(task: ActiveTask, args: argparse.Namespace, started_at: dt.datetime) -> ActiveTask | None:
    ensure_clean_checkpoint_baseline(task, args)
    start_stage = resolve_start_stage(task, args)
    validate_resume_prerequisites(task, start_stage, args)
    if args.resume_from is not None:
        print_progress(f"{task.task_id} resume mode starting at {start_stage}")
    baseline_head = git_head() if args.commit_after_task and not args.dry_run else ""
    status_update(
        task=task,
        role="preflight",
        started_at=started_at,
        latest_result="task parsed",
        next_step=start_stage.capitalize(),
        dry_run=args.dry_run,
    )
    if start_stage == "complete":
        print_progress(f"{task.task_id} already appears closed; finishing parent pipeline bookkeeping")
        status_update(
            task=task,
            role="complete",
            started_at=started_at,
            latest_result="task pipeline complete",
            next_step="already dispatched next Active task",
            dry_run=args.dry_run,
        )
        ensure_no_role_git_commit(task, args, baseline_head)
        create_git_checkpoint(task, args)
        return current_active_task_or_none()

    if start_stage == "controller_rework":
        print_progress(f"{task.task_id} existing Review rejected or blocked; dispatching rework")
        return dispatch_rework(task, args, started_at)

    if start_stage == "execution":
        baseline = git_snapshot()
        if not baseline.is_clean:
            print_progress(f"{task.task_id} baseline worktree is not clean; diff log will include baseline evidence")

        print_progress(f"{task.task_id} Execution started")
        run_codex_role(task=task, role="EXECUTION", prompt=execution_prompt(task), args=args, started_at=started_at)
        if not args.dry_run:
            ensure_file(task.report, "execution report")
        print_progress(f"{task.task_id} Execution finished, report {'would be checked' if args.dry_run else 'found'}")

        diff = diff_context(task, baseline)
    else:
        diff = resumed_diff_context(task)
        if start_stage in {"review", "controller"}:
            print_progress(f"{task.task_id} skipping completed role(s) before {start_stage}")

    if start_stage in {"execution", "review"}:
        print_progress(f"{task.task_id} Review started")
        run_codex_role(
            task=task,
            role="REVIEW",
            prompt=review_prompt(task, diff, args.inline_diff_context),
            args=args,
            started_at=started_at,
        )
        if args.dry_run:
            print_progress(f"{task.task_id} Review dry-run prompt ready")
        else:
            review_result = classify_review_result(task)
            if review_result == REVIEW_ACCEPTED:
                print_progress(f"{task.task_id} Review accepted")
            elif review_result == REVIEW_REJECTED_OR_BLOCKED:
                print_progress(f"{task.task_id} Review rejected or blocked; dispatching rework")
                return dispatch_rework(task, args, started_at)
            else:
                raise PipelineError(f"{task.task_id} review result is unknown: {rel(task.review)}")

    before_controller = controller_hashes()
    controller_packet = None if args.dry_run else build_controller_packet(task)
    print_progress(f"{task.task_id} Controller started")
    run_codex_role(
        task=task,
        role="CONTROLLER",
        prompt=controller_prompt(task, controller_packet),
        args=args,
        started_at=started_at,
    )
    if args.dry_run:
        print_progress(f"{task.task_id} Controller dry-run prompt ready")
        status_update(
            task=task,
            role="complete",
            started_at=started_at,
            latest_result="dry-run complete",
            next_step="run without --dry-run when ready",
            dry_run=True,
        )
        return None
    next_task = check_controller(task, before_controller)
    if next_task is None:
        print_progress("Controller reported phase complete")
    else:
        print_progress(f"Controller dispatched {next_task.task_id}")
    status_update(
        task=next_task or task,
        role="complete",
        started_at=started_at,
        latest_result="task pipeline complete",
        next_step=("phase complete" if next_task is None else f"next Active task {next_task.task_id}"),
        dry_run=False,
    )
    ensure_no_role_git_commit(task, args, baseline_head)
    create_git_checkpoint(task, args)
    return next_task


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the local Codex Execution -> Review -> Controller pipeline."
    )
    parser.add_argument("--tasks", type=int, default=1, help="maximum number of tasks to run (default: 1)")
    parser.add_argument(
        "--until-phase-complete",
        action="store_true",
        help="keep running active tasks until the current phase completes",
    )
    parser.add_argument(
        "--max-tasks",
        type=int,
        default=None,
        help="deprecated compatibility option; ignored when --until-phase-complete is used",
    )
    parser.add_argument(
        "--workflow",
        choices=["standard"],
        default="standard",
        help="workflow mode; Integration Agent has been removed, so only Execution -> Review -> Controller is supported",
    )
    parser.add_argument(
        "--count-by",
        choices=["task-id", "cycle"],
        default="task-id",
        help="count --tasks by unique task id or by pipeline cycle, where reworks count as another cycle (default: task-id)",
    )
    parser.add_argument(
        "--max-cycles",
        type=int,
        default=None,
        help="optional safety cap for total pipeline cycles; defaults to max(5, --tasks * 3) unless --until-phase-complete is used",
    )
    commit_group = parser.add_mutually_exclusive_group()
    commit_group.add_argument(
        "--commit-after-task",
        "--git-checkpoint",
        dest="commit_after_task",
        action="store_true",
        default=True,
        help="after each successful task closure, stage all changes and create a git checkpoint commit (default)",
    )
    commit_group.add_argument(
        "--no-commit-after-task",
        "--no-git-checkpoint",
        dest="commit_after_task",
        action="store_false",
        help="disable automatic git checkpoint commits after successful task closure",
    )
    parser.add_argument(
        "--checkpoint-message-prefix",
        default="agent checkpoint",
        help="commit message prefix for automatic git checkpoints (default: 'agent checkpoint')",
    )
    parser.add_argument(
        "--inline-diff-context",
        action="store_true",
        help="inline the compact generated diff context into Review prompts",
    )
    parser.add_argument(
        "--resume",
        dest="resume_from",
        action="store_const",
        const="auto",
        default=None,
        help="resume the current task from the first missing pipeline role based on existing artifacts",
    )
    parser.add_argument(
        "--resume-from",
        choices=["auto", "execution", "review", "controller"],
        default=None,
        help="resume a task from a specific pipeline role instead of starting from Execution",
    )
    parser.add_argument(
        "--resume-task",
        help="TASK id to resume from TASK_BOARD instead of the current Active row; requires --resume or --resume-from",
    )
    parser.add_argument("--dry-run", action="store_true", help="write prompts and planned steps without calling codex")
    parser.add_argument(
        "--codex-bin",
        default=shutil.which("codex") or "codex",
        help="path to codex executable (default: auto-detected codex)",
    )
    parser.add_argument("--model", help="optional model passed to codex exec")
    live_group = parser.add_mutually_exclusive_group()
    live_group.add_argument(
        "--live-tests",
        dest="live_tests",
        action="store_true",
        help="pass QUANT_SYSTEM_LIVE_TESTS=1 to role processes",
    )
    live_group.add_argument(
        "--no-live-tests",
        dest="live_tests",
        action="store_false",
        help="remove QUANT_SYSTEM_LIVE_TESTS from role process environment",
    )
    parser.set_defaults(live_tests=None)
    args = parser.parse_args(argv)
    if args.tasks < 1:
        parser.error("--tasks must be >= 1")
    if args.max_tasks is not None and args.max_tasks < 1:
        parser.error("--max-tasks must be >= 1")
    if args.max_cycles is not None and args.max_cycles < 1:
        parser.error("--max-cycles must be >= 1")
    if args.resume_task and args.resume_from is None:
        parser.error("--resume-task requires --resume or --resume-from")
    return args


def task_run_limit(args: argparse.Namespace) -> int | None:
    if args.until_phase_complete:
        return None
    return args.tasks


def cycle_run_limit(args: argparse.Namespace, task_limit: int | None) -> int | None:
    if args.max_cycles is not None:
        return args.max_cycles
    if args.until_phase_complete:
        return None
    assert task_limit is not None
    return max(5, task_limit * 3)


def main(argv: Sequence[str]) -> int:
    args = parse_args(argv)
    started_at = now_local()
    try:
        preflight(args)
        limit = task_run_limit(args)
        max_cycles = cycle_run_limit(args, limit)
        current = task_by_id(args.resume_task) if args.resume_task else current_active_task()
        counted_task_ids: set[str] = set()
        seen_parse_failures = 0
        cycle_count = 0
        while current is not None:
            if max_cycles is not None and cycle_count >= max_cycles:
                print_progress(f"Cycle safety cap reached after {max_cycles} cycle(s)")
                break
            if (
                limit is not None
                and args.count_by == "task-id"
                and current.task_id not in counted_task_ids
                and len(counted_task_ids) >= limit
            ):
                print_progress(f"Unique-task cap reached after {len(counted_task_ids)} task id(s)")
                break
            if limit is not None and args.count_by == "cycle" and cycle_count >= limit:
                print_progress(f"Safety cap reached after {limit} cycle(s)")
                break
            if current is None:
                break
            cycle_count += 1
            counted_task_ids.add(current.task_id)
            next_task = run_one_task(current, args, started_at)
            if args.dry_run:
                break
            if next_task is None:
                break
            try:
                current = next_task
                seen_parse_failures = 0
            except PipelineError:
                seen_parse_failures += 1
                if seen_parse_failures >= 2:
                    raise PipelineError("Could not parse Active task after Controller for consecutive checks")
                raise
        return 0
    except PipelineError as exc:
        status_update(
            task=None,
            role="failed",
            started_at=started_at,
            latest_result=str(exc),
            next_step="fix the reported issue and rerun",
            dry_run=args.dry_run,
        )
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
