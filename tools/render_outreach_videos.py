"""Render the published outreach walkthroughs as narrated MP4 files."""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from edge_tts import Communicate
from imageio_ffmpeg import get_ffmpeg_exe
from playwright.async_api import async_playwright


ROOT = Path(__file__).resolve().parents[1]
PROOFS = ROOT / "proofs"
EDGE = Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe")
VOICE = "en-US-AndrewMultilingualNeural"
SLUGS = [
    "l-e-electrical-services",
    "if-houston",
    "cutting-edge-flooring-services",
    "air-innovations",
    "avalon-insurance-agency",
    "aaigot-insurance-agency",
    "atlas-janitorial-services",
    "evergreen-lawn-care-tx",
    "wood-group-mortgage",
    "dmr-mortgage",
    "911-houston-movers",
    "met-plumbing",
    "moss-roofing-houston",
    "infinity-roofing",
    "bluebonnet-exteriors-htx",
    "dempsey-family-electric",
    "pjs-of-houston",
    "fernandez-landscapes",
    "strutton-plumbing",
    "loa-construction",
]


def run_ffmpeg(*args: str) -> None:
    command = [get_ffmpeg_exe(), "-hide_banner", "-loglevel", "error", "-y", *args]
    subprocess.run(command, check=True)


async def make_narration(texts: list[str], durations: list[int], work: Path) -> Path:
    padded: list[Path] = []
    for index, (text, duration) in enumerate(zip(texts, durations)):
        raw = work / f"voice-{index}.mp3"
        wav = work / f"voice-{index}.wav"
        await Communicate(text, VOICE, rate="+10%", pitch="-2Hz").save(str(raw))
        run_ffmpeg(
            "-i", str(raw),
            "-af", f"apad=pad_dur={duration},atrim=0:{duration}",
            "-ar", "48000", "-ac", "2", "-c:a", "pcm_s16le", str(wav),
        )
        padded.append(wav)

    concat = "".join(f"[{i}:a]" for i in range(len(padded)))
    output = work / "narration.wav"
    inputs: list[str] = []
    for item in padded:
        inputs.extend(["-i", str(item)])
    run_ffmpeg(*inputs, "-filter_complex", f"{concat}concat=n={len(padded)}:v=0:a=1[out]", "-map", "[out]", str(output))
    return output


async def render_one(browser, slug: str, semaphore: asyncio.Semaphore) -> tuple[str, int]:
    async with semaphore:
        source = PROOFS / slug / "index.html"
        output = PROOFS / slug / "walkthrough.mp4"
        if not source.exists():
            raise FileNotFoundError(source)

        with tempfile.TemporaryDirectory(prefix=f"avenity-{slug}-") as temp_name:
            work = Path(temp_name)
            video_dir = work / "video"
            video_dir.mkdir()
            context = await browser.new_context(
                viewport={"width": 1280, "height": 720},
                record_video_dir=str(video_dir),
                record_video_size={"width": 1280, "height": 720},
            )
            page = await context.new_page()
            await page.goto(source.as_uri(), wait_until="load")
            await page.evaluate("document.body.style.zoom='0.78'")
            payload = await page.evaluate("() => ({texts, durations: dur})")
            texts = list(payload["texts"])
            durations = [int(value) for value in payload["durations"]]
            await page.evaluate("speechSynthesis.speak = () => {}; speechSynthesis.cancel = () => {}")
            video = page.video
            await page.click("#play")
            await page.wait_for_timeout((sum(durations) + 1) * 1000)
            await context.close()
            visual = Path(await video.path())
            narration = await make_narration(texts, durations, work)
            run_ffmpeg(
                "-i", str(visual), "-i", str(narration),
                "-t", str(sum(durations)),
                "-c:v", "libx264", "-preset", "medium", "-crf", "25",
                "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k",
                "-movflags", "+faststart", str(output),
            )
        return slug, output.stat().st_size


async def render(slugs: list[str], concurrency: int) -> None:
    if not EDGE.exists():
        raise FileNotFoundError(EDGE)
    semaphore = asyncio.Semaphore(concurrency)
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(executable_path=str(EDGE), headless=True)
        try:
            tasks = [asyncio.create_task(render_one(browser, slug, semaphore)) for slug in slugs]
            for task in asyncio.as_completed(tasks):
                slug, size = await task
                print(json.dumps({"rendered": slug, "bytes": size}), flush=True)
        finally:
            await browser.close()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int)
    parser.add_argument("--slug", action="append")
    parser.add_argument("--concurrency", type=int, default=4)
    args = parser.parse_args()
    slugs = args.slug or SLUGS
    if args.limit:
        slugs = slugs[: args.limit]
    asyncio.run(render(slugs, args.concurrency))


if __name__ == "__main__":
    main()
