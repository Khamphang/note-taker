# Note Taker CLI

> ⚗️ **ໂປຣເຈັກນີ້ສ້າງຂຶ້ນໂດຍໃຊ້ລະບົບ TBW System 1**
> *(Think-Build-Watch System v1 — ປະກອບດ້ວຍ: ສະພາ Six Hats Council + Superpowers Pipeline + Council Review + Claude Office Visualizer + Hooks)*
>
> ທົດລອງໃຊ້ AI ພັດທະນາ software ແບບ end-to-end ຕັ້ງແຕ່ອອກແບບ → ຂຽນ code → ທົດສອບ → deploy ໂດຍ human ບໍ່ຕ້ອງຂຽນ code ດ້ວຍຕົນເອງ

---

## ກ່ຽວກັບໂປຣເຈັກ

CLI tool ສຳລັບ add, list, delete, search ໂນດ ບັນທຶກໄວ້ໃນ `~/.notes.json`
ມີລະບົບ encryption ໃຊ້ AES-256-GCM + PBKDF2 ສຳລັບລັອກໂນດດ້ວຍ password

## ຂະບວນການ AI ທີ່ໃຊ້

ໂປຣເຈັກນີ້ຜ່ານ pipeline ຂອງ AI agents 3 ຊັ້ນ:

1. **ສະພາ (Six Hats Council)** — AI ວິເຄາະ requirements ຈາກ 5 ມຸມມອງ (ຂໍ້ມູນ, ຄວາມສ່ຽງ, ຜົນດີ, ທາງເລືອກ, ຄວາມຮູ້ສຶກ) ແລ້ວສ້າງ design brief
2. **Superpowers Pipeline** — AI ແບ່ງງານ, ເຮັດ TDD (RED→GREEN→REFACTOR), ລັນ parallel agents ຂຽນ code
3. **Council Review** — AI ກວດ output ຄືນ ກ່ອນ approve

Human ເຮັດແຕ່: approve brief, ເບິ່ງຜົນ, ລາຍງານ bug

## Features

- `note add "ຂໍ້ຄວາມ"` — ເພີ່ມໂນດ
- `note list` — ລາຍການທັງໝົດ (ຮຮ `--json`)
- `note delete <id>` — ລົບດ້ວຍ ID
- `note search <keyword>` — ຄົ້ນຫາ (case-insensitive)
- `note lock` — ເຂົ້າລະຫັດດ້ວຍ password (AES-256-GCM)
- `note unlock` — ຖອດລະຫັດ

## ການຕິດຕັ້ງ

```bash
pip install cryptography
python notes.py add "hello"
python notes.py list
```

## Tests

```bash
python -m pytest test_notes.py test_crypto.py -v
```

20 tests — ຄອບຄຸມ add, delete, list, search, encryption, session key

## Stack

- Python 3.11+
- `cryptography` library (AES-256-GCM, PBKDF2-SHA256)
- `argparse`, `uuid`, `json` (stdlib only นอกจาก crypto)

---

*Built with [Claude Code](https://claude.ai/claude-code) — AI-driven TDD pipeline experiment*
