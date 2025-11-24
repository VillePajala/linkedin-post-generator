# ChatGPT Prompt for Converting LinkedIn Screenshots to JSON

Use this prompt when converting LinkedIn post analytics screenshots to JSON format.

## Prompt to Use:

```
I have a screenshot of a LinkedIn post with its analytics. Please extract all the data and create a JSON file in this exact format:

{
  "post_id": "optional_identifier",
  "content": "FULL POST CONTENT HERE - extract the exact text",
  "metadata": {
    "date": "YYYY-MM-DD",
    "time": "HH:MM",
    "timezone": "your timezone"
  },
  "engagement": {
    "impressions": 0,
    "reactions": 0,
    "comments": 0,
    "shares": 0,
    "clicks": 0,
    "engagement_rate": 0.0,
    "first_hour_reactions": 0
  },
  "post_characteristics": {
    "type": "text_only | image | video | link | poll",
    "has_image": false,
    "has_video": false,
    "has_link": false,
    "has_hashtags": false,
    "hashtags": [],
    "has_emoji": false,
    "has_list": false,
    "has_question": false,
    "word_count": 0,
    "character_count": 0,
    "line_breaks": 0
  },
  "context": {
    "topic": "main topic of the post",
    "goal": "educate | inspire | promote | share | discuss",
    "tone": "professional | casual | personal | authoritative"
  },
  "notes": ""
}

Instructions:
1. Extract ALL visible data from the screenshot
2. For the "content" field, include the EXACT post text with proper line breaks
3. Calculate engagement_rate as: (reactions + comments + shares) / impressions * 100
4. Analyze the post to fill "post_characteristics" (count words, check for lists, questions, etc.)
5. If any data is not visible in the screenshot, use null or 0
6. Infer the context (topic, goal, tone) from the content
7. Count line breaks in the post accurately
8. Return ONLY the JSON, no additional text

Here is the screenshot: [attach screenshot]
```

## Tips for Best Results:

1. **Take clear screenshots** that show:
   - Full post content
   - All engagement metrics (impressions, reactions, comments, shares)
   - Post date and time if visible
   - Any images/videos included

2. **Multiple screenshots per post** if needed:
   - One for post content
   - One for analytics/metrics

3. **Name your files consistently**:
   - `post_2025_10_15.json`
   - `post_ai_healthcare.json`
   - Or use LinkedIn's post ID if visible

4. **Save to `examples/` directory** - our scripts will find them

5. **Mix of .txt and .json files is fine** - scripts handle both

## What ChatGPT Should Extract:

**From Post Content:**
- Exact text with line breaks
- Hashtags used
- Whether it has emojis, lists, questions
- Word/character count
- Type (text, image, video, link)

**From Analytics:**
- Impressions
- Reactions (likes, etc.)
- Comments count
- Shares/reposts
- Clicks (if visible)
- Date/time posted

**From Analysis:**
- Topic
- Goal of the post
- Tone/voice
- Engagement rate calculation

## Example Workflow:

1. Go to LinkedIn → Your post → View analytics
2. Take screenshot(s)
3. Upload to ChatGPT with the prompt above
4. Copy the JSON output
5. Save as `examples/post_YYYY_MM_DD.json`
6. Repeat for 20-30 of your best posts
7. Run `python scripts/analyze_style.py`
8. Run `python scripts/analyze_performance.py` (coming soon)
