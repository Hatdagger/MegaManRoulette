# Mega Man 2 reference build

Static recompilation of Mega Man 2 (Legacy Collection, CRC32 `CF5DE2BC`, see
[../../docs/roms.md](../../docs/roms.md)) on NESRecomp's cycle backend. This is the
**reference** the native engine is validated against, not the shipping game.

## Status

- Boots through the intro, title, NORMAL/DIFFICULT select and stage select.
- Air Man's stage loads and is playable through its first section.
- With `seeds.txt`, the scripted route runs **100% native** (0% interpreted).
- Native and `--interp-only` runs produce **identical per-frame hashes** for all 2,700
  frames of `route_first_stage.txt`.
- Not yet done: comparison against the independent emulator oracle, the SDL
  window/launcher, longer routes (full stages, bosses, Wily stages).

## Files

| File | Purpose |
|---|---|
| `game.toml` | Recompiler config |
| `seeds.txt` | Code entry points found by `--miss-log`; build input |
| `route_stage_select.txt` | Input route: boot → stage select |
| `route_first_stage.txt` | Input route: boot → Air Man stage, walk and jump right |

## Build (Linux, headless)

```sh
# from the repo root, with your ROM outside the repo
cmake -S nesrecomp/recompiler -B build/recompiler -G Ninja -DCMAKE_BUILD_TYPE=Release
cmake --build build/recompiler

cmake -S nesrecomp/runner/cyc/project -B build/mm2 -G Ninja -DCMAKE_BUILD_TYPE=Release \
  -DNESRECOMP_ROM=/path/to/mm2.nes \
  -DNESRECOMP_GAME_CONFIG=$PWD/recomp/mm2/game.toml \
  -DNESRECOMP_HEADLESS=ON
cmake --build build/mm2
```

Windows: same steps with `-G 'Visual Studio 17 2022' -A x64`
(see `nesrecomp/docs/GETTING_STARTED.md`).

## Run and verify

```sh
# screenshot every 300 frames along the route
build/mm2/nes_game /path/to/mm2.nes --frames 2700 \
  --input recomp/mm2/route_first_stage.txt --shot-every 300 --screenshot shots/r.png

# native vs interpreter: hashes must match line for line
build/mm2/nes_game /path/to/mm2.nes --frames 2700 \
  --input recomp/mm2/route_first_stage.txt --hash-out native.hash
build/mm2/nes_game /path/to/mm2.nes --frames 2700 \
  --input recomp/mm2/route_first_stage.txt --interp-only --hash-out interp.hash
cmp native.hash interp.hash
```

## Extending coverage

New routes reach new code. Record it and rebuild:

```sh
build/mm2/nes_game /path/to/mm2.nes --frames N --input NEW_ROUTE.txt \
  --miss-log recomp/mm2/seeds.txt
```

`--miss-log` merges into the existing file. Never edit generated code; fix inputs
or the framework instead.
