"""Command-line interface for Local-First Signal."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer
from rich import print as rprint
from rich.console import Console

from lfs.core.preset import Preset, example_local_first_signal
from lfs.dsp.engine import render_to_wav
from lfs.semantic.classifier import classify
from lfs.semantic.prompt_compiler import compile_prompt, prompt_to_text

app = typer.Typer(help="Local-First Signal — offline generative music AI")
console = Console()


@app.command()
def render(
    preset: Optional[Path] = typer.Option(None, help="Path to preset JSON"),
    out: Path = typer.Option("output.wav", help="Output WAV path"),
    length: float = typer.Option(30.0, help="Length in seconds"),
    seed: Optional[int] = typer.Option(None, help="Override seed"),
):
    """Render a preset to WAV (deterministic)."""
    if preset is None:
        p = example_local_first_signal()
        rprint("[yellow]No preset given — using flagship 'Local-First Signal'[/yellow]")
    else:
        data = json.loads(preset.read_text())
        p = Preset.from_dict(data)

    if seed is not None:
        p.seed = seed

    rprint(f"Rendering [bold]{p.name}[/bold] (seed={p.seed}) → {out}")
    render_to_wav(p, str(out), length_sec=length)
    rprint(f"[green]Done.[/green] Wrote {out}")


@app.command()
def prompt(
    preset: Optional[Path] = typer.Option(None, help="Path to preset JSON"),
    format: str = typer.Option("text", help="text | json"),
    seed: Optional[int] = typer.Option(None),
):
    """Generate a Suno-style prompt from a preset."""
    if preset is None:
        p = example_local_first_signal()
    else:
        data = json.loads(preset.read_text())
        p = Preset.from_dict(data)

    if seed is not None:
        p.seed = seed

    profile = classify(p)
    suno = compile_prompt(profile)

    if format == "json":
        print(json.dumps(suno.__dict__, indent=2))
    else:
        print(prompt_to_text(suno))


@app.command()
def classify_cmd(
    preset: Optional[Path] = typer.Option(None, "--preset"),
):
    """Show the sonic profile extracted from a preset."""
    if preset is None:
        p = example_local_first_signal()
    else:
        data = json.loads(preset.read_text())
        p = Preset.from_dict(data)

    profile = classify(p)
    rprint(profile)


@app.command()
def version():
    """Show version."""
    from lfs import __version__
    rprint(f"Local-First Signal v{__version__}")


if __name__ == "__main__":
    app()