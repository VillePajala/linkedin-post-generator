#!/usr/bin/env python3
"""
LinkedIn Post Generator - Generates post drafts using Claude CLI
Supports both manual mode (topic/goal) and auto mode (from context)
"""

import os
import sys
import subprocess
import yaml
import json
import argparse
from pathlib import Path
from datetime import datetime
from collections import defaultdict

def load_config():
    """Load configuration from config.yaml"""
    config_path = Path(__file__).parent.parent / "config.yaml"
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def load_style_guide(style_guide_path):
    """Load the style guide created by analyze_style.py"""
    guide_path = Path(__file__).parent.parent / style_guide_path

    if not guide_path.exists():
        print(f"Error: Style guide not found at {guide_path}")
        print("Please run 'python scripts/analyze_style.py' first to create the style guide")
        sys.exit(1)

    with open(guide_path, 'r', encoding='utf-8') as f:
        return f.read()

def load_context(context_name, contexts_dir):
    """Load a topic context from YAML file"""
    context_path = Path(__file__).parent.parent / contexts_dir / f"{context_name}.yaml"

    if not context_path.exists():
        print(f"Error: Context '{context_name}' not found at {context_path}")
        print(f"Available contexts: {list_contexts(contexts_dir)}")
        sys.exit(1)

    with open(context_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def list_contexts(contexts_dir):
    """List available context files"""
    contexts_path = Path(__file__).parent.parent / contexts_dir
    if not contexts_path.exists():
        return []

    context_files = list(contexts_path.glob("*.yaml"))
    return [f.stem for f in context_files]

def load_inspiration_notes(inspiration_dir, num_notes=3):
    """Load random inspiration notes from inspiration directory"""
    import random

    inspiration_path = Path(__file__).parent.parent / inspiration_dir

    if not inspiration_path.exists():
        return []

    # Find all text files
    text_files = list(inspiration_path.glob("*.txt")) + list(inspiration_path.glob("*.md"))
    text_files = [f for f in text_files if f.name.lower() != 'readme.md']

    if not text_files:
        return []

    # Pick random files
    selected_files = random.sample(text_files, min(num_notes, len(text_files)))

    inspirations = []
    for file_path in selected_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if content:
                    inspirations.append({
                        'file': file_path.name,
                        'content': content
                    })
        except:
            pass

    return inspirations

def load_performance_insights(examples_dir):
    """Load and analyze performance insights from JSON posts"""
    examples_path = Path(__file__).parent.parent / examples_dir

    json_files = list(examples_path.glob("*.json"))
    json_files = [f for f in json_files if 'example' not in f.name.lower()]

    if not json_files:
        return None

    posts = []
    for file_path in json_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if data.get('content') and data.get('engagement'):
                    posts.append(data)
        except:
            pass

    if len(posts) < 3:
        return None

    # Calculate engagement rates
    posts_with_rate = []
    for post in posts:
        engagement = post.get('engagement', {})
        impressions = engagement.get('impressions', 0)
        if impressions > 0:
            reactions = engagement.get('reactions', 0)
            comments = engagement.get('comments', 0)
            shares = engagement.get('shares', 0)
            rate = ((reactions + comments + shares) / impressions) * 100
            posts_with_rate.append((post, rate))

    if not posts_with_rate:
        return None

    # Sort by engagement rate
    posts_with_rate.sort(key=lambda x: x[1], reverse=True)

    # Get top quartile
    top_count = max(1, len(posts_with_rate) // 4)
    top_posts = [p for p, r in posts_with_rate[:top_count]]

    # Calculate insights
    insights = {
        'avg_length': int(sum(p.get('post_characteristics', {}).get('character_count', 0) for p in top_posts) / len(top_posts)),
        'common_formats': [],
        'best_time': None,
        'best_day': None
    }

    # Analyze formats
    format_counts = {
        'lists': sum(1 for p in top_posts if p.get('post_characteristics', {}).get('has_list')),
        'questions': sum(1 for p in top_posts if p.get('post_characteristics', {}).get('has_question')),
        'hashtags': sum(1 for p in top_posts if p.get('post_characteristics', {}).get('has_hashtags')),
        'images': sum(1 for p in top_posts if p.get('post_characteristics', {}).get('has_image')),
    }

    for format_name, count in format_counts.items():
        if count / len(top_posts) >= 0.5:  # Used in 50%+ of top posts
            insights['common_formats'].append(format_name)

    # Best time
    time_data = defaultdict(list)
    for post in top_posts:
        time_str = post.get('metadata', {}).get('time')
        if time_str:
            try:
                hour = int(time_str.split(':')[0])
                rate = next((r for p, r in posts_with_rate if p == post), 0)
                time_data[hour].append(rate)
            except:
                pass

    if time_data:
        best_hour = max(time_data.items(), key=lambda x: sum(x[1])/len(x[1]))[0]
        insights['best_time'] = f"{best_hour:02d}:00"

    # Best day
    day_data = defaultdict(list)
    for post in top_posts:
        date_str = post.get('metadata', {}).get('date')
        if date_str:
            try:
                from datetime import datetime
                date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                day = date_obj.strftime("%A")
                rate = next((r for p, r in posts_with_rate if p == post), 0)
                day_data[day].append(rate)
            except:
                pass

    if day_data:
        best_day = max(day_data.items(), key=lambda x: sum(x[1])/len(x[1]))[0]
        insights['best_day'] = best_day

    return insights

def build_manual_prompt(style_guide, topic, goal, config, insights=None, inspirations=None):
    """Build prompt for manual mode (user provides topic and goal)"""

    audience = config['defaults']['target_audience']
    tone = config['defaults']['tone_guidance']
    max_length = config['defaults']['max_length']

    prompt = f"""You are a LinkedIn post writer. Your task is to write a post that EXACTLY matches the following style guide.

STYLE GUIDE TO FOLLOW:
{style_guide}

POST REQUIREMENTS:
- Topic: {topic}
- Goal: {goal}
- Target Audience: {audience}
- Tone: {tone}
- Maximum Length: {max_length} characters"""

    # Add inspiration notes if available
    if inspirations:
        prompt += f"""

INSPIRATION NOTES (use these as creative fuel, not direct content):"""
        for insp in inspirations:
            prompt += f"""
- {insp['content']}"""

    # Add performance insights if available
    if insights:
        prompt += f"""

PERFORMANCE OPTIMIZATION (based on your top-performing posts):
- Target Length: ~{insights['avg_length']} characters"""

        if insights['common_formats']:
            formats_text = ', '.join(insights['common_formats'])
            prompt += f"""
- Consider using: {formats_text}"""

        prompt += """

LINKEDIN ALGORITHM OPTIMIZATION:
- Create a strong hook in the first 2 lines (crucial for dwell time)
- Aim for engagement in the first hour (reactions/comments boost visibility)
- End with a question or call-to-action to encourage comments
- Keep paragraphs short for mobile readability
- Avoid external links in the post itself (add in first comment if needed)"""

    prompt += """

Write a LinkedIn post draft that matches the style guide precisely. The post should feel authentic and natural, as if written by the person whose style you're emulating.

After the post content, add a separator line and suggest an image that would complement the post.

Format your output as:
[POST CONTENT]

---IMAGE SUGGESTION---
[Brief description of what image/visual would work well with this post]"""

    return prompt

def build_context_prompt(style_guide, context_data, config, inspirations=None):
    """Build prompt for auto mode (using stored context)"""

    audience = config['defaults'].get('target_audience', 'professional audience')
    max_length = config['defaults']['max_length']

    # Format the context data
    topic = context_data.get('topic', 'Unknown')
    themes = context_data.get('themes', [])
    key_messages = context_data.get('key_messages', [])
    target_audience = context_data.get('target_audience', audience)
    recent_angles = context_data.get('recent_angles_covered', [])

    themes_text = "\n".join([f"- {theme}" for theme in themes])
    messages_text = "\n".join([f"- {msg}" for msg in key_messages])
    recent_text = "\n".join([f"- {angle}" for angle in recent_angles]) if recent_angles else "None yet"

    prompt = f"""You are a LinkedIn post writer. Your task is to write a post that EXACTLY matches the following style guide.

STYLE GUIDE TO FOLLOW:
{style_guide}

BROADER TOPIC CONTEXT:
Topic: {topic}
Target Audience: {target_audience}

Key Themes to Draw From:
{themes_text}

Key Messages to Convey:
{messages_text}

Recently Covered Angles (DO NOT REPEAT):
{recent_text}"""

    # Add inspiration notes if available
    if inspirations:
        prompt += f"""

INSPIRATION NOTES (recent observations and ideas - use as creative fuel):"""
        for insp in inspirations:
            prompt += f"""
- {insp['content']}"""

    prompt += f"""

POST REQUIREMENTS:
- Choose a FRESH angle or theme from the list above that hasn't been recently covered
- Maximum Length: {max_length} characters
- Match the style guide precisely
- Keep the post authentic and natural

Write a LinkedIn post draft that explores a new angle within this topic.

After the post content, add a separator line and suggest an image that would complement the post.

Format your output as:
[POST CONTENT]

---IMAGE SUGGESTION---
[Brief description of what image/visual would work well with this post]"""

    return prompt

def generate_with_claude(prompt, claude_cli):
    """Send prompt to Claude CLI and get response"""

    print("\nGenerating post with Claude...")

    try:
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
        print("Please install Claude CLI or update config.yaml")
        sys.exit(1)

def save_draft(content, output_dir, mode, identifier):
    """Save the generated draft to output directory"""

    output_path = Path(__file__).parent.parent / output_dir
    output_path.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"draft_{mode}_{identifier}_{timestamp}.md"

    file_path = output_path / filename

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"\n✓ Draft saved to: {file_path}")
    return file_path

def update_context_with_new_post(context_name, contexts_dir, topic_summary):
    """Update context file to track this post angle"""
    context_path = Path(__file__).parent.parent / contexts_dir / f"{context_name}.yaml"

    with open(context_path, 'r') as f:
        context_data = yaml.safe_load(f)

    if 'recent_angles_covered' not in context_data:
        context_data['recent_angles_covered'] = []

    # Add new entry with date
    date_str = datetime.now().strftime("%Y-%m-%d")
    context_data['recent_angles_covered'].insert(0, f"{date_str}: {topic_summary}")

    # Keep only last 10 entries
    context_data['recent_angles_covered'] = context_data['recent_angles_covered'][:10]

    with open(context_path, 'w') as f:
        yaml.dump(context_data, f, default_flow_style=False, sort_keys=False)

def main():
    parser = argparse.ArgumentParser(description='Generate LinkedIn post drafts')

    # Mode selection
    mode_group = parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument('--manual', action='store_true',
                           help='Manual mode: provide topic and goal')
    mode_group.add_argument('--context', type=str,
                           help='Auto mode: use stored context (provide context name)')

    # Manual mode arguments
    parser.add_argument('--topic', type=str,
                       help='Topic for the post (required in manual mode)')
    parser.add_argument('--goal', type=str,
                       help='Goal of the post (required in manual mode)')

    # Optional argument for context mode
    parser.add_argument('--update-context', action='store_true',
                       help='Update context file with this post angle (context mode only)')
    parser.add_argument('--angle-summary', type=str,
                       help='Brief description of angle covered (used with --update-context)')

    args = parser.parse_args()

    # Validate arguments
    if args.manual and (not args.topic or not args.goal):
        parser.error("--manual mode requires both --topic and --goal")

    print("=== LinkedIn Post Generator ===\n")

    # Load config and style guide
    config = load_config()
    claude_cli = config['claude_cli_command']
    style_guide = load_style_guide(config['paths']['style_guide'])

    # Load performance insights if available
    insights = load_performance_insights(config['paths']['examples'])
    if insights:
        print("📊 Using performance insights from your past posts")
        if insights['best_time']:
            print(f"   Best posting time: {insights['best_time']}")
        if insights['best_day']:
            print(f"   Best posting day: {insights['best_day']}")
        print()

    # Load inspiration notes
    inspirations = load_inspiration_notes('inspiration', num_notes=3)
    if inspirations:
        print(f"💡 Found {len(inspirations)} inspiration notes:")
        for insp in inspirations:
            preview = insp['content'][:60] + "..." if len(insp['content']) > 60 else insp['content']
            print(f"   - {insp['file']}: {preview}")
        print()

    # Build prompt based on mode
    if args.manual:
        print(f"Mode: Manual")
        print(f"Topic: {args.topic}")
        print(f"Goal: {args.goal}")
        prompt = build_manual_prompt(style_guide, args.topic, args.goal, config, insights, inspirations)
        mode = "manual"
        identifier = args.topic.replace(" ", "_")[:30]
    else:
        print(f"Mode: Auto (Context)")
        print(f"Context: {args.context}")
        context_data = load_context(args.context, config['paths']['contexts'])
        prompt = build_context_prompt(style_guide, context_data, config, inspirations)
        mode = "context"
        identifier = args.context

    # Generate post
    draft = generate_with_claude(prompt, claude_cli)

    # Save draft
    draft_path = save_draft(draft, config['paths']['output'], mode, identifier)

    # Update context if requested
    if args.context and args.update_context:
        if args.angle_summary:
            update_context_with_new_post(args.context, config['paths']['contexts'], args.angle_summary)
            print(f"✓ Context updated with new angle")
        else:
            print("⚠ --angle-summary required to update context")

    # Display the draft
    print("\n" + "="*60)
    print("GENERATED DRAFT:")
    print("="*60)
    print(draft)
    print("="*60)

    # Show posting recommendations
    if insights:
        print("\n📅 POSTING RECOMMENDATIONS:")
        if insights['best_day'] and insights['best_time']:
            print(f"   Optimal time: {insights['best_day']} at {insights['best_time']}")
        elif insights['best_day']:
            print(f"   Best day: {insights['best_day']}")
        elif insights['best_time']:
            print(f"   Best time: {insights['best_time']}")

        print("\n💡 TIPS:")
        print("   - Post and engage with comments in the first hour")
        print("   - Tag relevant people to boost initial engagement")
        print("   - Share in relevant LinkedIn groups after posting")

    print(f"\n✓ Generation complete!")

if __name__ == "__main__":
    main()
