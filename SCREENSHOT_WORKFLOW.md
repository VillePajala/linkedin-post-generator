# Screenshot to JSON Workflow

This guide shows you how to convert your LinkedIn post analytics into JSON format using ChatGPT.

## Why This Approach?

- **No LinkedIn API needed** (which is nearly impossible to access for personal profiles)
- **No Creator Mode required** (which can hurt engagement)
- **Gets all the data you need** for performance optimization
- **Simple and effective** workflow

## Step-by-Step Process

### 1. Capture LinkedIn Analytics

For each post you want to analyze:

1. Go to your LinkedIn profile
2. Find the post
3. Click to view post analytics
4. Take screenshots that capture:
   - **Post content** (the full text)
   - **Engagement metrics**: Impressions, reactions, comments, shares, clicks
   - **Date and time** the post was published
   - **Post format**: Images, videos, links if any

**Pro tip**: Take 2-3 screenshots per post if needed to capture all data clearly.

### 2. Prepare ChatGPT Prompt

Open `prompts/chatgpt_conversion_prompt.md` and copy the conversion prompt.

The prompt tells ChatGPT to:
- Extract all visible data from screenshots
- Format it as JSON matching our schema
- Calculate engagement rate
- Analyze post characteristics (hashtags, questions, lists, etc.)

### 3. Convert with ChatGPT

1. Open ChatGPT (GPT-4 with vision recommended)
2. Paste the prompt from `chatgpt_conversion_prompt.md`
3. Upload your screenshot(s)
4. ChatGPT will return JSON data

### 4. Save JSON File

1. Copy the JSON output from ChatGPT
2. Save it as `examples/post_YYYY_MM_DD.json` (use the post date)
   - Example: `examples/post_2025_10_15.json`
3. Repeat for 10-30 of your posts

**Focus on**: Your best performing posts + a mix of different topics/formats

### 5. Run Analytics

Once you have at least 5 JSON files:

```bash
# Analyze your style (works with text OR JSON files)
python scripts/analyze_style.py

# Analyze what drives engagement (requires JSON files)
python scripts/analyze_performance.py
```

### 6. Generate Optimized Posts

Now when you generate posts, the system automatically uses your performance insights:

```bash
python scripts/generate.py \
  --manual \
  --topic "Your topic" \
  --goal "your goal"
```

The generator will:
- Match your writing style
- Use optimal post length from your top performers
- Suggest formats that work for you (lists, questions, etc.)
- Recommend best posting times
- Apply LinkedIn algorithm optimization

## Example JSON Structure

```json
{
  "content": "Your full post text here...",
  "metadata": {
    "date": "2025-10-15",
    "time": "09:30",
    "timezone": "EET"
  },
  "engagement": {
    "impressions": 12500,
    "reactions": 243,
    "comments": 18,
    "shares": 12
  },
  "post_characteristics": {
    "type": "text_only",
    "has_list": true,
    "has_question": true,
    "character_count": 850
  }
}
```

See `examples/post_example.json` for the complete schema.

## Tips for Best Results

### Screenshot Quality
- Use high resolution screenshots
- Ensure all numbers are clearly visible
- Capture the full post text
- Include post date/time if visible

### Post Selection
- Include 10-30 posts minimum
- Mix of high and medium performers (to see patterns)
- Variety of topics and formats
- Recent posts preferred (algorithm changes over time)

### Data Accuracy
- Double-check ChatGPT's numbers match your screenshots
- Manually fix any obvious errors in the JSON
- If ChatGPT can't see certain data, you can add it manually

### File Naming
- Use consistent naming: `post_YYYY_MM_DD.json`
- Or use descriptive names: `post_ai_healthcare_oct15.json`
- Avoid spaces in filenames

## What Gets Analyzed

Once you have JSON files, `analyze_performance.py` will tell you:

- **Best posting times**: Which hours get most engagement
- **Best posting days**: Which days of the week work best
- **Optimal length**: Character count of your top posts
- **Winning formats**: Lists, questions, images, hashtags usage
- **Top topics**: What subjects resonate most
- **Top performers**: Your 5 best posts analyzed in detail

## Maintaining Your Data

### Regular Updates
- Add new posts every month
- Keep your data fresh (algorithm evolves)
- Re-run analysis periodically

### Storage
- Keep your JSON files backed up
- LinkedIn only shows limited historical data
- This becomes your permanent analytics database

## Troubleshooting

**ChatGPT can't read the screenshot**
- Try higher quality screenshot
- Break into multiple smaller screenshots
- Manually type unclear numbers into the JSON

**JSON format errors**
- Validate JSON at jsonlint.com
- Check for missing commas, brackets
- Compare to `examples/post_example.json`

**Not enough data for analysis**
- Need at least 5 posts with engagement data
- Add more posts for better insights
- Quality > quantity (pick your best posts)

## Alternative: Manual Entry

If screenshots are difficult, you can manually create JSON files:

1. Copy `examples/post_example.json`
2. Fill in your post data manually
3. Check LinkedIn analytics for metrics
4. Save as new JSON file

This is slower but gives you full control.

## Privacy Note

All data stays local on your machine. Nothing is sent to any service except:
- Screenshots to ChatGPT (for conversion only)
- Post content to Claude CLI (for generation only)

Your engagement data never leaves your computer.
