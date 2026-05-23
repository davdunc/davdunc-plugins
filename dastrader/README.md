# dastrader

DAS Trader Pro hotkey, button, and routing assistant for Cobra Trading users (Cobra Trading / DAS Trader Pro).

## What this skill does

- Writes Classic and Advanced DAS hotkey scripts
- Builds TriggerOrder OCO brackets (stop + target) attached at entry
- Sizes positions by fixed share count or by % equity risk
- Guides route selection (ARCAL, EDGXM, SMRTL, etc.) for momentum, large size, and extended hours
- Debugs broken scripts (arithmetic precedence trap, missing TIF compatibility, etc.)
- Explains when each script pattern is appropriate

## Reference files

- `skills/dastrader/references/hotkey-scripting.md` — syntax, variables, 16 examples
- `skills/dastrader/references/order-types-routing.md` — all routes, TIFs, stop types
- `skills/dastrader/references/cmd-api.md` — CMD API TCP protocol, NEWORDER, das-bridge

## Usage

Install this plugin and ask things like:

- "Write a hotkey that buys 200 shares at ask+0.05 with a 30-cent hard stop"
- "Give me a break-even stop button"
- "Build an equity-risk entry that sizes my position to 1% account risk"
- "What route should I use for a momentum scalp on a low-float name?"

