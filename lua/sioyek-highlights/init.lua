-- lua/sioyek-highlights/init.lua
local M = {}
local config = require("sioyek-highlights.config")

local function get_highlights()
  local db_path = config.options.db_path

  -- Check if the database file exists
  if vim.fn.filereadable(db_path) == 0 then
    vim.notify("Sioyek database not found at: " .. db_path, vim.log.levels.ERROR)
    return {}
  end
  
  -- Make sure the sqlite3 command-line tool is installed.
  if vim.fn.executable("sqlite3") == 0 then
    vim.notify("sqlite3 is not installed. Please install it.", vim.log.levels.ERROR)
    return {}
  end

  -- Query to get desc, text_annot, document name, and modification_time
  local cmd = string.format("sqlite3 -separator '|' '%s' \"SELECT h.desc, h.text_annot, h.document_path, COALESCE(ob.document_name, ''), h.modification_time FROM highlights h LEFT JOIN opened_books ob ON h.document_path = ob.path WHERE h.desc != '' OR h.text_annot != '' ORDER BY h.modification_time DESC;\"", db_path)
  local handle = io.popen(cmd)
  if not handle then return {} end

  local result = handle:read("*a")
  handle:close()

  local highlights = {}
  for line in result:gmatch("[^\r\n]+") do
    local parts = vim.split(line, "|", { plain = true })
    if #parts >= 4 then
      local desc = parts[1] and parts[1]:gsub("^%s+", ""):gsub("%s+$", "") or ""
      local text_annot = parts[2] and parts[2]:gsub("^%s+", ""):gsub("%s+$", "") or ""
      local document_hash = parts[3] and parts[3]:gsub("^%s+", ""):gsub("%s+$", "") or ""
      local document_name = parts[4] and parts[4]:gsub("^%s+", ""):gsub("%s+$", "") or ""
      local modification_time = parts[5] and parts[5]:gsub("^%s+", ""):gsub("%s+$", "") or ""
      
      -- Format timestamp (remove seconds)
      local formatted_time = ""
      if modification_time ~= "" then
        formatted_time = modification_time:match("(%d%d%d%d%-%d%d%-%d%d %d%d:%d%d)") or modification_time
      end
      
      -- Use document_name if available, otherwise fallback to hash
      local pdf_name = "Unknown PDF"
      if document_name ~= "" then
        pdf_name = vim.fn.fnamemodify(document_name, ":t")
      elseif document_hash ~= "" then
        pdf_name = document_hash:sub(1, 12) .. "..."
      end
      
      -- Only add if at least one field has content
      if desc ~= "" or text_annot ~= "" then
        table.insert(highlights, { 
          desc = desc, 
          text_annot = text_annot, 
          pdf_name = pdf_name,
          document_path = document_hash,
          timestamp = formatted_time
        })
      end
    end
  end
  return highlights
end

local function insert_highlight()
  local pickers = require("telescope.pickers")
  local finders = require("telescope.finders")
  local conf = require("telescope.config").values
  local actions = require("telescope.actions")
  local action_state = require("telescope.actions.state")
  
  local highlights = get_highlights()
  if #highlights == 0 then
    vim.notify("No Sioyek highlights found")
    return
  end

  pickers.new({}, {
    prompt_title = "Search",
    layout_strategy = "vertical",
    layout_config = {
      vertical = {
        prompt_position = "bottom",
        mirror = false,
        preview_height = 0.6,
        results_height = 6,
        width = 0.9,
        height = 0.9,
      },
    },
    default_selection_index = #highlights,
    finder = finders.new_table({
      results = highlights,
      entry_maker = function(entry)
        local display_text = ""
        if entry.desc ~= "" then
          display_text = entry.desc:gsub("\n", " "):gsub("%s+", " ")
        elseif entry.text_annot ~= "" then
          display_text = entry.text_annot:gsub("\n", " "):gsub("%s+", " ")
        end
        
        return {
          value = entry,
          display = display_text,
          ordinal = (entry.desc or "") .. " " .. (entry.text_annot or "") .. " " .. (entry.pdf_name or ""),
        }
      end,
    }),
    sorter = conf.generic_sorter({}),
    previewer = require("telescope.previewers").new_buffer_previewer({
      title = "Highlight Details",
      define_preview = function(self, entry, status)
        local lines = {}
        
        local function wrap_text(text, width)
          local wrapped_lines = {}
          for line in text:gmatch("[^\r\n]+") do
            if #line <= width then
              table.insert(wrapped_lines, line)
            else
              local current_line = ""
              for word in line:gmatch("%S+") do
                if #current_line + #word + 1 <= width then
                  current_line = current_line == "" and word or current_line .. " " .. word
                else
                  if current_line ~= "" then
                    table.insert(wrapped_lines, current_line)
                  end
                  current_line = word
                end
              end
              if current_line ~= "" then
                table.insert(wrapped_lines, current_line)
              end
            end
          end
          return wrapped_lines
        end
        
        local width = math.floor(vim.api.nvim_win_get_width(0) * 0.8) + 6
        width = math.max(width, 60) 
        
        if entry.value.pdf_name and entry.value.pdf_name ~= "" then
          table.insert(lines, "📄 PDF: " .. entry.value.pdf_name)
          if entry.value.timestamp ~= "" then
            table.insert(lines, "🕒 " .. entry.value.timestamp)
          end
          table.insert(lines, "")
        end
        
        if entry.value.desc and entry.value.desc ~= "" then
          table.insert(lines, "🔍 Highlight:")
          table.insert(lines, "")
          local wrapped_desc = wrap_text(entry.value.desc, width)
          for _, line in ipairs(wrapped_desc) do
            table.insert(lines, line)
          end
          table.insert(lines, "")
        end
        
        if entry.value.text_annot and entry.value.text_annot ~= "" then
          table.insert(lines, "📝 Annotation:")
          table.insert(lines, "")
          local wrapped_annot = wrap_text(entry.value.text_annot, width)
          for _, line in ipairs(wrapped_annot) do
            table.insert(lines, line)
          end
        end
        
        vim.api.nvim_buf_set_lines(self.state.bufnr, 0, -1, false, lines)
        vim.api.nvim_buf_set_option(self.state.bufnr, 'filetype', 'markdown')
      end
    }),
    attach_mappings = function(prompt_bufnr)
      actions.select_default:replace(function()
        actions.close(prompt_bufnr)
        local selection = action_state.get_selected_entry()
        if not selection then return end

        local original_text = ""
        if selection.value.desc and selection.value.desc ~= "" then
          original_text = selection.value.desc
        elseif selection.value.text_annot and selection.value.text_annot ~= "" then
          original_text = selection.value.text_annot
        else
          vim.notify("No content to insert", vim.log.levels.WARN)
          return
        end
        
        local formatted_lines = config.options.format_function(original_text)

        local cursor = vim.api.nvim_win_get_cursor(0)
        local row, col = cursor[1], cursor[2]

        vim.api.nvim_buf_set_text(0, row - 1, col, row - 1, col, formatted_lines)

        local start_line = row
        local end_line = row + #formatted_lines - 1

        -- Select the lines that were just inserted
        vim.cmd('normal! ' .. start_line .. 'GV' .. end_line .. 'G')
        -- Apply formatting
        vim.cmd('normal! gq')
        -- Go to the end of the changed text
        vim.cmd("normal! ']")
        -- Open a new line below and enter insert mode
        vim.cmd('normal! oS. ')
      end)
      return true
    end,
  }):find()
end

-- Das ist die wichtige Funktion für veröffentlichte Plugins
function M.setup(opts)
  config.setup(opts)
  
  -- Keymap und Command erstellen
  vim.keymap.set("n", "<leader>sh", insert_highlight, { desc = "Insert Sioyek Highlight" })
  vim.api.nvim_create_user_command("SioyekHighlights", insert_highlight, {})
end

return M
