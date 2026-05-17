local M = {}

function M.check()
	vim.health.start("nvim-sioyek-highlights")

	if vim.fn.executable("sqlite3") == 1 then
		vim.health.ok("sqlite3")
	else
		vim.health.error("sqlite3 not found (required for sioyek highlights)")
	end

	if vim.fn.executable("python3") == 1 then
		vim.health.ok("python3")
	else
		vim.health.error("python3 not found (required for jump_to_highlight)")
	end

	if vim.fn.executable("sioyek") == 1 then
		vim.health.ok("sioyek")
	else
		vim.health.warn("sioyek not in PATH (PDF viewer)")
	end

	if vim.fn.filereadable(vim.fn.expand("~/.local/share/sioyek/shared.db")) == 1 then
		vim.health.ok("~/.local/share/sioyek/shared.db")
	else
		vim.health.warn("sioyek shared.db not found – no highlights to query")
	end

	if pcall(require, "telescope") then
		vim.health.ok("telescope.nvim installed")
	else
		vim.health.error("telescope.nvim not installed (required dependency)")
	end
end

return M
