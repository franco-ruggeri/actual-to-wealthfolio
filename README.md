# wealthfolio-actualbudget-sync

Wealthfolio addon to sync data with Actual Budget.

## Current Status

- Addon shell is wired into the Wealthfolio sidebar.
- Addon route is available at `/addon/wealthfolio-actualbudget-sync`.
- UI currently includes a `Sync` button placeholder.
- Sync logic is not implemented yet.

## Development

```bash
# Install dependencies
pnpm install

# Start Wealthfolio dev server
pnpm dev:server

# Type-check
pnpm type-check

# Build addon
pnpm build

# Package addon zip
pnpm bundle
```

## Project Structure

- `src/addon.tsx`: addon entry and UI.
- `manifest.json`: addon metadata.
- `dist/addon.js`: build output.

## License

MIT
