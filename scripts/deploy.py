#!/usr/bin/env python3
"""Publish the site to the gh-pages branch. Always does a fresh build with the
production base path baked in first -- never republishes a stale local-preview
dist/, since that would ship the un-prefixed-path 404 bug this whole
source/build split exists to fix.

Run `python scripts/build.py` on its own any time to preview locally with zero
git/network side effects. Only this script (deploy.py) ever touches git or
pushes anything."""

import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

import build

REPO_ROOT = build.REPO_ROOT
DIST_DIR = build.DEFAULT_OUT_DIR
# Served from the custom domain root (jamesvalcourt.com), not a /jamesvalcourt
# subpath, so root-relative links need no prefix.
DEPLOY_BASE_PATH = ""
BRANCH = "gh-pages"
WORKTREE_DIR = REPO_ROOT / ".deploy" / "gh-pages-worktree"
# How long to wait for GitHub to finish building the commit we just pushed.
BUILD_POLL_SECONDS = 10
BUILD_POLL_ATTEMPTS = 18


def run(args, check=True, capture=False):
    result = subprocess.run(args, cwd=REPO_ROOT, check=False,
                             capture_output=capture, text=True)
    if check and result.returncode != 0:
        stderr = result.stderr if capture else ""
        raise RuntimeError(f"Command failed: {' '.join(args)}\n{stderr}")
    return result


def remote_has_branch(branch: str) -> bool:
    result = run(["git", "ls-remote", "--exit-code", "--heads", "origin", branch],
                 check=False, capture=True)
    return result.returncode == 0


def ensure_worktree():
    """Get the worktree onto exactly what origin/gh-pages currently is.

    The reset matters even when the worktree already exists: anything that
    commits to gh-pages outside this script (GitHub's Settings -> Pages UI
    writes CNAME commits itself, for one) leaves the local branch behind the
    remote, and the push at the end would be rejected as non-fast-forward.
    Discarding local gh-pages commits is safe because every deploy commit is a
    full snapshot of dist/, rebuilt from src/ moments ago -- never a patch on
    top of what was there before."""
    run(["git", "worktree", "prune"])

    if not remote_has_branch(BRANCH):
        print(f"No {BRANCH} branch on origin yet -- creating it (first deploy).")
        if WORKTREE_DIR.exists() and not (WORKTREE_DIR / ".git").exists():
            shutil.rmtree(WORKTREE_DIR)  # stale dir git doesn't know about
        if not (WORKTREE_DIR / ".git").exists():
            WORKTREE_DIR.parent.mkdir(parents=True, exist_ok=True)
            run(["git", "worktree", "add", "--orphan", "-b", BRANCH, str(WORKTREE_DIR)])
        return

    run(["git", "fetch", "origin", BRANCH])
    if (WORKTREE_DIR / ".git").exists():
        run(["git", "-C", str(WORKTREE_DIR), "reset", "--hard", f"origin/{BRANCH}"])
        run(["git", "-C", str(WORKTREE_DIR), "clean", "-fdq"])
    else:
        if WORKTREE_DIR.exists():
            shutil.rmtree(WORKTREE_DIR)  # stale dir git doesn't know about
        WORKTREE_DIR.parent.mkdir(parents=True, exist_ok=True)
        print(f"Found existing origin/{BRANCH}, checking it out into worktree...")
        run(["git", "worktree", "add", str(WORKTREE_DIR), f"origin/{BRANCH}", "-B", BRANCH])


def sync_worktree_with_dist():
    # Clear everything currently tracked, then repopulate from dist/. Handles
    # deletions/renames cleanly (e.g. a blog post slug changed since last deploy).
    run(["git", "-C", str(WORKTREE_DIR), "rm", "-rf", "--quiet", "."], check=False)
    for item in DIST_DIR.iterdir():
        dest = WORKTREE_DIR / item.name
        if item.is_dir():
            shutil.copytree(item, dest, dirs_exist_ok=True)
        else:
            shutil.copy2(item, dest)


def commit_dist_snapshot() -> str | None:
    """Stage dist/ over the worktree and commit it. Returns the new gh-pages
    sha, or None when the build is byte-identical to what's already published."""
    sync_worktree_with_dist()
    run(["git", "-C", str(WORKTREE_DIR), "add", "-A"])
    status = run(["git", "-C", str(WORKTREE_DIR), "status", "--porcelain"], capture=True)
    if not status.stdout.strip():
        return None

    sha = run(["git", "rev-parse", "--short", "HEAD"], capture=True).stdout.strip()
    run(["git", "-C", str(WORKTREE_DIR), "commit", "-m", f"Deploy site from main@{sha}"])
    return run(["git", "-C", str(WORKTREE_DIR), "rev-parse", "HEAD"], capture=True).stdout.strip()


def gh_pages_api(path: str):
    """GET a Pages API endpoint via the gh CLI. Returns None if gh isn't
    installed or isn't authenticated -- verification is a nicety, not a
    requirement, and the deploy itself only ever needs git."""
    if shutil.which("gh") is None:
        return None
    result = run(["gh", "api", f"repos/{{owner}}/{{repo}}/pages/{path}"],
                 check=False, capture=True)
    if result.returncode != 0:
        return None
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return None


def wait_for_pages_build(expected_sha: str):
    """Confirm GitHub actually built the commit we just pushed. Pages can serve
    one stale build for a while after a settings change, so 'pushed' is not the
    same as 'live' -- this is the check that tells the two apart."""
    for attempt in range(BUILD_POLL_ATTEMPTS):
        latest = gh_pages_api("builds/latest")
        if latest is None:
            print("Skipping build check (gh CLI unavailable or not authenticated).")
            return
        status, commit = latest.get("status"), latest.get("commit")
        if commit == expected_sha and status == "built":
            print(f"GitHub Pages built {expected_sha[:7]} -- the deploy is live.")
            return
        if commit == expected_sha and status == "errored":
            message = (latest.get("error") or {}).get("message") or "no message"
            raise RuntimeError(f"GitHub Pages failed to build {expected_sha[:7]}: {message}")
        if attempt == 0:
            print(f"Waiting for GitHub Pages to build {expected_sha[:7]}...")
        time.sleep(BUILD_POLL_SECONDS)

    print(
        f"warning: gave up waiting after {BUILD_POLL_ATTEMPTS * BUILD_POLL_SECONDS}s. "
        f"The push succeeded; check the build with:\n"
        f"  gh api repos/{{owner}}/{{repo}}/pages/builds/latest\n"
        f"and confirm its 'commit' is {expected_sha}."
    )


def publish():
    is_first_deploy = not remote_has_branch(BRANCH)

    print(f"Building with base_path={DEPLOY_BASE_PATH!r}...")
    build.build_site(base_path=DEPLOY_BASE_PATH, out_dir=DIST_DIR)
    (DIST_DIR / ".nojekyll").touch()

    ensure_worktree()
    pushed_sha = commit_dist_snapshot()
    if pushed_sha is None:
        print("Nothing changed since the last deploy -- skipping commit/push.")
        return

    push = run(["git", "-C", str(WORKTREE_DIR), "push", "origin", f"HEAD:{BRANCH}"],
               check=False, capture=True)
    if push.returncode != 0:
        # Someone/something pushed to gh-pages between our fetch and our push.
        # Rebuild the snapshot on top of whatever landed and try once more.
        print("Push rejected -- refreshing from origin and retrying once...")
        ensure_worktree()
        pushed_sha = commit_dist_snapshot()
        if pushed_sha is None:
            print(f"origin/{BRANCH} already matches this build -- nothing to push.")
            return
        run(["git", "-C", str(WORKTREE_DIR), "push", "origin", f"HEAD:{BRANCH}"])
    print(f"\nPushed to origin/{BRANCH}.")

    wait_for_pages_build(pushed_sha)

    if is_first_deploy:
        print(
            "\nFirst deploy done. One-time manual step required:\n"
            "  GitHub repo -> Settings -> Pages -> Source: 'Deploy from a branch'\n"
            f"  Branch: {BRANCH} / (root)\n"
            "  (equivalent: gh api -X PUT repos/jrvalcourt/jamesvalcourt/pages "
            f"-f source[branch]={BRANCH} -f 'source[path]=/')"
        )


if __name__ == "__main__":
    try:
        publish()
    except RuntimeError as e:
        print(f"error: {e}", file=sys.stderr)
        sys.exit(1)
