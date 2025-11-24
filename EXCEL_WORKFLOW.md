# Excel to JSON Workflow Guide

The **easiest and fastest** way to import your LinkedIn analytics!

## Why This Method is Best

✅ **LinkedIn provides Excel exports** - native feature, no scraping
✅ **All analytics included** - impressions, reactions, comments, etc.
✅ **Batch process multiple posts** - export many at once
✅ **Add post content easily** - simple copy-paste
✅ **Images supported** - save separately and reference them
✅ **One command converts all** - automated JSON generation

## Step-by-Step Workflow

### 1. Export from LinkedIn

For each post you want to analyze:

1. Go to your LinkedIn profile
2. Find the post
3. Click the "..." menu → **View analytics**
4. Click **Export** or **Download** button
5. LinkedIn gives you an Excel file: `PostAnalytics_[YourName]_[PostID].xlsx`

**Pro tip:** Do this for 10-30 of your best posts

### 2. Add Post Content to Excel

LinkedIn's export doesn't include the actual post text, so:

1. Open the Excel file
2. Add a new row with label `Content` in column A
3. In column B (or rows below), paste your full post text
4. Copy-paste from the post on LinkedIn

**Example structure:**
```
| Post URL          | https://linkedin.com/... |
| Post Date         | Sep 30, 2025             |
| Impressions       | 5,537                    |
| Reactions         | 49                       |
| Comments          | 5                        |
| Content           | Your post text here...   |
| Image             |                          |
```

### 3. Handle Images (Optional)

If your post had an image:

**Option A: Mark image presence**
- Add row with `Image` label (converter will detect it)
- Save actual image file as: `examples/images/post_YYYY_MM_DD_image_1.png`

**Option B: Reference in Excel**
- Add the image filename in column B next to `Image` label
- Save image file to `examples/images/`

**Option C: Skip for now**
- Just add the `Image` label
- The system will know `has_image: true` for analytics

### 4. Save Excel Files

Save all your Excel files to the `examples/` directory:

```
examples/
├── PostAnalytics_VillePajala_7378683643709448192.xlsx
├── PostAnalytics_VillePajala_7234567890123456789.xlsx
├── PostAnalytics_VillePajala_7123456789012345678.xlsx
└── ...
```

### 5. Convert to JSON

Run the converter script:

```bash
python scripts/convert_excel_to_json.py
```

**What it does:**
- Reads all `.xlsx` files in `examples/`
- Extracts all engagement data
- Parses post content
- Detects post characteristics (hashtags, questions, lists, emojis, etc.)
- Calculates engagement rate
- Creates individual JSON files: `post_YYYY_MM_DD.json`
- Creates combined file: `all_posts.json`
- Extracts embedded images (if any)

### 6. Review Generated Files

Check the created JSON files:

```bash
ls examples/*.json
```

You should see:
- `post_2025_09_30.json`
- `post_2025_10_15.json`
- `all_posts.json` (contains all posts in array)

Open one to verify:
```json
{
  "post_id": "7378683643709448192",
  "content": "Your full post content...",
  "metadata": {
    "date": "2025-09-30",
    "time": "06:54"
  },
  "engagement": {
    "impressions": 5537,
    "reactions": 49,
    "comments": 5,
    "engagement_rate": 0.98
  },
  "post_characteristics": {
    "type": "image",
    "has_image": true,
    "word_count": 158,
    "character_count": 1298
  }
}
```

### 7. Run Analytics

Now you can analyze your data:

```bash
# Analyze writing style
python scripts/analyze_style.py

# Analyze what drives engagement
python scripts/analyze_performance.py
```

### 8. Generate Optimized Posts

Use your insights:

```bash
python scripts/generate.py \
  --manual \
  --topic "Your topic" \
  --goal "your goal"
```

The generator automatically uses insights from your JSON data!

## Excel File Format

The converter expects this structure in each Excel file:

```
Row  | Column A                  | Column B
-----|---------------------------|------------------
1    | Post URL                  | https://...
2    | Post Date                 | Sep 30, 2025
3    | Post Publish Time         | 6:54 AM
4    | [empty]                   |
5    | Post Performance          |
6    | Impressions               | 5,537
7    | Members reached           | 3,329
8    | Reactions                 | 49
9    | Comments                  | 5
...  | ...                       | ...
N    | Content                   | Your post text...
N+1  | [continuation]            | More post text...
N+2  | Image                     | [optional filename]
```

**Flexible format:** The script is smart about finding the data, so minor variations are OK.

## Handling Images

### Save Images Manually

For each post with an image:

1. Download/screenshot the image from LinkedIn
2. Save as: `examples/images/post_YYYY_MM_DD_image_1.png`
   - Use the post date from the JSON
   - Example: `post_2025_09_30_image_1.png`

3. (Optional) Update the JSON file to reference it:
   ```json
   "post_characteristics": {
     "image_files": ["post_2025_09_30_image_1.png"]
   }
   ```

The analytics script will detect posts with images and include that in the analysis.

### Image Naming Convention

```
post_YYYY_MM_DD_image_N.png

Examples:
- post_2025_09_30_image_1.png
- post_2025_10_15_image_1.png
- post_2025_10_15_image_2.png  (if post has multiple images)
```

## Tips for Best Results

### Excel Preparation
- ✅ Keep LinkedIn's original format (don't delete rows)
- ✅ Add `Content` row with full post text
- ✅ Mark `Image` if post had image
- ✅ Multiple files? Just drop them all in `examples/`

### Content Accuracy
- ✅ Copy exact post text (including line breaks)
- ✅ Include emojis if used
- ✅ Include hashtags
- ✅ Preserve formatting

### Batch Processing
- ✅ Export 10-30 posts at once
- ✅ Focus on your best performers
- ✅ Include variety (different topics, formats)
- ✅ Recent posts preferred (algorithm evolves)

### Image Workflow
- ✅ Save images with consistent naming
- ✅ PNG or JPG format
- ✅ Keep in `examples/images/` directory
- ✅ Not critical for analytics (just nice to have)

## Troubleshooting

### "No Excel files found"
- Make sure files have `.xlsx` or `.xls` extension
- Place them in the `examples/` directory
- Check file isn't open in Excel

### "Content field empty"
- Add a row with `Content` label in column A
- Paste your post text in column B (or rows below)
- Make sure text isn't just spaces

### "Wrong engagement numbers"
- LinkedIn uses commas in numbers (5,537)
- Script handles this automatically
- If numbers seem off, check the Excel file

### "Images not extracted"
- Excel might not have embedded images
- That's OK - just mark `Image` row and save images manually
- Reference them in the JSON if needed

### "Date/time parsing error"
- Script expects "Sep 30, 2025" and "6:54 AM" format
- This is LinkedIn's default format
- If different, edit the script's parse functions

## Advantages Over Screenshot Method

| Feature | Excel Method | Screenshot Method |
|---------|--------------|-------------------|
| Data accuracy | ✅ Exact numbers | ⚠️ OCR errors possible |
| Speed | ✅ Very fast | ⚠️ Slower (ChatGPT conversion) |
| Batch processing | ✅ Many at once | ⚠️ One by one |
| Automation | ✅ Fully automated | ⚠️ Manual ChatGPT step |
| Image handling | ⚠️ Manual save | ✅ In screenshot |
| Setup difficulty | ✅ Simple | ⚠️ Requires ChatGPT |

**Best of both:** Use Excel for data, manually save images if needed!

## Example: Full Workflow

```bash
# 1. Export 20 posts from LinkedIn → Excel files

# 2. Add post content to each Excel file

# 3. Save Excel files to examples/
mv ~/Downloads/PostAnalytics*.xlsx examples/

# 4. Convert all to JSON
python scripts/convert_excel_to_json.py

# 5. (Optional) Add images
# Download images from LinkedIn
# Save to examples/images/ with proper naming

# 6. Analyze
python scripts/analyze_style.py
python scripts/analyze_performance.py

# 7. Generate optimized posts
python scripts/generate.py --manual --topic "AI" --goal "educate"
```

## Maintaining Your Data

### Regular Updates
- Export new posts monthly
- Add them to `examples/`
- Re-run converter
- Re-run analytics

### Organization
```
examples/
├── images/
│   ├── post_2025_09_30_image_1.png
│   ├── post_2025_10_15_image_1.png
│   └── ...
├── post_2025_09_30.json
├── post_2025_10_15.json
├── all_posts.json
└── PostAnalytics_*.xlsx (originals kept for reference)
```

### Backup
- Keep original Excel files
- JSON files are generated (can be recreated)
- Images should be backed up

## Advanced: Custom Excel Format

If your Excel has a different format, you can edit `scripts/convert_excel_to_json.py`:

The script looks for specific labels like:
- `"Post URL"`
- `"Post Date"`
- `"Impressions"`
- `"Reactions"`
- `"Comments"`
- `"Content"`
- `"Image"`

Adjust the labels in the script if your export uses different names.

## Questions?

**Q: Do I need to add content to Excel manually?**
A: Yes, LinkedIn's export doesn't include post text. Quick copy-paste from LinkedIn.

**Q: What if I have 100 posts?**
A: Export all, add content to all, drop in `examples/`, run converter once. It processes all files.

**Q: Can I skip images?**
A: Yes! The `has_image: true` flag is enough for analytics. Images are optional reference.

**Q: What about videos?**
A: Mark with `Video` row like images. Save video thumbnail or note the URL.

**Q: Does this work with Company Page posts?**
A: Yes! Same workflow, same Excel format from LinkedIn.

---

Ready to import your data? Start with 5-10 posts to test the workflow! 🚀
