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
}

function M.setup(options)
  if options then
    M.options = vim.tbl_deep_extend("force", M.options, options)
  end
end

return M
