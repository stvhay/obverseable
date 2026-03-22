"""
Phase 0-2: Setup + Surface Recon + Source Recovery.

Single script that navigates to a target, fingerprints, classifies scripts,
extracts source maps for all app bundles, and writes everything to the
case study directory.

Usage:
    uv run python .claude/skills/geckordp/tools/phase_recon.py <url> <target_dir>

Example:
    uv run python .claude/skills/geckordp/tools/phase_recon.py \
        https://todomvc.com/examples/react/dist/ \
        casestudies/todomvc.com
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from recon import RDPSession, write_json, write_sources


def run(url, target_dir, impl_name=None):
    """Run phases 0-2 on a single URL."""
    os.makedirs(os.path.join(target_dir, "raw/sources"), exist_ok=True)
    os.makedirs(os.path.join(target_dir, "raw/network"), exist_ok=True)
    os.makedirs(os.path.join(target_dir, "notes"), exist_ok=True)

    prefix = f"{impl_name}_" if impl_name else ""

    with RDPSession() as s:
        # Phase 0: Navigate
        s.navigate(url, wait=4.0)
        print(f"[recon] Navigated to {url}")

        # Phase 1: Surface recon
        surface = s.fingerprint()
        write_json(surface, os.path.join(target_dir, f"notes/{prefix}surface.json"))
        print(f"[recon] Fingerprint: {surface.get('title', '?')}")

        scripts = s.classify_scripts()
        write_json(scripts, os.path.join(target_dir, f"notes/{prefix}scripts.json"))
        print(f"[recon] Scripts classified: {len(scripts)}")
        for sc in scripts:
            src_label = sc.get("src") or f"inline ({sc['len']}b)"
            print(f"  [{sc['role']:15s}] {src_label}")

        # Phase 2: Source recovery — extract source maps for all app bundles
        app_scripts = [sc for sc in scripts if sc["role"] == "app" and sc.get("src")]
        infra_scripts = [sc for sc in scripts if sc["role"] == "shared-infra" and sc.get("src")]

        all_sources = {}
        for sc in app_scripts + infra_scripts:
            src_url = sc["src"]
            print(f"[recon] Extracting source map: {src_url}")
            sources = s.extract_source_map(src_url)
            if sources:
                app_only = {k: v for k, v in sources.items() if k != "__bundle__"}
                if app_only:
                    subdir = impl_name or "main"
                    write_sources(app_only, os.path.join(target_dir, f"raw/sources/{subdir}/"))
                    print(f"  Source map: {len(app_only)} files")
                    all_sources.update(app_only)
                elif "__bundle__" in sources:
                    fname = os.path.basename(src_url)
                    subdir = impl_name or "main"
                    out = os.path.join(target_dir, f"raw/sources/{subdir}/{fname}")
                    os.makedirs(os.path.dirname(out), exist_ok=True)
                    with open(out, "w") as f:
                        f.write(sources["__bundle__"])
                    print(f"  No source map, saved raw bundle ({len(sources['__bundle__'])} chars)")
            else:
                print(f"  Failed to fetch")

        # Also get inline scripts
        inlines = s.eval_json(
            '''JSON.stringify([...document.querySelectorAll("script:not([src])")].map((s,i) => ({
                index: i, len: s.textContent.length,
                content: s.textContent.slice(0, 500)
            })))'''
        )
        if inlines:
            write_json(inlines, os.path.join(target_dir, f"notes/{prefix}inline_scripts.json"))

        # Fetch CSS source files (for mechanism analysis, not just computed values)
        print("[recon] Fetching CSS sources...")
        css_sources = s.fetch_css_sources()
        for css in css_sources:
            fname = css["href"].split("/")[-1].split("?")[0] or "stylesheet.css"
            out = os.path.join(target_dir, f"raw/sources/{impl_name or 'main'}/{fname}")
            os.makedirs(os.path.dirname(out), exist_ok=True)
            with open(out, "w") as f:
                f.write(css["content"])
            print(f"  CSS: {fname} ({len(css['content'])} chars)")

        # Capture network on reload
        print("[recon] Capturing network traffic...")
        traffic = s.capture_network(action="reload", wait=5.0)
        write_json(traffic, os.path.join(target_dir, f"raw/network/{prefix}capture.json"))
        print(f"[recon] Network: {len(traffic)} requests")

        # Extract computed styles for key selectors discovered on the page.
        # Uses semantic HTML tags + classes found in the DOM, not hardcoded selectors.
        discovered_selectors = s.eval_json(
            """JSON.stringify((() => {
                const sels = new Set(['body', 'h1', 'h2', 'h3', 'header', 'main', 'footer', 'nav', 'aside']);
                // Add elements with class attributes (up to 30)
                document.querySelectorAll('[class]').forEach(el => {
                    if (sels.size >= 30) return;
                    const cls = el.classList[0];
                    if (cls && cls.length < 30) sels.add('.' + cls);
                });
                return [...sels];
            })())"""
        )
        if discovered_selectors:
            styles = s.extract_styles(discovered_selectors)
            if styles:
                found = [st for st in styles if st.get("found")]
                write_json(styles, os.path.join(target_dir, f"notes/{prefix}styles.json"))
                print(f"[recon] Styles extracted for {len(found)}/{len(discovered_selectors)} selectors")

    summary = {
        "url": url,
        "title": surface.get("title"),
        "scripts_total": len(scripts),
        "scripts_by_role": {},
        "source_files_recovered": len(all_sources),
        "network_requests": len(traffic),
        "styles_extracted": len([s for s in (styles or []) if s.get("found")]),
    }
    for sc in scripts:
        role = sc["role"]
        summary["scripts_by_role"][role] = summary["scripts_by_role"].get(role, 0) + 1

    write_json(summary, os.path.join(target_dir, f"notes/{prefix}recon_summary.json"))
    print(f"\n[recon] Done. Summary written to notes/{prefix}recon_summary.json")
    return summary


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: phase_recon.py <url> <target_dir> [impl_name]")
        sys.exit(1)
    url = sys.argv[1]
    target_dir = sys.argv[2]
    impl_name = sys.argv[3] if len(sys.argv) > 3 else None
    run(url, target_dir, impl_name)
