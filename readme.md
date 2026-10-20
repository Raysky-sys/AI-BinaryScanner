# Binary Scanner

A Windows desktop application that inspects files for known AI-generation
and content-provenance markers, and reports what it finds in a clear,
searchable log.

The scanner reads the raw bytes of each selected file, converts them to
lowercase, and looks for a curated list of anchor strings — C2PA and content
credential markers, vendor identifiers (Google, OpenAI, Microsoft, Adobe,
Meta), local AI tool names (Automatic1111, ComfyUI, Fooocus, InvokeAI, Kohya),
and tell-tale metadata fields such as `prompt:`, `negative prompt:`,
`steps:`, `sampler:`, `cfg scale:`, `seed:`, and `modelhash:`.

Everything runs locally. No file is uploaded anywhere.

---

## Table of Contents

- [Features](#features)
- [How it works](#how-it-works)
- [Marker categories](#marker-categories)
- [Important: markers are not proof](#important-markers-are-not-proof)
- [Requirements](#requirements)
- [Running from source](#running-from-source)
- [Building the standalone executable](#building-the-standalone-executable)
- [Project structure](#project-structure)
- [Using the application](#using-the-application)
- [The log output](#the-log-output)
- [Limitations](#limitations)
- [License](#license)
- [Contributing](#contributing)
- [Acknowledgements](#acknowledgements)

---

## Features

- **Select single or multiple files** via a standard multi-select file dialog.
- **Select folders**, with an option to include subfolders recursively. Add as
  many folders as you like — they are merged into one scan list.
- **Manage the scan list**: remove highlighted entries, or clear everything and
  start over.
- **Duplicate protection** — the same file cannot be added to the list twice.
- **Non-blocking scans** — work happens on a background thread, so the window
  stays responsive and shows a live progress bar.
- **Full in-GUI log** — per-file results, detected markers, errors, a summary
  count, and a list of every flagged file.
- **Colour-coded output** — matches in red, errors in amber, everything else in
  standard text.
- **Save the log** to a `.txt` file for archiving, sharing, or attaching to a
  report.
- **Duplicate paths are normalised**, so `C:\Images` and `c:\images\` are
  treated as the same target.
- **Standalone `.exe`** — no Python installation required on the machine that
  runs it.

---

## How it works

For every selected file the scanner:

1. Opens the file in binary mode (`rb`).
2. Reads its contents and lowercases the bytes.
3. Searches for each anchor from the list using a substring test.
4. Records every anchor that is present.
5. Writes a per-file result to the log.

A file is "flagged" when one or more anchors are found. At the end of the run
the log shows the total number of flagged files and lists their full paths.

The original single-file logic lives in `Binary_scanner.py` and is imported by
the GUI, so the detection rules and the interface stay separated.

---

## Marker categories

| Category | Examples |
| --- | --- |
| C2PA / technical markers | `c2pa`, `c2pa-ocsp`, `digitalsourcetype`, `trainedalgorithmicmedia`, `compositewithtrainedalgorithmicmedia`, `manifest`, `assertions`, `provenance`, `jumbf`, `cai`, `content credentials` |
| Google | `pki.goog`, `google c2pa`, `google core time stamping`, `goog/c2pa` |
| OpenAI / Microsoft | `openai`, `openai.com`, `dall-e`, `dall-e 3`, `microsoft.com`, `bing.com`, `microsoft-c2pa`, `designer` |
| Adobe | `adobe`, `firefly`, `adobe-c2pa` |
| Meta | `meta.com`, `imagine` |
| Local AI tools | `automatic1111`, `sd-webui`, `comfyui`, `workflow`, `fooocus`, `invokeai`, `kohya`, `stable diffusion` |
| Metadata fields | `prompt:`, `negative prompt:`, `steps:`, `sampler:`, `cfg scale:`, `seed:`, `modelhash:` |

---

## Important: markers are not proof

This tool produces **indicators, not verdicts.**

Markers such as `adobe`, `cai`, `manifest`, `c2pa`, and `workflow` routinely
appear in legitimate files:

- `cai` is an Adobe marker left behind when an image is edited in Photoshop.
- `c2pa` / `provenance` indicate content credentials, which are often
  *added* by cameras and editing software to authentic files.
- `workflow` and `manifest` are extremely common generic words.
- `seed`, `steps`, and `modelhash` can appear in unrelated technical files.

For higher-confidence conclusions, look for **combinations**: a vendor marker
plus generative metadata, for example `trainedalgorithmicmedia` together with
`prompt:` or `seed:`, or `c2pa` alongside `openai` / `google` / `adobe`.

The application repeats this caveat in the log after every scan.

---

## Requirements

**To run from source:**

- Python 3.10 or newer (Windows, macOS, or Linux)
- Tkinter — included with the standard Windows and macOS installers. On some
  Linux distributions install it separately:

  ```bash
  sudo apt install python3-tk

## Limitations
Marker matching is a heuristic. It finds known strings; it does not parse structured metadata, validate signatures, or confirm C2PA cryptographic claims.
Uncompressed formats matter. Markers embedded in EXIF, XMP, or PNG text chunks are visible to a raw byte scan. Metadata that is compressed or stored in a proprietary container may not be.
Whole files are loaded into memory during the scan. Very large video files will use significant RAM.
Read errors are reported, not retried. Locked files, permissions problems, and disconnected drives are shown in the log and counted in the summary.
Case-insensitive matching is intentional, but it can produce incidental matches inside binary data.


## Contributing

Contributions are welcome. A few things that help:

Adding markers — extend the ANCHORS list in Binary_scanner.py. Keep entries lowercase, since the file content is lowercased before matching.
Suggesting formats — if a specific file type needs dedicated handling (e.g. parsing EXIF properly instead of raw byte scanning), open an issue first so the approach can be agreed on.
Keeping the core separate — detection rules belong in Binary_scanner.py; interface work belongs in binary_scanner_gui.py.
Please run a scan on a test folder before submitting changes.

## Acknowledgements

Built on top of the publicly documented C2PA / Content Credentials marker strings and the metadata conventions used by Stable Diffusion front ends.


## `.gitignore`

```gitignore
# Byte-compiled / optimized files
__pycache__/
*.py[cod]
*$py.class

# PyInstaller
build/
dist/
*.manifest
*.spec

# Virtual environments
.venv/
venv/
env/

# Exported logs and test output
*.log
scan_results/

# Editor / OS noise
.vscode/
.idea/
Thumbs.db
.DS_Store



## License

MIT License

Copyright (c) 2025 <Raysky-sys>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
