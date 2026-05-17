-- lua/sioyek-highlights/config.lua
local M = {}

M.options = {
  db_path = vim.fn.expand("~/.local/share/sioyek/shared.db"),
  format_function = function(text)
    local lines = vim.split(text, '\n', { plain = true })
    local formatted_lines = {}
    if #lines > 0 then
      lines[1] = '> *"' .. lines[1]
      lines[#lines] = lines[#lines] .. '"*'
      for i, line in ipairs(lines) do
        if i > 1 then
          table.insert(formatted_lines, '> ' .. line)
        else
          table.insert(formatted_lines, line)
        end
      end
    end
    return formatted_lines
  end,
  on_insert = function(start_line, end_line)
    vim.cmd('normal! ' .. start_line .. 'GV' .. end_line .. 'G')
    vim.cmd('normal! gq')
    vim.cmd("normal! ']")
    local pos = vim.api.nvim_win_get_cursor(0)
    local line = vim.api.nvim_buf_get_lines(0, pos[1] - 1, pos[1], false)[1]
    vim.api.nvim_win_set_cursor(0, { pos[1], #line })
    local ok, fn = pcall(require, 'footnote')
    if ok then
      fn.new_footnote()
      vim.cmd('normal! A ')
    end
  end,
}

function M.setup(options)
  if options then
    M.options = vim.tbl_deep_extend("force", M.options, options)
  end
end

return M
