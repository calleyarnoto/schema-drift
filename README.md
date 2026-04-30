# schema-drift

> Compare database schemas across environments and generate human-readable diff reports.

---

## Installation

```bash
pip install schema-drift
```

Or install from source:

```bash
git clone https://github.com/yourname/schema-drift.git && cd schema-drift && pip install .
```

---

## Usage

Point `schema-drift` at two database URLs and it will output a diff report:

```bash
schema-drift compare \
  --source postgresql://user:pass@localhost/mydb_dev \
  --target postgresql://user:pass@prod-host/mydb_prod \
  --output report.md
```

**Example output:**

```
[+] Table added:        audit_logs
[-] Table removed:      legacy_sessions
[~] Table modified:     users
      [+] Column added:   last_login_at (TIMESTAMP)
      [~] Column changed: email  varchar(100) → varchar(255)
```

You can also export reports as JSON:

```bash
schema-drift compare --source <url> --target <url> --format json
```

For a full list of options:

```bash
schema-drift --help
```

---

## Supported Databases

- PostgreSQL
- MySQL / MariaDB
- SQLite

---

## Contributing

Pull requests are welcome. Please open an issue first to discuss any significant changes.

---

## License

[MIT](LICENSE)