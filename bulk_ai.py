#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 29 12:09:23 2025

@author: kburchardt
"""

from openai import OpenAI
import requests
import pandas as pd
import json
from collections import OrderedDict
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, BarColumn, TextColumn, TimeElapsedColumn
from rich.text import Text
from rich.columns import Columns

console = Console()

# =============================================================================
# GPT Function & Keys
# =============================================================================

client = OpenAI(
    api_key="##ADD-YOUR-KEY-HERE###"
)


def gpt(topic: str, max_children: int = 10):
    max_children = max(1, min(int(max_children), 50))  # clamp 1–50

    chat_completion = client.chat.completions.create(
        model="gpt-4o-mini",
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an SEO keyword generator. "
                    "Return JSON with keys 'main_page' and 'child_pages'. "
                    f"Include up to {max_children} child pages. "
                    "Keep keywords short-tail and directly relevant. "
                    "Avoid long-tail or repetitive phrasing."
                ),
            },
            {"role": "user", "content": f"Generate SEO structure for: {topic}"},
        ],
    )
    return chat_completion.choices[0].message.content


def get_keywords(search_question, country="en-US"):
    "Go to kwrds.ai and get your api there"
    url = "##ADD-YOUR-KEY-HERE###"
    headers = {
        "X-API-KEY": "c5276875-c61a-4e6d-9666-3fade2bbfe8b",
        "Content-Type": "application/json",
    }
    payload = {"search_question": search_question, "search_country": country}

    response = requests.post(url, headers=headers, json=payload)
    if response.status_code != 200:
        console.print(f"[red]Error {response.status_code}[/]: {response.text}")
        return pd.DataFrame()

    data = response.json()
    try:
        df = pd.DataFrame.from_dict(data)
        df.reset_index(drop=True, inplace=True)
    except Exception as e:
        console.print(f"[red]Error parsing response:[/] {e}")
        df = pd.DataFrame()
    return df


def parse_pages_input(s: str) -> list[str]:
    if not s:
        return []
    parts = [p.strip() for p in s.replace(";", ",").split(",")]
    return [p for p in parts if p]


def merge_pages(manual: list[str], gpt_pages: list[str], max_total: int | None = None) -> list[str]:
    merged = []
    seen = set()
    for lst in (manual, gpt_pages):
        for x in lst:
            if not x:
                continue
            key = x.lower()
            if key not in seen:
                merged.append(x)
                seen.add(key)
            if max_total and len(merged) >= max_total:
                return merged
    return merged


# =============================================================================
# Rich Console UI
# =============================================================================

def print_intro():
    console.rule("[bold magenta]SEO Keyword Generator[/]")
    intro = (
        "[bold]This tool[/] uses OpenAI + KWRDS.ai to generate SEO keyword plans.\n"
        "You'll be prompted for a topic, number of child pages, and any manual pages.\n"
        "Each page will fetch live keyword data."
    )
    console.print(Panel(intro, title="📘 Instructions", border_style="cyan"))


def print_topic_summary(topic, main_page, all_pages):
    table = Table(expand=True, box=None)
    table.add_column("Main Page", style="bold cyan")
    table.add_column("Child Pages", style="white")
    table.add_row(main_page, "\n".join(f"• {p}" for p in all_pages))
    console.print(Panel(table, title=f"🌐 Topic: [bold]{topic}[/]", border_style="blue"))


def progress_fetch_keywords(pages, fetch_func):
    results = {}
    total = len(pages)
    progress = Progress(
        TextColumn("[bold yellow]Fetching keywords…[/]"),
        BarColumn(),
        TextColumn("{task.completed}/{task.total}"),
        TimeElapsedColumn(),
        expand=True,
        console=console,
    )

    with progress:
        task = progress.add_task("keywords", total=total)
        for page in pages:
            progress.update(task, description=f"[cyan]Fetching:[/] {page}")
            kdf = fetch_func(page)
            results[page] = kdf
            progress.advance(task)
    return results


def print_summary(index_df, outfile):
    console.rule("[bold green]Summary[/]")
    total_rows = len(index_df) - 1
    summary = Table.grid(padding=(0, 1))
    summary.add_row("Total Child Pages:", f"[bold]{total_rows}[/]")
    summary.add_row("Total Search Volume:", f"[bold]{index_df.loc[index_df['Page type'] == 'Total', 'Search volume'].values[0]:,}[/]")
    summary.add_row("Potential Traffic (10%):", f"[cyan]{index_df.loc[index_df['Page type'] == 'Total', 'Potential traffic (10%)'].values[0]:,}[/]")
    summary.add_row("Estimated Signups (4%):", f"[green]{index_df.loc[index_df['Page type'] == 'Total', 'Est signups (4%)'].values[0]:,}[/]")

    console.print(
        Panel(
            Columns([summary]),
            title="📊 SEO Keyword Summary",
            border_style="magenta",
        )
    )
    console.print(f"[dim]Results exported to [italic]{outfile}[/]\n")


def print_completion():
    console.rule("[bold green]✅ Done[/]")
    console.print("All keyword research complete.\n")


# =============================================================================
# Main Execution
# =============================================================================

def main():
    print_intro()

    topic = input("Enter the main topic/keyword: ").strip()
    max_children = input("Max number of child pages (1–50) [default 10]: ")
    manual_str = input("Extra pages to include (comma-separated) [optional]: ").strip()

    console.print("[cyan]Generating keyword structure with GPT…[/]")
    pages = gpt(topic, max_children=max_children)
    data = json.loads(pages)

    main_page = data.get("main_page", topic)
    gpt_children = data.get("child_pages", [])

    manual_pages = parse_pages_input(manual_str)
    all_pages = merge_pages(manual_pages, gpt_children)

    print_topic_summary(topic, main_page, all_pages)

    # Collect keyword tables
    console.print("[yellow]Fetching keyword data for each child page...[/]")
    child_frames = progress_fetch_keywords(all_pages, get_keywords)

    # Build index
    rows = []
    for page, kdf in child_frames.items():
        vol_col = next((c for c in ["volume", "Search Volume", "search_volume"] if c in kdf.columns), None)
        total_volume = int(kdf[vol_col].fillna(0).sum()) if vol_col else 0
        rows.append({"Page type": page, "Search volume": total_volume})

    index_df = pd.DataFrame(rows).sort_values("Search volume", ascending=False).reset_index(drop=True)

    POTENTIAL_TRAFFIC_RATE = 0.10
    EST_SIGNUP_RATE = 0.04
    index_df["Potential traffic (10%)"] = (index_df["Search volume"] * POTENTIAL_TRAFFIC_RATE).round().astype(int)
    index_df["Est signups (4%)"] = (index_df["Potential traffic (10%)"] * EST_SIGNUP_RATE).round().astype(int)

    totals = {
        "Page type": "Total",
        "Search volume": int(index_df["Search volume"].sum()),
        "Potential traffic (10%)": int(index_df["Potential traffic (10%)"].sum()),
        "Est signups (4%)": int(index_df["Est signups (4%)"].sum()),
    }
    index_df = pd.concat([index_df, pd.DataFrame([totals])], ignore_index=True)

    outfile = "seo_keywords.xlsx"
    with pd.ExcelWriter(outfile, engine="xlsxwriter") as writer:
        index_df.to_excel(writer, index=False, sheet_name="Index")
        for page, kdf in child_frames.items():
            sheet_name = page[:31]
            kdf.to_excel(writer, index=False, sheet_name=sheet_name)

    print_summary(index_df, outfile)
    print_completion()


if __name__ == "__main__":
    main()
