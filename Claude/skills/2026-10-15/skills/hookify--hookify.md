---
description: Create hooks to prevent unwanted behaviors from conversation analysis or explicit instructions
argument-hint: Optional specific behavior to address
allowed-tools: ["Read", "Write", "AskUserQuestion", "Task", "Grep", "TodoWrite", "Skill"]
---
# Hookify - Create Hooks from Unwanted Behaviors

**FIRST: Load the hookify:writing-rules skill** using the Skill tool to understand rule file format and syntax.

Create hook rules to prevent problematic behaviors by analyzing the conversation or from explicit user instructions.

## Your Task

You will help the user create hookify rules to prevent unwanted behaviors. Follow these steps:

### Step 1: Gather Behavior Information

**If $ARGUMENTS is provided:**
- User has given specific instructions: `$ARGUMENTS`
- Still analyze recent conversation (last 10-15 user messages) for additional context
- Look for examples of the behavior happening

**If $ARGUMENTS is empty:**
- Launch the conversation-analyzer agent to find problematic behaviors
- Agent will scan user prompts for frustration signals
- Agent will return structured findings

**To analyze conversation:**
Use the Task tool to launch conversation-analyzer agent:

### Step 2: Present Findings to User

After gathering behaviors (from arguments or agent), present to user using AskUserQuestion:

**Question 1: Which behaviors to hookify?**
- Header: "Create Rules"
- multiSelect: true
- Options: List each detected behavior (max 4)
  - Label: Short description (e.g., "Block rm -rf")
  - Description: Why it's problematic

**Question 2: For each selected behavior, ask about action:**
- "Should this block the operation or just warn?"
- Options:
  - "Just warn" (action: warn - shows message but allows)
  - "Block operation" (action: block - prevents execution)

**Question 3: Ask for example patterns:**
- "What patterns should trigger this rule?"
- Show detected patterns
- Allow user to refine or add more

### Step 3: Generate Rule Files

For each confirmed behavior, create a `.claude/hookify.{rule-name}.local.md` file:

**Rule naming convention:**
- Use kebab-case
- Be descriptive: `block-dangerous-rm`, `warn-console-log`, `require-tests-before-stop`
- Start with action verb: block, warn, prevent, require

**File format:**
```markdown
---
name: {rule-name}
enabled: true
event: {bash|file|stop|prompt|all}
pattern: {regex pattern}
action: {warn|block}
---

{Message to show Claude when rule triggers}
```

**Action values:**
- `warn`: Show message but allow operation (default)
- `block`: Prevent operation or stop session

**For more complex rules (multiple conditions):**

### Step 4: Create Files and Confirm

**IMPORTANT**: Rule files must be created in the current working directory's `.claude/` folder, NOT the plugin directory.

Use the current working directory (where Claude Code was started) as the base path.

1. Check if `.claude/` directory exists in current working directory
   - If not, create it first with: `mkdir -p .claude`

2. Use Write tool to create each `.claude/hookify.{name}.local.md` file
   - Use relative path from current working directory: `.claude/hookify.{name}.local.md`
   - The path should resolve to the project's .claude directory, not the plugin's

3. Show user what was created:
   ```
   Created 3 hookify rules:
   - .claude/hookify.dangerous-rm.local.md
   - .claude/hookify.console-log.local.md
   - .claude/hookify.sensitive-files.local.md

   These rules will trigger on:
   - dangerous-rm: Bash commands matching "rm -rf"
   - console-log: Edits adding console.log statements
   - sensitive-files: Edits to .env or credentials files
   ```

4. Verify files were created in the correct location by listing them

5. Inform user: **"Rules are active immediately - no restart needed!"**

   The hookify hooks are already loaded and will read your new rules on the next tool use.

## Event Types Reference

- **bash**: Matches Bash tool commands
- **file**: Matches Edit, Write, MultiEdit tools
- **stop**: Matches when agent wants to stop (use for completion checks)
- **prompt**: Matches when user submits prompts
- **all**: Matches all events

## Pattern Writing Tips

**Bash patterns:**
- Match dangerous commands: `rm\s+-rf|chmod\s+777|dd\s+if=`
- Match specific tools: `npm\s+install\s+|pip\s+install`

**File patterns:**
- Match code patterns: `console\.log\(|eval\(|innerHTML\s*=`
- Match file paths: `\.env$|\.git/|node_modules/`

**Stop patterns:**
- Check for missing steps: (check transcript or completion criteria)

## Important Notes

- **No restart needed**: Rules take effect immediately on the next tool use
- **File location**: Create files in project's `.claude/` directory (current working directory), NOT the plugin's .claude/
- **Regex syntax**: Use Python regex syntax (raw strings, no need to escape in YAML)
- **Action types**: Rules can `warn` (default) or `block` operations
- **Testing**: Test rules immediately after creating them
