# LinkedIn Post Generator

AI-powered tool to generate LinkedIn post drafts that match your personal writing style.

## Features

- **Style Learning**: Analyzes your previous posts to understand your unique writing style
- **Performance Analytics**: Learn what drives engagement from your past posts
- **AI-Optimized Generation**: Creates posts based on your high-performing content patterns
- **Manual Mode**: Generate posts by providing a topic and goal
- **Auto Mode**: Generate posts from stored topic contexts with broader themes
- **Context Management**: Track what angles you've covered to avoid repetition
- **LinkedIn Algorithm Aware**: Built-in optimization for LinkedIn's engagement algorithm

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Ensure Claude CLI is Available

This tool uses Claude CLI to generate posts. Make sure you have it installed:

```bash
# Test if Claude CLI is available
claude --version
```

If you're using a different command (like `codex`), update `config.yaml`:

```yaml
claude_cli_command: "codex"  # or whatever your command is
```

### 3. Add Your Example Posts

**Option A: Simple Text Files (Quick Start)**
1. Copy 10-30 of your previous LinkedIn posts into the `examples/` directory
2. Save them as `.txt` or `.md` files (one post per file)
3. See `examples/README.md` for more details

**Option B: With Engagement Data - Excel Export (Easiest!)**
1. Export posts from LinkedIn (View analytics → Export to Excel)
2. Add post content to each Excel file (simple copy-paste)
3. Save Excel files to `examples/` directory
4. Run: `python scripts/convert_excel_to_json.py`
5. See `EXCEL_WORKFLOW.md` for detailed guide

**Option C: With Engagement Data - Screenshots**
1. Go to your LinkedIn profile → View each post's analytics
2. Take screenshots of posts with their engagement metrics
3. Use ChatGPT to convert screenshots to JSON (see `prompts/chatgpt_conversion_prompt.md`)
4. Save JSON files to `examples/` directory
5. See `SCREENSHOT_WORKFLOW.md` for detailed guide

### 4. Analyze Your Style

Run the style analyzer to learn your writing patterns:

```bash
python scripts/analyze_style.py
```

This creates a style guide at `prompts/style_guide.txt` that will be used for all post generation.

### 5. Analyze Performance (Optional but Powerful)

If you added JSON posts with engagement data:

```bash
python scripts/analyze_performance.py
```

This analyzes what drives engagement in your posts:
- Best posting times and days
- Optimal post length
- What formats work best (lists, questions, images, etc.)
- Top performing topics and patterns

The generator will automatically use these insights!

## Usage

### Manual Mode - Generate Single Posts

Provide a specific topic and goal for a one-off post:

```bash
python scripts/generate.py \
  --manual \
  --topic "AI in healthcare" \
  --goal "educate my network about diagnostic AI"
```

### Auto Mode - Generate from Context

First, create a topic context:

```bash
# Create a new context
python scripts/manage_context.py create ai_healthcare

# Edit the generated contexts/ai_healthcare.yaml file to add:
# - themes and angles to explore
# - key messages
# - target audience
```

Then generate posts from that context:

```bash
python scripts/generate.py --context ai_healthcare
```

The system will automatically choose a fresh angle that hasn't been covered recently.

### Track What You've Posted

When you use a generated draft, update the context to track what angle you covered:

```bash
python scripts/generate.py \
  --context ai_healthcare \
  --update-context \
  --angle-summary "FDA approval process for diagnostic AI"
```

This prevents repetitive content in future posts.

## Context Management

```bash
# List all contexts
python scripts/manage_context.py list

# Show details of a context
python scripts/manage_context.py show ai_healthcare

# Delete a context
python scripts/manage_context.py delete old_topic
```

## Workflow Examples

### Getting Started (Quick)

1. Add your example posts to `examples/` (text files)
2. Run `python scripts/analyze_style.py`
3. Generate your first post:
   ```bash
   python scripts/generate.py --manual --topic "Test topic" --goal "test the system"
   ```

### Getting Started (With Performance Analytics - Excel Method)

1. **Export from LinkedIn:**
   - View analytics for each post → Export to Excel
   - Save Excel files to `examples/` directory
   - Repeat for 10-30 of your best posts

2. **Add post content:**
   - Open each Excel file
   - Add a row with `Content` label
   - Paste your full post text
   - (Optional) Add `Image` row if post had image

3. **Convert to JSON:**
   ```bash
   python scripts/convert_excel_to_json.py
   ```

4. **Analyze:**
   ```bash
   python scripts/analyze_style.py
   python scripts/analyze_performance.py
   ```

5. **Generate optimized posts:**
   ```bash
   python scripts/generate.py --manual --topic "Your topic" --goal "your goal"
   ```

   The system will automatically use your performance insights!

**See `EXCEL_WORKFLOW.md` for detailed step-by-step guide**

**Alternative:** Use screenshots instead (see `SCREENSHOT_WORKFLOW.md`)

### Regular Use - Manual Posts

When you have a specific idea:

```bash
python scripts/generate.py \
  --manual \
  --topic "Remote work productivity" \
  --goal "share my team's best practices"
```

### Regular Use - Auto Posts from Context

For ongoing topics you post about regularly:

```bash
# Set up context once
python scripts/manage_context.py create remote_work
# Edit contexts/remote_work.yaml with themes

# Generate posts whenever you need
python scripts/generate.py --context remote_work
```

## Directory Structure

```
linkedin-post-creator/
├── examples/           # Your example posts
│   ├── images/                     # Post images
│   ├── post_example.json           # Example JSON format
│   ├── PostAnalytics_*.xlsx        # LinkedIn Excel exports
│   ├── post_2025_09_30.json        # Converted JSON files
│   ├── all_posts.json              # Combined JSON array
│   └── README.md                   # Instructions
├── contexts/           # Topic contexts (.yaml files)
├── scripts/
│   ├── analyze_style.py        # Analyzes your writing style
│   ├── analyze_performance.py  # Analyzes engagement patterns
│   ├── convert_excel_to_json.py # Converts Excel to JSON
│   ├── generate.py             # Main post generator (AI-optimized)
│   └── manage_context.py       # Context management tool
├── output/             # Generated draft posts
├── prompts/
│   ├── style_guide.txt                 # Auto-generated style guide
│   └── chatgpt_conversion_prompt.md    # Prompt for converting screenshots
├── EXCEL_WORKFLOW.md       # Excel import guide
├── SCREENSHOT_WORKFLOW.md  # Screenshot import guide
├── config.yaml             # Configuration
└── requirements.txt        # Python dependencies
```

## Configuration

Edit `config.yaml` to customize:

- `claude_cli_command`: Command to run Claude CLI
- `target_audience`: Default audience for posts
- `tone_guidance`: Overall tone preferences
- `max_length`: Maximum post length in characters

## Tips

- **More examples = better style**: Provide 20-30 example posts for best results
- **JSON format unlocks analytics**: Use JSON posts with engagement data for AI-optimized generation
- **Update style periodically**: Re-run `analyze_style.py` as your writing evolves
- **Context hygiene**: Update contexts with `--update-context` to avoid repetitive posts
- **Edit before posting**: Drafts are starting points - always review and personalize
- **First hour matters**: LinkedIn's algorithm prioritizes early engagement - post when your audience is active
- **Screenshot workflow**: Take clear screenshots of your LinkedIn analytics for accurate data conversion

## Troubleshooting

**"Claude CLI command not found"**
- Make sure Claude CLI is installed and in your PATH
- Update `claude_cli_command` in `config.yaml` if using a different command

**"No example posts found"**
- Add `.txt` or `.md` files to the `examples/` directory
- Make sure files contain actual post content

**"Style guide not found"**
- Run `python scripts/analyze_style.py` first to create the style guide

## License

MIT
