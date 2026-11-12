# Mega Man Roulette

A randomized merge of Mega Man 1–6 (NES). Every run draws a pool of 8 stages and
Robot Masters from all six games, plus one of the six fortress sets. Beat a boss to
earn its weapon; keep going for another round of 8 with your loadout carried over.

> **Status:** planning / bootstrapping. Nothing playable yet.

## Approach

- **Native engine, recomps as references.** Each game is statically recompiled with
  [NESRecomp](https://github.com/mstan/nesrecomp) to produce a faithful *reference
  build*. A native, data-driven Mega Man engine is then written and validated
  against those references (same inputs → same positions/timing). The engine is free
  of NES limits (object slots, sprite flicker, menu size, resolution).
- **Mega Man 2 first.** MM2 (US / Legacy Collection) is the first reference and the
  first game ported into the native engine. Other games follow one at a time.

See [docs/design.md](docs/design.md) for the full design and
[docs/roms.md](docs/roms.md) for the exact ROMs expected.

## You supply the ROMs

This repository contains **no Capcom code or data**. Builds are produced from your own
legally obtained ROMs, verified by checksum on import. Do not commit ROMs, archives,
or generated code; `.gitignore` blocks them.

## Repository layout

| Path | Contents |
|---|---|
| `nesrecomp/` | NESRecomp framework (git submodule) |
| `docs/` | Design notes, ROM list, requirement & quirk tables (as they're built) |

Clone with submodules:

```
git clone --recurse-submodules https://github.com/Hatdagger/MegaManRoulette
```

## License note

NESRecomp is under the PolyForm Noncommercial 1.0.0 license, so builds that include
it must stay noncommercial. This project's own license is not yet chosen.
