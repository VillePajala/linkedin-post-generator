#!/usr/bin/env python3
"""
Context Manager - Create and manage topic contexts for automatic post generation
"""

import os
import sys
import yaml
import argparse
from pathlib import Path

def load_config():
    """Load configuration from config.yaml"""
    config_path = Path(__file__).parent.parent / "config.yaml"
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def list_contexts(contexts_dir):
    """List all available contexts"""
    contexts_path = Path(__file__).parent.parent / contexts_dir
    contexts_path.mkdir(parents=True, exist_ok=True)

    context_files = list(contexts_path.glob("*.yaml"))

    if not context_files:
        print("No contexts found.")
        return []

    contexts = []
    for file_path in context_files:
        with open(file_path, 'r') as f:
            data = yaml.safe_load(f)
            contexts.append({
                'name': file_path.stem,
                'topic': data.get('topic', 'N/A'),
                'themes_count': len(data.get('themes', [])),
                'recent_posts': len(data.get('recent_angles_covered', []))
            })

    return contexts

def create_context_template(name, contexts_dir):
    """Create a new context template"""
    contexts_path = Path(__file__).parent.parent / contexts_dir
    contexts_path.mkdir(parents=True, exist_ok=True)

    file_path = contexts_path / f"{name}.yaml"

    if file_path.exists():
        print(f"Error: Context '{name}' already exists at {file_path}")
        sys.exit(1)

    # Create template
    template = {
        'topic': 'Your Topic Name',
        'description': 'Brief description of what this topic is about',
        'target_audience': 'Who is this content for? (e.g., tech professionals, startup founders)',
        'themes': [
            'Theme or angle 1',
            'Theme or angle 2',
            'Theme or angle 3',
            'Add more themes...'
        ],
        'key_messages': [
            'Key message or perspective 1',
            'Key message or perspective 2',
            'Add more messages...'
        ],
        'posting_frequency': 'How often? (e.g., weekly, bi-weekly)',
        'recent_angles_covered': []
    }

    with open(file_path, 'w') as f:
        yaml.dump(template, f, default_flow_style=False, sort_keys=False)

    print(f"✓ Created new context template: {file_path}")
    print(f"\nPlease edit this file to customize your context:")
    print(f"  - Fill in the topic and description")
    print(f"  - Add relevant themes and key messages")
    print(f"  - Set your target audience")
    print(f"\nThen generate posts with:")
    print(f"  python scripts/generate.py --context {name}")

def show_context_details(name, contexts_dir):
    """Show details of a specific context"""
    contexts_path = Path(__file__).parent.parent / contexts_dir
    file_path = contexts_path / f"{name}.yaml"

    if not file_path.exists():
        print(f"Error: Context '{name}' not found")
        sys.exit(1)

    with open(file_path, 'r') as f:
        data = yaml.safe_load(f)

    print(f"\n{'='*60}")
    print(f"CONTEXT: {name}")
    print(f"{'='*60}")
    print(f"\nTopic: {data.get('topic', 'N/A')}")
    print(f"Description: {data.get('description', 'N/A')}")
    print(f"Target Audience: {data.get('target_audience', 'N/A')}")
    print(f"Posting Frequency: {data.get('posting_frequency', 'N/A')}")

    print(f"\nThemes ({len(data.get('themes', []))}):")
    for theme in data.get('themes', []):
        print(f"  - {theme}")

    print(f"\nKey Messages ({len(data.get('key_messages', []))}):")
    for msg in data.get('key_messages', []):
        print(f"  - {msg}")

    recent = data.get('recent_angles_covered', [])
    print(f"\nRecent Angles Covered ({len(recent)}):")
    if recent:
        for angle in recent:
            print(f"  - {angle}")
    else:
        print("  None yet")

    print(f"\n{'='*60}")

def delete_context(name, contexts_dir):
    """Delete a context"""
    contexts_path = Path(__file__).parent.parent / contexts_dir
    file_path = contexts_path / f"{name}.yaml"

    if not file_path.exists():
        print(f"Error: Context '{name}' not found")
        sys.exit(1)

    confirm = input(f"Delete context '{name}'? (yes/no): ")
    if confirm.lower() == 'yes':
        file_path.unlink()
        print(f"✓ Deleted context '{name}'")
    else:
        print("Cancelled")

def main():
    parser = argparse.ArgumentParser(description='Manage LinkedIn post topic contexts')

    subparsers = parser.add_subparsers(dest='command', help='Command to run')

    # List command
    subparsers.add_parser('list', help='List all contexts')

    # Create command
    create_parser = subparsers.add_parser('create', help='Create a new context')
    create_parser.add_argument('name', help='Name for the new context (e.g., ai_healthcare)')

    # Show command
    show_parser = subparsers.add_parser('show', help='Show context details')
    show_parser.add_argument('name', help='Name of the context to show')

    # Delete command
    delete_parser = subparsers.add_parser('delete', help='Delete a context')
    delete_parser.add_argument('name', help='Name of the context to delete')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    config = load_config()
    contexts_dir = config['paths']['contexts']

    if args.command == 'list':
        print("\n=== Available Contexts ===\n")
        contexts = list_contexts(contexts_dir)
        if contexts:
            for ctx in contexts:
                print(f"📁 {ctx['name']}")
                print(f"   Topic: {ctx['topic']}")
                print(f"   Themes: {ctx['themes_count']} | Recent posts: {ctx['recent_posts']}")
                print()
        print(f"Use 'python scripts/manage_context.py show <name>' for details")

    elif args.command == 'create':
        create_context_template(args.name, contexts_dir)

    elif args.command == 'show':
        show_context_details(args.name, contexts_dir)

    elif args.command == 'delete':
        delete_context(args.name, contexts_dir)

if __name__ == "__main__":
    main()
