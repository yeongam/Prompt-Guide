# mcp-builder

- Slug: `mcp-builder`
- Source: https://github.com/anthropics/skills/tree/main/skills/mcp-builder
- Source commit: `ref:main`
- Trigger: Guide for creating high-quality MCP (Model Context Protocol) servers that enable LLMs to interact with external services through well-designed tools. Use when building MCP servers to integrate external APIs or services, whether in Python (.

## Output

Compact, repeatable instructions for the task the skill covers.

## Token Policy

- Reference the upstream SKILL.md instead of copying its full body.
- Keep the local card to trigger + one-line output + policy notes.
- Load full skill content only when the skill actually fires.

## Compatibility

- Namespaced separately from Claude Code slash-command skills.
- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.

## Source Summary

# MCP Server Development Guide ## Overview Create MCP (Model Context Protocol) servers that enable LLMs to interact with external services through well-designed tools. The quality of an MCP server is measured by how well it enables LLMs to accomplish real-world tasks. --- # Process ## 🚀 High-Level Workflow Creating a high-quality MCP server involves four main phases: ### Phase 1: Deep Research and Planning #### 1.1.
