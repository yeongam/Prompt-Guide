# Anthropic TypeScript SDK

- Slug: `anthropic-typescript-sdk`
- Source: https://github.com/anthropics/anthropic-sdk-typescript
- Source commit: `unknown`
- Trigger: Use for implementing Claude API features in TypeScript or JavaScript.

## Procedure

1. Install @anthropic-ai/sdk and import Anthropic.
2. Instantiate with new Anthropic({ apiKey: process.env.ANTHROPIC_API_KEY }).
3. Use client.messages.create for calls; client.messages.stream for streaming.
4. Pass tools array with name, description, and input_schema.
5. Model IDs: claude-sonnet-4-6, claude-opus-4-7, claude-haiku-4-5.

## Output

Compact TypeScript snippet aligned with current @anthropic-ai/sdk version.

## Token Policy

- Avoid repeated background context.
- Return only decision-critical code or instructions.
- Link to source repo instead of copying long docs.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.

## Source Summary

# Claude SDK for TypeScript [![NPM version](https://img.shields.io/npm/v/@anthropic-
ai/sdk.svg)](https://npmjs.org/package/@anthropic-ai/sdk) The Claude SDK for TypeScript
provides access to the [Claude API](https://docs.anthropic.com/en/api/) from server-side
TypeScript or JavaScript applications. ## Documentation Full documentation is available
at **[platform.claude.com/docs/en/api/sdks/typescript](https://platfor.
