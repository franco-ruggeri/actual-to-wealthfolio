# AGENTS.md

Operational guide for coding agents working in `wealthfolio-actualbudget-sync`.

## Project Snapshot

- TypeScript addon for Wealthfolio.
- Entry file: `src/addon.tsx`.
- Build output: `dist/addon.js`.
- Addon metadata: `manifest.json`.
- Package manager lockfile: `pnpm-lock.yaml` (prefer `pnpm`).

## Commands

Use these commands for local validation and packaging:

- Install dependencies: `pnpm install`
- Type-check: `pnpm type-check`
- Build addon: `pnpm build`
- Package zip bundle: `pnpm bundle`
- Run Wealthfolio dev server (when available): `pnpm dev:server`

## Definition of Done

Before finishing code changes, run when relevant:

1. `pnpm type-check`
2. `pnpm build`

If a command cannot run in the current environment, report the failure and the reason.

## Coding Guidelines

- Follow existing patterns in `src/addon.tsx` and keep changes scoped.
- Prefer small, explicit React components and handlers.
- Keep UI text concise and action-oriented.
- Use `@wealthfolio/ui` components instead of ad-hoc primitives when possible.
- Avoid adding dependencies unless required by the task.
- Do not add placeholder abstractions for logic that does not exist yet.

## Git and Change Hygiene

- Do not revert user changes outside the requested scope.
- Keep commits focused and use Conventional Commits (`feat:`, `fix:`, `docs:`, etc.).
- Do not force-push or rewrite history unless explicitly requested.

## Notes

- The legacy Python project docs live in `old/AGENTS.md` and do not apply to the addon code.
