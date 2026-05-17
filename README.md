# nvim-sioyek-highlights

**DEMO**

![Image](https://github.com/user-attachments/assets/dde16808-9bfc-4b38-9465-c4f15f5c9959)


## README.md

A Neovim plugin to integrate Sioyek PDF reader highlights directly into your editor. 

1. Import Highlights directly under Cursor via TUI
2. Jump from Citation back to the PDF! 


## Features

**Import:** 
- fuzzy-search through your Sioyek highlight-database using Telescope
- Insert highlights as formatted quotes into your current buffer
- Support for both highlight descriptions and annotations

**Jump**
- if your Cursor is above a citation/highlight, press `leader s j` to
jump to the location of the highlight in the PDF. This uses running
Sioyek instance or opens a new if none is running. 
- searching for words only so you have no trouble formatting the
citation however you want 
- searching for words only so you have no trouble formatting the
citation however you want 


## Requirements

- Neovim >= 0.8
- [Telescope.nvim](https://github.com/nvim-telescope/telescope.nvim)
- `sqlite3` command-line tool
- [Sioyek PDF reader](https://sioyek.info/)

## Verify

`:checkhealth sioyek-highlights`

## Dependencies

- `sqlite3` — database CLI
- `python3` — for helper scripts
- [telescope.nvim](https://github.com/nvim-telescope/telescope.nvim)
- Optional: [sioyek](https://sioyek.info/) — PDF viewer

## Installation

### Using [lazy.nvim](https://github.com/folke/lazy.nvim)

```lua
{
  "jbuck95/nvim-sioyek-highlights",
  dependencies = { "nvim-telescope/telescope.nvim" },
  config = true,
}
```

### Using [packer.nvim](https://github.com/wbthomason/packer.nvim)

```lua
use {
  "jbuck95/nvim-sioyek-highlights",
  requires = { "nvim-telescope/telescope.nvim" },
  config = function()
    require("sioyek-highlights").setup()
  end
}
```

## Usage

- `<leader>sh` - Open Sioyek highlights picker
- `:SioyekHighlights` - Command to open the picker

- `<leader>sj` - Jump to highlight
- `:SioyekJump` 


## Configuration

The plugin works out of the box with default Sioyek database location (`~/.local/share/sioyek/shared.db`).

## Requirements

Make sure you have `sqlite3` installed:

**Arch Linux:**
```bash
sudo pacman -S sqlite
```

**Ubuntu/Debian:**
```bash
sudo apt install sqlite3
```

**macOS:**
```bash
brew install sqlite3
```

## Todo

- [ ] update formatting/ add format options. 

## LICENSE
```
MIT License

Copyright (c) 2025 Jan

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
```
