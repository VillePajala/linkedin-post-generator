#!/usr/bin/env python3
"""
Style Analyzer - Analyzes example LinkedIn posts to extract writing style patterns
"""

import os
import sys
import subprocess
import yaml
import json
from pathlib import Path

def load_config():
    """Load configuration from config.yaml"""
    config_path = Path(__file__).parent.parent / "config.yaml"
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def read_example_posts(examples_dir):
    """Read all example posts from the examples directory (supports .txt, .md, and .json)"""
    examples_path = Path(__file__).parent.parent / examples_dir

    if not examples_path.exists():
        print(f"Error: Examples directory not found at {examples_path}")
        sys.exit(1)

    posts = []
    posts_with_metadata = []

    # Read text/markdown files
    text_files = list(examples_path.glob("*.txt")) + list(examples_path.glob("*.md"))

    # Read JSON files
    json_files = list(examples_path.glob("*.json"))

    # Skip example files
    json_files = [f for f in json_files if 'example' not in f.name.lower()]

    if not text_files and not json_files:
        print(f"Error: No example posts found in {examples_path}")
        print("Please add .txt, .md, or .json files with your example posts")
        sys.exit(1)

    # Load text/markdown files
    for file_path in text_files:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            if content:
                posts.append(content)

    # Load JSON files
    for file_path in json_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                content = data.get('content', '').strip()
                if content:
                    posts.append(content)
                    posts_with_metadata.append(data)
        except json.JSONDecodeError:
            print(f"Warning: Could not parse JSON file {file_path.name}, skipping...")
        except Exception as e:
            print(f"Warning: Error reading {file_path.name}: {e}, skipping...")

    print(f"Loaded {len(posts)} example posts ({len(posts_with_metadata)} with engagement data)")
    return posts, posts_with_metadata

def analyze_with_claude(posts, claude_cli):
    """Send posts to Claude for style analysis"""

    # Combine all posts with separators
    combined_posts = "\n\n---POST SEPARATOR---\n\n".join(posts)

    # Build the analysis prompt
    prompt = f"""Analyze these LinkedIn posts and create a detailed style guide that captures the author's writing style.

EXAMPLE POSTS:
{combined_posts}

Please analyze and document:
1. **Tone & Voice**: Is it professional, casual, personal, authoritative, conversational?
2. **Structure Patterns**: How do posts typically open? How do they close? Common section patterns?
3. **Sentence Style**: Short and punchy? Long and flowing? Mix of both? Use of questions?
4. **Formatting**: Use of emojis, bullet points, numbered lists, line breaks, capitalization
5. **Content Approach**: Storytelling, data-driven, opinion-based, educational, provocative?
6. **Typical Length**: Character/word count range
7. **Engagement Tactics**: How does the author encourage interaction? Calls to action?
8. **Unique Quirks**: Any distinctive patterns or signature elements?

Output this as a clear, actionable style guide that can be used to generate new posts that match this exact style."""

    print("\nAnalyzing style with Claude...")
    print(f"Sending {len(combined_posts)} characters to Claude CLI...")

    try:
        # Call Claude CLI with the prompt
        result = subprocess.run(
            [claude_cli],
            input=prompt,
            text=True,
            capture_output=True,
            check=True
        )

        return result.stdout.strip()

    except subprocess.CalledProcessError as e:
        print(f"Error calling Claude CLI: {e}")
        print(f"stderr: {e.stderr}")
        sys.exit(1)
    except FileNotFoundError:
        print(f"Error: Claude CLI command '{claude_cli}' not found")
        print("Please install Claude CLI or update config.yaml with correct command")
        sys.exit(1)

def save_style_guide(style_guide, output_path):
    """Save the generated style guide"""
    style_guide_path = Path(__file__).parent.parent / output_path
    style_guide_path.parent.mkdir(parents=True, exist_ok=True)

    with open(style_guide_path, 'w', encoding='utf-8') as f:
        f.write(style_guide)

    print(f"\n✓ Style guide saved to: {style_guide_path}")

def main():
    print("=== LinkedIn Post Style Analyzer ===\n")

    # Load config
    config = load_config()
    claude_cli = config['claude_cli_command']
    examples_dir = config['paths']['examples']
    style_guide_path = config['paths']['style_guide']

    # Read example posts
    posts, posts_with_metadata = read_example_posts(examples_dir)

    # Analyze with Claude
    style_guide = analyze_with_claude(posts, claude_cli)

    # Save style guide
    save_style_guide(style_guide, style_guide_path)

    print("\n✓ Style analysis complete!")
    print(f"You can now use generate.py to create posts matching your style")

    if posts_with_metadata:
        print(f"\nℹ You have {len(posts_with_metadata)} posts with engagement data.")
        print(f"Run 'python scripts/analyze_performance.py' to find what drives engagement!")

if __name__ == "__main__":
    main()
