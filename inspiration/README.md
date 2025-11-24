# Inspiration Folder

Drop quick ideas, observations, and raw thoughts here. The post generator will randomly pick 2-3 of these to inspire your posts.

## How to Use

### Quick Notes (Best Format)
Create simple text files with your raw ideas:

**Example: `idea_001.txt`**
```
Claude Code just auto-fixed a bug I introduced 10 commits ago.
It remembered the context from the original PR review.
This is getting scary good.
```

**Example: `observation_cursor_vs_codex.txt`**
```
Noticed Cursor is faster for quick edits but Claude Code is better
for complex refactoring. Need to write about when to use which.
```

**Example: `matchops_feature_idea.txt`**
```
What if MatchOps could detect when you're about to make the same
mistake twice? Like a "you tried this pattern before and it failed" alert.
```

## File Formats Supported

- **`.txt`** - Plain text notes (easiest!)
- **`.md`** - Markdown notes
- **Any text file** - Will be read and used for inspiration

## What to Put Here

### ✅ Good Inspiration Content:

- **Quick observations**: "Noticed that..."
- **Aha moments**: "Just realized..."
- **Frustrations**: "Why does X always..."
- **Questions**: "What if we could..."
- **Feature ideas**: "MatchOps should..."
- **Comparisons**: "X vs Y - X wins because..."
- **Debugging stories**: "Spent 3 hours on..."
- **User feedback**: "Someone said..."
- **Industry trends**: "Saw article about..."
- **Personal reflections**: "Changed my mind about..."

### ❌ Not Needed Here:

- Full post drafts (those go in `output/`)
- Complete posts (those are in `examples/`)
- Context definitions (those are in `contexts/`)

## How the Generator Uses This

When you run:
```bash
python scripts/generate.py --context matchops_local
```

The generator will:
1. Pick 2-3 random inspiration files
2. Read them as context
3. Use them to spark ideas for the post
4. Combine with your style guide + context themes
5. Generate a post that might incorporate those inspirations

**The inspiration is subtle** - it's not copy-pasted, but used as creative fuel.

## Organization Tips

### By Date
```
inspiration/
├── 2025_11_24_bug_fix_idea.txt
├── 2025_11_23_cursor_observation.txt
└── 2025_11_22_user_feedback.txt
```

### By Topic
```
inspiration/
├── matchops_features/
│   ├── idea_001.txt
│   └── idea_002.txt
├── vibe_coding/
│   ├── observation_001.txt
│   └── observation_002.txt
└── ai_tools_comparison/
    └── cursor_vs_claude.txt
```

### Numbered
```
inspiration/
├── idea_001.txt
├── idea_002.txt
├── idea_003.txt
└── ...
```

**Any format works!** The generator scans all text files.

## Example Workflow

### Your Daily Routine:
1. **Morning coffee**: Notice something while coding
2. **Quick capture**:
   ```bash
   echo "Claude suggested a pattern I never thought of -
   using composition instead of inheritance for the
   plugin system. Mind blown." > inspiration/idea_$(date +%Y%m%d).txt
   ```
3. **Generate post later**:
   ```bash
   python scripts/generate.py --context matchops_local
   ```
4. **System picks 2-3 ideas** from your inspiration folder
5. **Post incorporates** the inspiration naturally

## Managing Old Ideas

### Archive Used Ideas
Once an idea is incorporated into a post, you can:

```bash
mkdir inspiration/archive
mv inspiration/idea_001.txt inspiration/archive/
```

Or just leave them - more inspiration = more variety!

### Clean Up Periodically
```bash
# Move old ideas to archive
mv inspiration/*_2025_10_*.txt inspiration/archive/
```

## Tips

- **Write raw, unfiltered** - no need to be polished
- **Capture quickly** - don't overthink it
- **Date or number files** - helps you track
- **One idea per file** - easier to mix and match
- **Keep it brief** - 1-3 sentences is perfect
- **No pressure** - not every idea gets used, that's fine!

---

**This folder is your creative dump.** Brain farts, shower thoughts, 3am insights - all welcome! 🧠✨
