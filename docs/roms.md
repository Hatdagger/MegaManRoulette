# Expected ROMs

Source: *Mega Man Legacy Collection* NES dumps (No-Intro naming). Checksums are of
the ROM **without** the 16-byte iNES header. The launcher should verify these on import.

| Game | No-Intro name | Mapper | PRG | CHR | CRC32 | SHA-1 |
|---|---|---|---|---|---|---|
| MM1 | Mega Man (World) (Mega Man Legacy Collection) (Unl) | UxROM (2) | 128 KB | CHR-RAM | `1C47D202` | `63e8a6e3a443bc7fc27e939ff59c7b160046392e` |
| MM2 | Mega Man 2 (World) (Mega Man Legacy Collection) | MMC1 (1) | 256 KB | CHR-RAM | `CF5DE2BC` | `5d11fe03bdcee860d3e161c6a0af4a7a3bbb9834` |
| MM3 | Mega Man 3 (World) (Mega Man Legacy Collection) (Unl) | MMC3 (4) | 256 KB | 128 KB CHR-ROM | `599629D5` | `63e309f23efbf4ae7b084678bade1fa4d45ddc9c` |
| MM4 | Mega Man 4 (World) (Mega Man Legacy Collection) (Unl) | MMC3 (4) | 512 KB | CHR-RAM | `0FAA8F73` | `acd38aebcc130e3011c24834763e76d7c752820d` |
| MM5 | Mega Man 5 (World) (Mega Man Legacy Collection) (Unl) | MMC3 (4) | 256 KB | 256 KB CHR-ROM | `68B85928` | `967c2beaf4bf69f8eb31cb82c741e254e0642f48` |
| MM6 | Mega Man 6 (World) (Mega Man Legacy Collection) (Unl) | MMC3 (4) | 512 KB | CHR-RAM | `DCC74EF2` | `cc3f955cfc1275e374bf6141f65f02e589b33c9c` |

Notes:
- All six carry NES 2.0 headers.
- The MM2 dump is US-based: title-screen text includes NORMAL / DIFFICULT and
  "MEGA MAN" naming.
- These are the Legacy Collection releases, which No-Intro lists separately from the
  original carts. Other projects (e.g. the MM3 NESRecomp port) may expect cart dumps.
