# Design

Living document of decisions made so far. "Open" items are explicitly undecided.

## Architecture

1. **Reference builds.** Each of MM1–6 is statically recompiled with NESRecomp. These
   builds are the ground truth for behavior; they are not what ships.
2. **Native engine.** A data-driven Mega Man engine, written natively, with no NES
   hardware limits. Validated by running identical inputs through the reference build
   and the engine and comparing player/object position and timing.
3. **Content import.** Stages, enemies, bosses, weapons and music are extracted from
   the player's own ROMs at first launch (see `roms.md`). Logic for bosses/weapons is
   rewritten natively, using each recomp's generated C as the reference.
4. **Order of work.** Mega Man 2 first (reference build → engine core → one stage and
   boss → full game), then the remaining games one at a time. The randomizer ships once
   a few games are ported; the pool grows as more are added.
5. The MM3 NESRecomp project is a reference only, consulted when stuck (check its
   license before reusing any code).

### Per-game behavior profiles

Physics constants, collision rules, abilities and boss timing are loaded per game.
The engine grows forward from MM2: slide (MM3+) and charge shot (MM4+) are abilities
enabled by profile. A run setup option can force one movement profile everywhere
(e.g. MM6 movement), stored in the seed.

## Runs

- **Pool:** 8 stages + Robot Masters drawn from all six games (46 total: MM1 has 6,
  MM2–6 have 8 each).
- **Fortress:** one of the six endgame sets, chosen per round.
- **Rewards:** defeating a boss gives the same weapon it gives in its own game. Items
  stay tied to the stage that originally awards them.
- **Lucky easy runs are fine.** No difficulty balancing of pools.

### Seed generation

1. Pick the fortress set (it has its own requirements).
2. Draw 8 stages.
3. Simulate from the starting kit: every item a stage or the fortress needs must be
   awarded by a stage in the same pool, reachable in some order. Otherwise reroll.
4. Encode a shareable code: **version + RNG seed + settings flags.** The version means
   old seeds don't silently change after rebalancing.

### Rounds (marathon)

- After clearing 8 bosses + fortress, a new round of 8 + fortress is offered.
- Round pool = f(base seed, round number), so one code reproduces the whole marathon.
- Cleared stages/fortresses are excluded until exhausted. 46 stages / 6 fortresses ≈
  six rounds covers nearly everything (48 slots: last round has 6, or 2 repeats — open).
- Loadout, round number and cleared list are saved between rounds.

### Inventory

- **Weapons:** max 8 slots. Picking up a 9th opens a swap screen (keep new / drop one).
- **Items:** separate inventory, never count toward the 8, cannot be dropped.
- Only weapons tagged with a **progression use** (e.g. a boss that only takes damage
  from one weapon, a weapon with a stage-traversal use) can cause a softlock if dropped.

### Run setup options (all stored in seed flags)

| Option | Values |
|---|---|
| Dropped required weapon | **Bring it back** (reappears; default spot: start of the stage that needs it) / **Let it happen** (player may solve it with glitches/techniques) |
| Difficulty (MM2) | Normal / Difficult |
| Faithful quirks | On / Off (may later split by weapon / stage / boss) |
| Movement profile | Per-game / force one profile |

"Let it happen" should still offer an **abandon round / reroll stage** escape in the
pause menu so a stuck run can end cleanly.

## Weapons & damage

- Boss weakness matchups are deferred: all weapons start at default damage values and
  get tuned later.
- Weapon-locked fights (e.g. MM2 Boobeam Trap / Crash Bomber) — open: require the
  weapon in pool, or fall back to default damage.

## Quirks

Glitches and techniques are kept as data-driven **quirk flags** at three scopes:

- **Weapon quirks** travel with the weapon. Example: MM1 pause trick — pausing while
  Thunder Beam overlaps a boss clears the boss's hit invincibility, so it hits again.
  Works against any boss from any game.
- **Stage quirks** apply only inside the stage (collision quirks, zips).
- **Boss quirks** follow the boss's AI/hitbox behavior.

Source list: each game's speedrun / TAS notes, tagged by scope.

## Data tables to build

- **Requirements table:** what each stage and fortress needs (items, weapons) and what
  each stage awards. Feeds the seed solver.
- **Quirk list:** per weapon / stage / boss.
- **Progression-use tags** on weapons.

## Open questions

- Starting kit contents.
- Last-round handling (6 stages vs. repeats).
- Weapon-locked fortress fights.
- Optional "authentic" presentation mode (flicker, slowdown, 256×240) vs modern-only.
