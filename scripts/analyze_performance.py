#!/usr/bin/env python3
"""
Performance Analyzer - Analyzes engagement data to find what drives performance
"""

import os
import sys
import json
import yaml
from pathlib import Path
from datetime import datetime
from collections import defaultdict

def load_config():
    """Load configuration from config.yaml"""
    config_path = Path(__file__).parent.parent / "config.yaml"
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def load_posts_with_metadata(examples_dir):
    """Load all JSON posts with engagement data"""
    examples_path = Path(__file__).parent.parent / examples_dir

    if not examples_path.exists():
        print(f"Error: Examples directory not found at {examples_path}")
        sys.exit(1)

    json_files = list(examples_path.glob("*.json"))
    json_files = [f for f in json_files if 'example' not in f.name.lower()]

    if not json_files:
        print(f"Error: No JSON files with engagement data found in {examples_path}")
        print("Please add JSON files with your posts and their analytics")
        sys.exit(1)

    posts = []
    for file_path in json_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Validate required fields
                if data.get('content') and data.get('engagement'):
                    posts.append(data)
        except json.JSONDecodeError:
            print(f"Warning: Could not parse JSON file {file_path.name}, skipping...")
        except Exception as e:
            print(f"Warning: Error reading {file_path.name}: {e}, skipping...")

    print(f"Loaded {len(posts)} posts with engagement data\n")
    return posts

def calculate_engagement_rate(post):
    """Calculate engagement rate for a post"""
    engagement = post.get('engagement', {})
    impressions = engagement.get('impressions', 0)

    if impressions == 0:
        return 0.0

    reactions = engagement.get('reactions', 0)
    comments = engagement.get('comments', 0)
    shares = engagement.get('shares', 0)

    return ((reactions + comments + shares) / impressions) * 100

def analyze_timing(posts):
    """Analyze best posting times"""
    print("📅 TIMING ANALYSIS")
    print("=" * 60)

    time_data = defaultdict(lambda: {'count': 0, 'total_engagement': 0, 'posts': []})
    day_data = defaultdict(lambda: {'count': 0, 'total_engagement': 0, 'posts': []})

    for post in posts:
        metadata = post.get('metadata', {})
        date_str = metadata.get('date')
        time_str = metadata.get('time')

        engagement_rate = calculate_engagement_rate(post)

        if date_str:
            try:
                date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                day = date_obj.strftime("%A")
                day_data[day]['count'] += 1
                day_data[day]['total_engagement'] += engagement_rate
                day_data[day]['posts'].append(post)
            except:
                pass

        if time_str:
            try:
                hour = int(time_str.split(':')[0])
                time_bucket = f"{hour:02d}:00-{hour:02d}:59"
                time_data[time_bucket]['count'] += 1
                time_data[time_bucket]['total_engagement'] += engagement_rate
                time_data[time_bucket]['posts'].append(post)
            except:
                pass

    # Best days
    if day_data:
        print("\nBest Days to Post:")
        sorted_days = sorted(day_data.items(), key=lambda x: x[1]['total_engagement'] / x[1]['count'], reverse=True)
        for day, data in sorted_days[:3]:
            avg_engagement = data['total_engagement'] / data['count']
            print(f"  {day:10s} - Avg Engagement: {avg_engagement:.2f}% ({data['count']} posts)")

    # Best times
    if time_data:
        print("\nBest Times to Post:")
        sorted_times = sorted(time_data.items(), key=lambda x: x[1]['total_engagement'] / x[1]['count'], reverse=True)
        for time, data in sorted_times[:5]:
            avg_engagement = data['total_engagement'] / data['count']
            print(f"  {time} - Avg Engagement: {avg_engagement:.2f}% ({data['count']} posts)")

    print()

def analyze_post_characteristics(posts):
    """Analyze what post characteristics drive engagement"""
    print("📊 POST CHARACTERISTICS ANALYSIS")
    print("=" * 60)

    # Length analysis
    length_buckets = {
        'Short (0-500 chars)': [],
        'Medium (501-1000 chars)': [],
        'Long (1001-1500 chars)': [],
        'Very Long (1501+ chars)': []
    }

    for post in posts:
        char_count = post.get('post_characteristics', {}).get('character_count', 0)
        engagement_rate = calculate_engagement_rate(post)

        if char_count <= 500:
            length_buckets['Short (0-500 chars)'].append(engagement_rate)
        elif char_count <= 1000:
            length_buckets['Medium (501-1000 chars)'].append(engagement_rate)
        elif char_count <= 1500:
            length_buckets['Long (1001-1500 chars)'].append(engagement_rate)
        else:
            length_buckets['Very Long (1501+ chars)'].append(engagement_rate)

    print("\nEngagement by Post Length:")
    for bucket, rates in length_buckets.items():
        if rates:
            avg = sum(rates) / len(rates)
            print(f"  {bucket:30s} - Avg: {avg:.2f}% ({len(rates)} posts)")

    # Format analysis
    format_data = {
        'has_image': [],
        'has_video': [],
        'has_link': [],
        'has_hashtags': [],
        'has_emoji': [],
        'has_list': [],
        'has_question': []
    }

    for post in posts:
        chars = post.get('post_characteristics', {})
        engagement_rate = calculate_engagement_rate(post)

        for key in format_data.keys():
            if chars.get(key, False):
                format_data[key].append(engagement_rate)

    print("\nEngagement by Format Elements:")
    for element, rates in format_data.items():
        if rates:
            avg = sum(rates) / len(rates)
            element_name = element.replace('has_', '').replace('_', ' ').title()
            print(f"  {element_name:15s} - Avg: {avg:.2f}% ({len(rates)} posts)")

    # Post type analysis
    type_data = defaultdict(list)
    for post in posts:
        post_type = post.get('post_characteristics', {}).get('type', 'unknown')
        engagement_rate = calculate_engagement_rate(post)
        type_data[post_type].append(engagement_rate)

    print("\nEngagement by Post Type:")
    for post_type, rates in sorted(type_data.items()):
        avg = sum(rates) / len(rates)
        print(f"  {post_type:15s} - Avg: {avg:.2f}% ({len(rates)} posts)")

    print()

def analyze_top_performers(posts):
    """Identify and analyze top performing posts"""
    print("🏆 TOP PERFORMING POSTS")
    print("=" * 60)

    # Sort by engagement rate
    posts_with_rate = [(post, calculate_engagement_rate(post)) for post in posts]
    posts_with_rate.sort(key=lambda x: x[1], reverse=True)

    print("\nTop 5 Posts by Engagement Rate:")
    for i, (post, rate) in enumerate(posts_with_rate[:5], 1):
        engagement = post.get('engagement', {})
        content_preview = post.get('content', '')[:80].replace('\n', ' ')
        print(f"\n{i}. Engagement Rate: {rate:.2f}%")
        print(f"   Impressions: {engagement.get('impressions', 0):,}")
        print(f"   Reactions: {engagement.get('reactions', 0)}, Comments: {engagement.get('comments', 0)}, Shares: {engagement.get('shares', 0)}")
        print(f"   Preview: \"{content_preview}...\"")

        # Characteristics
        chars = post.get('post_characteristics', {})
        characteristics = []
        if chars.get('has_image'): characteristics.append('image')
        if chars.get('has_video'): characteristics.append('video')
        if chars.get('has_list'): characteristics.append('list')
        if chars.get('has_question'): characteristics.append('question')
        if chars.get('has_hashtags'): characteristics.append('hashtags')

        if characteristics:
            print(f"   Characteristics: {', '.join(characteristics)}")

        # Topic
        topic = post.get('context', {}).get('topic', 'N/A')
        goal = post.get('context', {}).get('goal', 'N/A')
        print(f"   Topic: {topic} | Goal: {goal}")

    print()

def analyze_content_patterns(posts):
    """Analyze content patterns in high vs low performers"""
    print("🔍 CONTENT PATTERN ANALYSIS")
    print("=" * 60)

    # Separate into top and bottom performers
    posts_with_rate = [(post, calculate_engagement_rate(post)) for post in posts]
    posts_with_rate.sort(key=lambda x: x[1], reverse=True)

    top_quartile_size = max(1, len(posts_with_rate) // 4)
    top_posts = [p for p, r in posts_with_rate[:top_quartile_size]]
    bottom_posts = [p for p, r in posts_with_rate[-top_quartile_size:]]

    # Analyze topics
    top_topics = [p.get('context', {}).get('topic', 'unknown') for p in top_posts]
    bottom_topics = [p.get('context', {}).get('topic', 'unknown') for p in bottom_posts]

    print("\nTop Performing Topics:")
    topic_counts = defaultdict(int)
    for topic in top_topics:
        topic_counts[topic] += 1

    for topic, count in sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"  - {topic} ({count} posts)")

    # Analyze goals
    top_goals = [p.get('context', {}).get('goal', 'unknown') for p in top_posts]

    print("\nTop Performing Goals:")
    goal_counts = defaultdict(int)
    for goal in top_goals:
        goal_counts[goal] += 1

    for goal, count in sorted(goal_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  - {goal.title()} ({count} posts)")

    print()

def generate_recommendations(posts):
    """Generate actionable recommendations"""
    print("💡 RECOMMENDATIONS")
    print("=" * 60)

    posts_with_rate = [(post, calculate_engagement_rate(post)) for post in posts]
    posts_with_rate.sort(key=lambda x: x[1], reverse=True)

    top_quartile_size = max(1, len(posts_with_rate) // 4)
    top_posts = [p for p, r in posts_with_rate[:top_quartile_size]]

    # Calculate averages for top performers
    avg_length = sum(p.get('post_characteristics', {}).get('character_count', 0) for p in top_posts) / len(top_posts)

    format_counts = {
        'has_list': sum(1 for p in top_posts if p.get('post_characteristics', {}).get('has_list')),
        'has_question': sum(1 for p in top_posts if p.get('post_characteristics', {}).get('has_question')),
        'has_hashtags': sum(1 for p in top_posts if p.get('post_characteristics', {}).get('has_hashtags')),
        'has_emoji': sum(1 for p in top_posts if p.get('post_characteristics', {}).get('has_emoji')),
        'has_image': sum(1 for p in top_posts if p.get('post_characteristics', {}).get('has_image')),
    }

    print("\nBased on your top performing posts:\n")

    print(f"1. Optimal Post Length: ~{int(avg_length)} characters")

    print("\n2. Effective Format Elements:")
    for element, count in sorted(format_counts.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / len(top_posts)) * 100
        if percentage >= 50:
            element_name = element.replace('has_', '').replace('_', ' ').title()
            print(f"   - {element_name}: Used in {percentage:.0f}% of top posts")

    # Best time recommendation
    time_data = defaultdict(list)
    for post in top_posts:
        time_str = post.get('metadata', {}).get('time')
        if time_str:
            try:
                hour = int(time_str.split(':')[0])
                time_data[hour].append(calculate_engagement_rate(post))
            except:
                pass

    if time_data:
        best_hour = max(time_data.items(), key=lambda x: sum(x[1])/len(x[1]))[0]
        print(f"\n3. Best Posting Time: Around {best_hour:02d}:00")

    # Best day recommendation
    day_data = defaultdict(list)
    for post in top_posts:
        date_str = post.get('metadata', {}).get('date')
        if date_str:
            try:
                date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                day = date_obj.strftime("%A")
                day_data[day].append(calculate_engagement_rate(post))
            except:
                pass

    if day_data:
        best_day = max(day_data.items(), key=lambda x: sum(x[1])/len(x[1]))[0]
        print(f"\n4. Best Posting Day: {best_day}")

    print("\n5. LinkedIn Algorithm Optimization:")
    print("   - Aim for quick engagement in the first hour (crucial for reach)")
    print("   - Use engaging hooks to increase dwell time")
    print("   - End with questions to encourage comments")
    print("   - Avoid external links in first comment (post them later)")

    print()

def main():
    print("=== LinkedIn Post Performance Analyzer ===\n")

    # Load config
    config = load_config()
    examples_dir = config['paths']['examples']

    # Load posts with metadata
    posts = load_posts_with_metadata(examples_dir)

    if len(posts) < 5:
        print("⚠ Warning: You have fewer than 5 posts with engagement data.")
        print("   Add more posts for more accurate analysis.\n")

    # Run analyses
    analyze_timing(posts)
    analyze_post_characteristics(posts)
    analyze_top_performers(posts)
    analyze_content_patterns(posts)
    generate_recommendations(posts)

    print("✓ Performance analysis complete!\n")
    print("Use these insights when generating new posts with:")
    print("  python scripts/generate.py --manual --topic 'your topic' --goal 'your goal'")

if __name__ == "__main__":
    main()
