"""Small dependency-free desktop UI for the helpdesk agent.

Run from starter_v0 with:
    python ui.py --provider openrouter --model openai/gpt-4o-mini --version v0
"""

from __future__ import annotations

import argparse
import json
import tkinter as tk
from pathlib import Path
from tkinter import scrolledtext
from typing import Any

from chat import (
    ARTIFACTS_DIR,
    ROOT,
    load_lab_env,
    run_model_tool_loop,
    safe_slug,
    trim_history,
)
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from versioning import artifact_version_dict, build_artifact_version


class HelpdeskUI:
    def __init__(
        self,
        root_window: tk.Tk,
        *,
        provider: Any,
        provider_name: str,
        model: str | None,
        version: str,
        system_prompt: str,
        tools: list[dict[str, Any]],
        transcript_path: Path,
        history_window: int,
        max_tool_rounds: int,
        artifact_version: dict[str, str],
    ) -> None:
        self.window = root_window
        self.provider = provider
        self.model = model
        self.system_prompt = system_prompt
        self.tools = tools
        self.transcript_path = transcript_path
        self.history_window = history_window
        self.max_tool_rounds = max_tool_rounds
        self.history: list[dict[str, str]] = []
        self.transcript: dict[str, Any] = {
            "transcript_id": transcript_path.stem,
            **artifact_version,
            "provider": provider_name,
            "model": model,
            "history_window": history_window,
            "max_tool_rounds": max_tool_rounds,
            "turns": [],
        }

        self.window.title(f"Northstar Helpdesk - {version}")
        self.window.geometry("980x700")
        self.output = scrolledtext.ScrolledText(self.window, state="disabled", wrap=tk.WORD)
        self.output.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        bottom = tk.Frame(self.window)
        bottom.pack(fill=tk.X, padx=8, pady=(0, 8))
        self.entry = tk.Entry(bottom)
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.entry.bind("<Return>", lambda _event: self.send())
        tk.Button(bottom, text="Send", command=self.send).pack(side=tk.LEFT, padx=(8, 0))
        self._append(f"Version: {artifact_version['artifact_version']}\nType /exit to close.\n")

    def _append(self, text: str) -> None:
        self.output.configure(state="normal")
        self.output.insert(tk.END, text + "\n")
        self.output.see(tk.END)
        self.output.configure(state="disabled")

    def send(self) -> None:
        user_text = self.entry.get().strip()
        if not user_text:
            return
        self.entry.delete(0, tk.END)
        if user_text in {"/exit", "/quit"}:
            self.window.destroy()
            return
        self._append(f"You> {user_text}")
        messages = [
            {"role": "system", "content": self.system_prompt},
            *trim_history(self.history, self.history_window),
            {"role": "user", "content": user_text},
        ]
        try:
            result = run_model_tool_loop(
                provider=self.provider,
                messages=messages,
                tools=self.tools,
                model=self.model,
                max_tool_rounds=self.max_tool_rounds,
            )
        except Exception as exc:
            result = {"status": "provider_error", "assistant_text": "", "error": f"{type(exc).__name__}: {exc}", "rounds": [], "tool_events": []}
        for event in result.get("tool_events", []):
            self._append(
                "[tool] "
                f"{event.get('tool')}({json.dumps(event.get('args', {}), ensure_ascii=False)})\n"
                f"result={json.dumps(event.get('result', {}), ensure_ascii=False, indent=2)}"
            )
        self._append(f"Agent [{result.get('status')}]> {result.get('assistant_text', '')}")
        self.history.extend([
            {"role": "user", "content": user_text},
            {"role": "assistant", "content": result.get("assistant_text", "")},
        ])
        self.transcript["turns"].append({"user": user_text, **result})
        self.transcript_path.parent.mkdir(parents=True, exist_ok=True)
        self.transcript_path.write_text(json.dumps(self.transcript, ensure_ascii=False, indent=2, default=str), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Dependency-free IT Helpdesk desktop UI.")
    parser.add_argument("--provider", choices=["openrouter", "openai", "anthropic", "gemini"], required=True)
    parser.add_argument("--model", default=None)
    parser.add_argument("--version", required=True)
    parser.add_argument("--system-prompt", type=Path, default=ARTIFACTS_DIR / "system_prompt.md")
    parser.add_argument("--tools", type=Path, default=ARTIFACTS_DIR / "tools.yaml")
    parser.add_argument("--transcripts-dir", type=Path, default=ROOT / "transcripts")
    parser.add_argument("--history-window", type=int, default=5)
    parser.add_argument("--max-tool-rounds", type=int, default=4)
    args = parser.parse_args()
    load_lab_env(ROOT)
    system_prompt = args.system_prompt.read_text(encoding="utf-8")
    declarations = load_tool_declarations(args.tools)
    provider = make_provider(args.provider)
    model = args.model or getattr(provider, "default_model", None)
    artifact = artifact_version_dict(build_artifact_version(args.version, args.system_prompt, args.tools))
    transcript_id = f"{safe_slug(args.version)}_{safe_slug(args.provider)}_ui"
    ui = tk.Tk()
    HelpdeskUI(
        ui,
        provider=provider,
        provider_name=args.provider,
        model=model,
        version=args.version,
        system_prompt=system_prompt,
        tools=to_openai_tools(declarations),
        transcript_path=args.transcripts_dir / f"{transcript_id}.transcript.json",
        history_window=args.history_window,
        max_tool_rounds=args.max_tool_rounds,
        artifact_version=artifact,
    )
    ui.mainloop()


if __name__ == "__main__":
    main()
