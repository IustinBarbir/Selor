# SELOR

Compliance case tracker — a desktop application for managing DR/SA cases with a MySQL backend.

![Python](https://img.shields.io/badge/Python-3.10+-blue) ![tkinter](https://img.shields.io/badge/GUI-tkinter-green) ![MySQL](https://img.shields.io/badge/DB-MySQL-orange)

## Features

- **Data Entry** — submit new cases with validation, auto-populated fields, and calendar date pickers
- **Data View** — search, filter, and browse cases with multiple filter criteria (status, marketplace, date ranges, certificate validity, etc.)
- **Excel Export** — export filtered results to `.xlsx` (full dataset, not limited to on-screen rows)
- **Copy to Clipboard** — right-click any row to copy it, double-click a cell to copy its value
- **Historical / Latest Certificate** — toggle between showing all records or only the most recent certificate per partner
- **Responsive** — scrollable layout that works on smaller screens (laptops)
- **Custom UI** — gradient header, card-based layout, alternating row colors, Segoe UI typography (all pure tkinter/ttk, no extra GUI libraries)

## Screenshots

![Data Entry]<img width="1919" height="1125" alt="image" src="https://github.com/user-attachments/assets/3d92a4b1-5a21-4553-a401-045405ad4184" />

![Data View]<img width="1919" height="1074" alt="image" src="https://github.com/user-attachments/assets/d5646ad1-6e67-4493-a008-5bd298b49723" />


## Setup

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # fill in your database credentials
python app.py
```

## Build the .exe (Windows)

```
build.bat
```

Produces a single `dist/SELOR.exe` using PyInstaller. The logo from `assets/logo.png` is bundled inside the executable and also converted to `.ico` for the window icon (requires [Pillow](https://pypi.org/project/Pillow/)).

## Database

Create the table using `schema.sql`, then configure the connection in `.env` (see `.env.example`).

## Project structure

| File | Purpose |
|---|---|
| `app.py` | GUI (tkinter) |
| `db.py` | MySQL queries: insert, search/filter, Excel export |
| `config.py` | Reads DB credentials from `.env` |
| `schema.sql` | Table creation script |
| `build.bat` | Builds SELOR.exe (Windows) |
| `SELOR_queries.sql` | Useful queries for MySQL Workbench (data corrections, deletions) |
| `.env.example` | Template for database credentials |

## License

MIT
