#!/usr/bin/env python3
"""
Excel to JSON Converter - Converts LinkedIn Analytics Excel exports to JSON format
"""

import os
import sys
import json
import re
from pathlib import Path
from datetime import datetime
import pandas as pd
from openpyxl import load_workbook
from openpyxl.drawing.image import Image as OpenpyxlImage

def parse_number(value):
    """Parse number from string with commas (e.g., '5,537' -> 5537)"""
    if pd.isna(value):
        return 0
    if isinstance(value, (int, float)):
        return int(value)
    # Remove commas and convert
    try:
        return int(str(value).replace(',', ''))
    except:
        return 0

def parse_date(date_str):
    """Parse date from various formats"""
    if pd.isna(date_str):
        return None

    try:
        # Try parsing "Sep 30, 2025" format
        date_obj = datetime.strptime(str(date_str).strip(), "%b %d, %Y")
        return date_obj.strftime("%Y-%m-%d")
    except:
        try:
            # Try other common formats
            date_obj = datetime.strptime(str(date_str).strip(), "%Y-%m-%d")
            return date_obj.strftime("%Y-%m-%d")
        except:
            return None

def parse_time(time_str):
    """Parse time from '6:54 AM' format"""
    if pd.isna(time_str):
        return None

    try:
        time_obj = datetime.strptime(str(time_str).strip(), "%I:%M %p")
        return time_obj.strftime("%H:%M")
    except:
        return None

def extract_content(df, start_idx):
    """Extract post content from DataFrame starting at index"""
    content_lines = []

    for i in range(start_idx + 1, len(df)):
        row_val_0 = df.iloc[i, 0]
        row_val_1 = df.iloc[i, 1] if len(df.columns) > 1 else None

        # Stop if we hit 'Image' or another section marker
        if pd.notna(row_val_0) and str(row_val_0).strip().lower() == 'image':
            break

        # Add content from column 1 if present
        if pd.notna(row_val_1):
            content_lines.append(str(row_val_1).strip())
        # Otherwise check column 0 (for multi-row content)
        elif pd.notna(row_val_0) and str(row_val_0).strip() not in ['nan', '']:
            content_lines.append(str(row_val_0).strip())

    return '\n\n'.join(content_lines)

def extract_images_from_excel(excel_path, output_dir, post_id):
    """Extract embedded images from Excel file (Excel files are ZIP archives)"""
    import zipfile

    try:
        images_extracted = []
        image_counter = 1

        # Excel files are ZIP archives - extract images from xl/media/
        with zipfile.ZipFile(excel_path, 'r') as zip_ref:
            # Find all files in media folder
            media_files = [f for f in zip_ref.namelist() if 'xl/media/' in f and not f.endswith('/')]

            if media_files:
                print(f"   Found {len(media_files)} image(s) in Excel file")

                for media_file in media_files:
                    # Get file extension
                    file_ext = media_file.split('.')[-1] if '.' in media_file else 'png'

                    # Create output filename
                    image_filename = f"post_{post_id}_image_{image_counter}.{file_ext}"
                    image_path = output_dir / image_filename

                    # Extract and save
                    with zip_ref.open(media_file) as source:
                        with open(image_path, 'wb') as target:
                            target.write(source.read())

                    images_extracted.append(image_filename)
                    print(f"   ✓ Extracted: {image_filename}")
                    image_counter += 1
            else:
                print(f"   No images found in Excel archive")

        return images_extracted

    except Exception as e:
        print(f"   Warning: Could not extract images: {e}")
        import traceback
        traceback.print_exc()
        return []

def parse_linkedin_excel(excel_path, examples_dir):
    """Parse LinkedIn Analytics Excel file and convert to JSON"""

    print(f"\nProcessing: {excel_path.name}")

    # Read Excel without header
    df = pd.read_excel(excel_path, header=None)

    # Initialize data structure
    post_data = {
        "post_id": "",
        "content": "",
        "metadata": {
            "date": None,
            "time": None,
            "timezone": "EET"  # Default, can be changed
        },
        "engagement": {
            "impressions": 0,
            "reactions": 0,
            "comments": 0,
            "shares": 0,
            "clicks": 0,
            "engagement_rate": 0.0
        },
        "post_characteristics": {
            "type": "text_only",
            "has_image": False,
            "has_video": False,
            "has_link": False,
            "has_hashtags": False,
            "hashtags": [],
            "has_emoji": False,
            "has_list": False,
            "has_question": False,
            "word_count": 0,
            "character_count": 0,
            "line_breaks": 0,
            "image_files": []
        },
        "context": {
            "topic": "",
            "goal": "",
            "tone": "professional"
        },
        "notes": "Imported from LinkedIn Analytics Excel export"
    }

    # Parse the Excel structure
    for i, row in df.iterrows():
        label = str(row[0]).strip() if pd.notna(row[0]) else ""
        value = row[1] if len(df.columns) > 1 and pd.notna(row[1]) else None

        # Extract post URL and ID
        if label == "Post URL" and value:
            post_data["post_id"] = str(value).split(':')[-1] if ':' in str(value) else str(value)

        # Extract date
        elif label == "Post Date":
            post_data["metadata"]["date"] = parse_date(value)

        # Extract time
        elif label == "Post Publish Time":
            post_data["metadata"]["time"] = parse_time(value)

        # Extract impressions
        elif label == "Impressions":
            post_data["engagement"]["impressions"] = parse_number(value)

        # Extract reactions
        elif label == "Reactions":
            post_data["engagement"]["reactions"] = parse_number(value)

        # Extract comments
        elif label == "Comments":
            post_data["engagement"]["comments"] = parse_number(value)

        # Extract content
        elif label == "Content":
            post_data["content"] = extract_content(df, i)

        # Check for image marker
        elif label.lower() == "image":
            post_data["post_characteristics"]["has_image"] = True

    # Calculate engagement rate
    if post_data["engagement"]["impressions"] > 0:
        total_engagement = (
            post_data["engagement"]["reactions"] +
            post_data["engagement"]["comments"] +
            post_data["engagement"]["shares"]
        )
        post_data["engagement"]["engagement_rate"] = round(
            (total_engagement / post_data["engagement"]["impressions"]) * 100, 2
        )

    # Analyze content characteristics
    content = post_data["content"]
    if content:
        post_data["post_characteristics"]["word_count"] = len(content.split())
        post_data["post_characteristics"]["character_count"] = len(content)
        post_data["post_characteristics"]["line_breaks"] = content.count('\n')
        post_data["post_characteristics"]["has_emoji"] = bool(re.search(r'[^\w\s,.\-!?]', content))
        post_data["post_characteristics"]["has_question"] = '?' in content

        # Check for hashtags
        hashtags = re.findall(r'#\w+', content)
        if hashtags:
            post_data["post_characteristics"]["has_hashtags"] = True
            post_data["post_characteristics"]["hashtags"] = hashtags

        # Check for lists (numbered or bulleted)
        has_list = bool(re.search(r'(\n\d+\.|\n-|\n•)', content))
        post_data["post_characteristics"]["has_list"] = has_list

        # Check for links
        post_data["post_characteristics"]["has_link"] = bool(
            re.search(r'https?://', content)
        )

    # Extract images from Excel
    images_dir = examples_dir / "images"
    images_dir.mkdir(exist_ok=True)

    extracted_images = extract_images_from_excel(excel_path, images_dir, post_data["post_id"])

    if extracted_images:
        post_data["post_characteristics"]["image_files"] = extracted_images
        post_data["post_characteristics"]["has_image"] = True
        if content:
            post_data["post_characteristics"]["type"] = "image"

    # Determine post type
    if post_data["post_characteristics"]["has_video"]:
        post_data["post_characteristics"]["type"] = "video"
    elif post_data["post_characteristics"]["has_image"]:
        post_data["post_characteristics"]["type"] = "image"
    elif post_data["post_characteristics"]["has_link"]:
        post_data["post_characteristics"]["type"] = "link"

    return post_data

def convert_all_excel_files(examples_dir):
    """Convert all Excel files in examples directory to JSON"""

    examples_path = Path(examples_dir)

    if not examples_path.exists():
        print(f"Error: Examples directory not found at {examples_path}")
        return

    # Find all Excel files
    excel_files = list(examples_path.glob("*.xlsx")) + list(examples_path.glob("*.xls"))

    if not excel_files:
        print("No Excel files found in examples directory")
        return

    print(f"Found {len(excel_files)} Excel file(s)")

    all_posts = []

    for excel_file in excel_files:
        try:
            post_data = parse_linkedin_excel(excel_file, examples_path)

            # Generate JSON filename
            post_id = post_data["post_id"]
            date = post_data["metadata"]["date"]
            if date:
                json_filename = f"post_{date.replace('-', '_')}.json"
            else:
                json_filename = f"post_{post_id}.json"

            json_path = examples_path / json_filename

            # Save individual JSON
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(post_data, f, indent=2, ensure_ascii=False)

            print(f"✓ Created: {json_filename}")

            # Add to collection
            all_posts.append(post_data)

        except Exception as e:
            print(f"✗ Error processing {excel_file.name}: {e}")
            import traceback
            traceback.print_exc()

    # Create combined JSON array
    if all_posts:
        combined_path = examples_path / "all_posts.json"
        with open(combined_path, 'w', encoding='utf-8') as f:
            json.dump(all_posts, f, indent=2, ensure_ascii=False)

        print(f"\n✓ Created combined file: all_posts.json with {len(all_posts)} posts")

    print(f"\n✓ Conversion complete! Processed {len(all_posts)} posts")
    print(f"\nNext steps:")
    print(f"  1. Review the JSON files in {examples_path}")
    print(f"  2. Run: python scripts/analyze_style.py")
    print(f"  3. Run: python scripts/analyze_performance.py")

def main():
    # Get examples directory
    examples_dir = Path(__file__).parent.parent / "examples"

    print("=== Excel to JSON Converter ===\n")
    print("This script converts LinkedIn Analytics Excel exports to JSON format")
    print("Images will be extracted to examples/images/ directory\n")

    convert_all_excel_files(examples_dir)

if __name__ == "__main__":
    main()
