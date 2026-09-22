#!/usr/bin/env bun
/**
 * bump-plugin-version.ts — bump a version as a single action: worktree off origin/<base>
 * → edit the version field(s) → commit → push → open a PR.
 *
 * Two targets:
 *   1. A plugin (e.g. "trading"): bumps <plugin>/.claude-plugin/plugin.json's "version",
 *      AND syncs that same value into this plugin's entry in the root
 *      .claude-plugin/marketplace.json "plugins" array — these two must never drift, since
 *      marketplace.json's per-plugin "version" is what PINS installs to a release (per
 *      Claude Code's plugin-marketplace docs: omit it and every push is treated as an
 *      update; set it and installs only update when the string changes).
 *   2. "marketplace": bumps the top-level "version" field in
 *      .claude-plugin/marketplace.json itself (the collection as a whole). This field is
 *      cosmetic to Claude Code's installer (Anthropic's own marketplace.json never bumps
 *      it either) but versions the repo as a unit, which is the point of tracking it here.
 *
 * Usage:
 *   bun scripts/bump-plugin-version.ts <plugin|marketplace> <patch|minor|major|X.Y.Z> [options]
 *
 * Options:
 *   --reason "..."    One-line reason, used in the commit message and PR body.
 *                      Defaults to "Version bump." — pass a real reason when you have one.
 *   --base <branch>   Base branch to branch/PR against (default: main).
 *   --no-pr           Push the branch but skip opening a PR.
 *   --dry-run         Print what would happen; make no changes, no git/gh calls that mutate state.
 *
 * Examples:
 *   bun scripts/bump-plugin-version.ts trading patch --reason "EDGAR protocol doc fix (#15), no behavior change"
 *   bun scripts/bump-plugin-version.ts lifesystems 0.2.0 --reason "Adds Dance workflow"
 *   bun scripts/bump-plugin-version.ts marketplace minor --reason "Added the lifesystems plugin"
 *
 * Requires: git, gh (authenticated). Can be run from ANYWHERE inside ANY worktree of a
 * davdunc-plugins checkout, on ANY currently-checked-out branch — "current version" is
 * always read from origin/<base> via `git show`, never from the invoking worktree's
 * working directory. (Earlier versions of this script read plugin.json/marketplace.json
 * off disk in the "root" clone, which silently used whatever branch that clone happened
 * to have checked out instead of the real base ref — fixed 2026-09-22.)
 *
 * Leaves the created worktree in place — same convention this repo has used by hand:
 * remove it after the PR merges (`git worktree remove <path>`), not before.
 */

import { $ } from "bun";
import { readFileSync, writeFileSync, existsSync } from "fs";
import { join } from "path";

type Bump = "patch" | "minor" | "major";
const MARKETPLACE_TARGET = "marketplace";
const MARKETPLACE_REL_PATH = join(".claude-plugin", "marketplace.json");

function usageError(msg: string): never {
  console.error(`Error: ${msg}\n`);
  console.error(
    'Usage: bun scripts/bump-plugin-version.ts <plugin|marketplace> <patch|minor|major|X.Y.Z> [--reason "..."] [--base main] [--no-pr] [--dry-run]'
  );
  process.exit(1);
}

function parseArgs(argv: string[]) {
  const [target, bumpArg, ...rest] = argv;
  if (!target || !bumpArg) usageError("missing <plugin|marketplace> and/or <patch|minor|major|X.Y.Z>");

  let reason = "Version bump.";
  let base = "main";
  let openPr = true;
  let dryRun = false;

  for (let i = 0; i < rest.length; i++) {
    const a = rest[i];
    if (a === "--reason") reason = rest[++i] ?? usageError("--reason needs a value");
    else if (a === "--base") base = rest[++i] ?? usageError("--base needs a value");
    else if (a === "--no-pr") openPr = false;
    else if (a === "--dry-run") dryRun = true;
    else usageError(`unrecognized argument: ${a}`);
  }

  return { target, bumpArg, reason, base, openPr, dryRun };
}

function bumpSemver(current: string, bumpArg: string, sourceLabel: string): string {
  const m = current.match(/^(\d+)\.(\d+)\.(\d+)$/);
  if (!m) usageError(`current version "${current}" in ${sourceLabel} is not plain X.Y.Z semver — bump it by hand`);
  const [, maj, min, pat] = m.map(Number) as unknown as [never, number, number, number];

  if (/^\d+\.\d+\.\d+$/.test(bumpArg)) {
    if (bumpArg === current) usageError(`new version ${bumpArg} is the same as the current version in ${sourceLabel}`);
    return bumpArg;
  }

  const bump = bumpArg as Bump;
  if (bump === "patch") return `${maj}.${min}.${pat + 1}`;
  if (bump === "minor") return `${maj}.${min + 1}.0`;
  if (bump === "major") return `${maj + 1}.0.0`;
  usageError(`"${bumpArg}" is not patch, minor, major, or X.Y.Z`);
}

/**
 * The main repo root — NOT `git rev-parse --show-toplevel`, which returns the CURRENT
 * worktree's root. This script is often run from inside a worktree (e.g. while building
 * or testing it), so it needs the shared repo root all worktrees hang off of.
 * `--git-common-dir` is the one path that's the same from any worktree.
 */
async function repoRoot(): Promise<string> {
  const out = await $`git rev-parse --path-format=absolute --git-common-dir`.text();
  const gitDir = out.trim();
  return join(gitDir, "..");
}

/**
 * Read and parse a JSON file's content AT A GIT REF — never off disk. This is what makes
 * the script correct regardless of which branch happens to be checked out wherever it's
 * invoked from: `origin/<base>` is the only source of truth for "current".
 */
async function readJsonAtRef(root: string, ref: string, relPath: string): Promise<any> {
  const text = await $`git show ${ref}:${relPath}`.cwd(root).text().catch(() => {
    usageError(`"${relPath}" does not exist at ${ref} — wrong path or wrong base branch?`);
  });
  try {
    return JSON.parse(text as string);
  } catch {
    usageError(`"${relPath}" at ${ref} is not valid JSON`);
  }
}

function readJson(path: string): any {
  return JSON.parse(readFileSync(path, "utf-8"));
}

function writeJson(path: string, obj: unknown): void {
  // 2-space indent + trailing newline matches this repo's existing JSON style.
  writeFileSync(path, JSON.stringify(obj, null, 2) + "\n");
}

async function main() {
  const { target, bumpArg, reason, base, openPr, dryRun } = parseArgs(process.argv.slice(2));
  const isMarketplace = target === MARKETPLACE_TARGET;

  const root = await repoRoot();
  const baseRef = `origin/${base}`;

  await $`git fetch origin`.cwd(root);

  const pluginRelPath = join(target, ".claude-plugin", "plugin.json");
  let current: string;
  let sourceLabel: string;

  if (isMarketplace) {
    const mkt = await readJsonAtRef(root, baseRef, MARKETPLACE_REL_PATH);
    current = mkt.version;
    sourceLabel = `${baseRef}:${MARKETPLACE_REL_PATH}`;
    if (!current) usageError(`${sourceLabel} has no top-level "version" field yet — bootstrap it by hand first`);
  } else {
    const pkg = await readJsonAtRef(root, baseRef, pluginRelPath);
    current = pkg.version;
    sourceLabel = `${baseRef}:${pluginRelPath}`;
    if (!current) usageError(`${sourceLabel} has no "version" field to bump`);

    const mkt = await readJsonAtRef(root, baseRef, MARKETPLACE_REL_PATH);
    const entry = (mkt.plugins ?? []).find((p: any) => p.name === target);
    if (!entry) usageError(`no "${target}" entry in ${baseRef}:${MARKETPLACE_REL_PATH}'s plugins[] — name mismatch, or not a real plugin?`);
  }

  const next = bumpSemver(current, bumpArg, sourceLabel);
  const branch = `chore/${target}-v${next}`;
  const worktreePath = join(root, "..", ".worktrees", `bump-${target}-${next}`);

  console.log(`${target}: ${current} -> ${next}  (current read from ${sourceLabel})`);
  console.log(`branch: ${branch}`);
  console.log(`worktree: ${worktreePath}`);
  console.log(`base: ${baseRef}`);
  console.log(`reason: ${reason}`);
  if (!isMarketplace) console.log(`also syncing: marketplace.json plugins[].version for "${target}"`);

  if (dryRun) {
    console.log("\n--dry-run: no changes made.");
    return;
  }

  await $`git worktree add ${worktreePath} -b ${branch} ${baseRef}`.cwd(root);

  const wtMarketplaceJsonPath = join(worktreePath, MARKETPLACE_REL_PATH);
  const changedFiles: string[] = [];

  if (isMarketplace) {
    const wtMkt = readJson(wtMarketplaceJsonPath);
    wtMkt.version = next;
    writeJson(wtMarketplaceJsonPath, wtMkt);
    changedFiles.push(MARKETPLACE_REL_PATH);
  } else {
    const wtPluginJsonPath = join(worktreePath, pluginRelPath);
    const wtPkg = readJson(wtPluginJsonPath);
    wtPkg.version = next;
    writeJson(wtPluginJsonPath, wtPkg);
    changedFiles.push(pluginRelPath);

    const wtMkt = readJson(wtMarketplaceJsonPath);
    const entry = (wtMkt.plugins ?? []).find((p: any) => p.name === target);
    if (!entry) usageError(`"${target}" vanished from marketplace.json between the ref read and the worktree checkout — race condition?`);
    entry.version = next;
    writeJson(wtMarketplaceJsonPath, wtMkt);
    changedFiles.push(MARKETPLACE_REL_PATH);
  }

  const commitMsg = `${target}: bump version to ${next}\n\n${reason}\n\nCo-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>\nClaude-Session: https://claude.ai/code/session_016mfRe2cLXJNviRxStzTXSh`;

  await $`git add ${changedFiles}`.cwd(worktreePath);
  await $`git commit -m ${commitMsg}`.cwd(worktreePath);
  await $`git push -u origin ${branch}`.cwd(worktreePath);

  console.log(`\nPushed ${branch}.`);

  if (!openPr) {
    console.log("--no-pr: branch pushed, no PR opened.");
    return;
  }

  const prTitle = `${target}: bump version to ${next}`;
  const prBody = `${reason}\n\n🤖 Generated with [Claude Code](https://claude.com/claude-code)\n\nhttps://claude.ai/code/session_016mfRe2cLXJNviRxStzTXSh`;
  const prUrl = (
    await $`gh pr create --repo davdunc/davdunc-plugins --base ${base} --head ${branch} --title ${prTitle} --body ${prBody}`
      .cwd(worktreePath)
      .text()
  ).trim();

  console.log(`PR opened: ${prUrl}`);
  console.log(`Not merged — that's a separate step. Worktree left at ${worktreePath}; remove it after merge.`);
}

main().catch((e) => {
  console.error(e?.stderr?.toString?.() ?? e);
  process.exit(1);
});
