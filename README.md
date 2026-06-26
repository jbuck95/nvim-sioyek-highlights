# nvim-sioyek-highlights

**DEMO**

![Image](https://github.com/user-attachments/assets/dde16808-9bfc-4b38-9465-c4f15f5c9959)


## Description

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


## Requirements

- [sioyek](https://sioyek.info/) — PDF viewer 
- [telescope.nvim](https://github.com/nvim-telescope/telescope.nvim)
- `sqlite3` — database CLI
- `python3` — for helper scripts
- Optional: `PyMuPDF` (`pip install PyMuPDF`) — for precise page coordinate calculation in jump feature. Falls back to basic PDF opening if not available.

Verify your setup with `:checkhealth sioyek-highlights`. See `:h sioyek-highlights` for detailed help.

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


## Lua API

```lua
local sh = require("sioyek-highlights")

-- Optional: override defaults
sh.setup({
  db_path = "~/.local/share/sioyek/shared.db",
  format_function = function(text) ... end,  -- format highlight before insert
  on_insert = function(start_line, end_line) ... end,  -- callback after insert
})

-- Jump from cursor line to PDF highlight
sh.jump_to_highlight()
```

## Configuration

| Option | Default | Description |
|--------|---------|-------------|
| `db_path` | `~/.local/share/sioyek/shared.db` | Path to Sioyek highlight database |
| `format_function` | wraps text as `> *"..."*` | Function to format inserted highlight |
| `on_insert` | gq + footnote integration | Callback after highlight insertion |

## Minimal Config for Issues

```lua
vim.cmd([[set rtp+=~/.local/share/nvim/lazy/nvim-sioyek-highlights]])
require("sioyek-highlights").setup()
```

## Credits

Integrates with [Sioyek](https://sioyek.info/) PDF reader and [Telescope](https://github.com/nvim-telescope/telescope.nvim).

## Todo

- [x] update formatting/ add format options.

## Disclaimer

Built for my personal master's thesis workflow.
AI was used extensively in development.

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
