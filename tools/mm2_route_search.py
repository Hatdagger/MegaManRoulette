#!/usr/bin/env python3
"""Greedy route search for the MM2 reference build.

Builds a cheat-free --input route by trying short input chunks from a save
state, scoring the result from RAM, and committing the best chunk. The output
route is a plain NESRecomp input file, so it can be replayed against the
recompiled build, --interp-only and the TriCNES oracle.

RAM (MM2, verified against this ROM):
  $002A stage   $00A8 lives   $0440/$0460 player X screen/pixel
  $04A0 player Y   $06C0 player HP   $06C1 boss HP

Usage:
  mm2_route_search.py --exe build/mm2/nes_game --rom mm2.nes \
      --prefix recomp/mm2/route_first_stage.txt --start 1900 \
      --until 9000 --out route.txt --work /tmp/search
"""
import argparse, os, random, subprocess, sys
from concurrent.futures import ThreadPoolExecutor

CHUNK = 24       # frames committed per step
LOOK = 48        # extra idle frames simulated to catch delayed deaths


def read_ram(path):
    m = {}
    with open(path) as f:
        for line in f:
            if line.startswith('ram '):
                a, rest = line[4:].split(':', 1)
                a = int(a, 16)
                for i, b in enumerate(rest.split()):
                    m[a + i] = int(b, 16)
    return m


def candidates(rng):
    """Each candidate: list of (offset, buttons) within CHUNK frames."""
    c = [[(0, 'RIGHT')], [(0, '-')], [(0, 'LEFT')]]
    for h in (4, 10, 18, CHUNK):
        c.append([(0, 'RIGHT+A'), (h, 'RIGHT')])
        c.append([(0, 'A'), (h, '-')])
        c.append([(0, 'LEFT+A'), (h, 'LEFT')])
    # shooting: tap B while walking or standing
    for d in ('RIGHT', '-', 'LEFT'):
        steps = []
        for t in range(0, CHUNK, 8):
            steps += [(t, (d + '+B') if d != '-' else 'B'), (t + 4, d)]
        c.append(steps)
    # jump + shoot
    c.append([(0, 'RIGHT+A'), (6, 'RIGHT+A+B'), (10, 'RIGHT+A'), (16, 'RIGHT')])
    c.append([(0, 'A'), (6, 'A+B'), (10, 'A'), (16, '-')])
    rng.shuffle(c)
    return c


class Search:
    def __init__(self, a):
        self.a = a
        os.makedirs(a.work, exist_ok=True)
        self.route = []          # absolute (frame, buttons)
        self.n = 0

    def run(self, state, start, steps, frames, mem_frame, mem_out, save=None):
        inp = os.path.join(self.a.work, f'in{self.n}_{os.getpid()}_{id(steps)}.txt')
        self.n += 1
        with open(inp, 'w') as f:
            for fr, b in steps:
                f.write(f'{fr} {b}\n')
        cmd = [self.a.exe, self.a.rom, '--frames', str(frames), '--input', inp,
               '--mem-frame', str(mem_frame), '--mem-out', mem_out]
        if state:
            cmd += ['--load-state', state]
        if save:
            cmd += ['--save-state', f'{save[0]}:{save[1]}']
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        os.remove(inp)
        return read_ram(mem_out)

    @staticmethod
    def score(m, base):
        x = m[0x440] * 256 + m[0x460]
        s = x
        if m[0xA8] < base[0xA8] or m[0x6C0] == 0 or (m[0x4A0] >= 0xE0 and m[0x4A0] < 0xF8):
            s -= 100000
        s -= (base[0x6C0] - m[0x6C0]) * 40
        if m[0x6C1] and base[0x6C1]:
            s += (base[0x6C1] - m[0x6C1]) * 600
        if m[0x2A] != base[0x2A]:
            s += 1000000
        return s

    def main(self):
        a = self.a
        rng = random.Random(a.seed)
        # prefix route up to --start, and the starting state
        with open(a.prefix) as f:
            for line in f:
                p = line.split()
                if p and int(p[0]) < a.start:
                    self.route.append((int(p[0]), p[1] if len(p) > 1 else '-'))
        state = os.path.join(a.work, 'cur.state')
        base = self.run(None, 0, self.route, a.start, a.start - 1,
                        os.path.join(a.work, 'base.txt'), save=(a.start - 1, state))
        f0 = a.start
        # history of committed steps for backtracking: (frame, state file, route length)
        hist = [(f0, state, len(self.route))]
        best_x, since_best, explore = -1, 0, 0
        while f0 < a.until:
            cands = candidates(rng)
            cur = hist[-1][1]

            def sim(i):
                steps = [(f0 + o, b) for o, b in cands[i]]
                end = f0 + CHUNK + LOOK
                # after the chunk, stand still: a chunk only scores well if
                # Mega Man is somewhere safe when it ends
                steps.append((f0 + CHUNK, '-'))
                m = self.run(cur, f0, steps, end, end - 1,
                             os.path.join(a.work, f'm{i}.txt'))
                return self.score(m, base), i

            with ThreadPoolExecutor(a.jobs) as ex:
                scored = sorted(ex.map(sim, range(len(cands))), reverse=True)
            if explore:
                safe = [c for c in scored if c[0] > -50000] or scored
                pick = rng.choice(safe)
                explore -= 1
            else:
                pick = scored[0]
            steps = [(f0 + o, b) for o, b in cands[pick[1]]]
            nstate = os.path.join(a.work, f'st{f0 + CHUNK}.state')
            m = self.run(cur, f0, steps, f0 + CHUNK, f0 + CHUNK - 1,
                         os.path.join(a.work, 'commit.txt'), save=(f0 + CHUNK - 1, nstate))
            del self.route[hist[-1][2]:]
            self.route += steps
            f0 += CHUNK
            hist.append((f0, nstate, len(self.route)))
            x = m[0x440] * 256 + m[0x460] + (0 if not m[0x6C1] else 4000 + (28 - m[0x6C1]) * 50)
            print(f'f={f0} stage={m[0x2A]} x={m[0x440]}:{m[0x460]} y={m[0x4A0]} '
                  f'hp={m[0x6C0]} boss={m[0x6C1]} lives={m[0xA8]} score={pick[0]}'
                  f'{" explore" if explore else ""}', flush=True)
            if m[0x2A] != base[0x2A]:
                break
            dead = m[0xA8] < base[0xA8] or m[0x6C0] == 0
            if x > best_x and not dead:
                best_x, since_best = x, 0
            else:
                since_best += 1
            if dead or since_best >= a.stall:
                back = min(len(hist) - 1, a.backtrack + rng.randrange(a.backtrack))
                del hist[len(hist) - back:]
                f0 = hist[-1][0]
                del self.route[hist[-1][2]:]
                explore, since_best = 3, 0
                print(f'  backtrack {back} steps to f={f0}', flush=True)
            with open(a.out, 'w') as f:
                for fr, b in self.route:
                    f.write(f'{fr} {b}\n')
        with open(a.out, 'w') as f:
            for fr, b in self.route:
                f.write(f'{fr} {b}\n')


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--exe', required=True)
    p.add_argument('--rom', required=True)
    p.add_argument('--prefix', required=True)
    p.add_argument('--start', type=int, required=True)
    p.add_argument('--until', type=int, default=9000)
    p.add_argument('--out', required=True)
    p.add_argument('--work', default='/tmp/mm2search')
    p.add_argument('--jobs', type=int, default=2)
    p.add_argument('--seed', type=int, default=1)
    p.add_argument('--stall', type=int, default=8)
    p.add_argument('--backtrack', type=int, default=4)
    Search(p.parse_args()).main()
