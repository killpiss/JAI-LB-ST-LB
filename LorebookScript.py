#!/usr/bin/env python3
"""
Convert various lorebook formats to SillyTavern World Info format.
Usage: python convert_lorebook.py <input.json> <output_name>
"""

import json
import sys


def get_field(entry, *field_names, default=None):
    """Try multiple field names, return first found or default."""
    for name in field_names:
        if name in entry:
            return entry[name]
    return default


def parse_keys(value):
    """Convert keys to list format, handling strings or lists."""
    if isinstance(value, list):
        return value
    if isinstance(value, str):
        return [k.strip() for k in value.split(",") if k.strip()]
    return []


def convert_to_sillytavern(input_data, lorebook_name="Lorebook"):
    """Convert any lorebook format to SillyTavern World Info format."""
    
    entries = {}
    
    for idx, entry in enumerate(input_data):
        keys = parse_keys(get_field(entry, "key", "keys", "keyword", "keywords", default=[]))
        keysecondary = parse_keys(get_field(entry, "keysecondary", "secondary_keys", "keys_secondary", default=[]))
        
        content = get_field(entry, "content", "text", "entry", "body", "description", default="")
        comment = get_field(entry, "name", "comment", "title", "memo", "label", default=f"Entry {idx}")
        
        enabled = get_field(entry, "enabled", "active", default=True)
        constant = get_field(entry, "constant", "always_active", "permanent", default=False)
        
        order = get_field(entry, "insertion_order", "order", "priority", "sort_order", default=100)
        position = get_field(entry, "position", "insert_position", default=4)  # 4 = at depth
        depth = get_field(entry, "depth", "scan_depth", default=4)
        
        probability = get_field(entry, "probability", "chance", "activation_chance", default=100)
        
        case_sensitive = get_field(entry, "case_sensitive", "caseSensitive", default=False)
        match_whole = get_field(entry, "matchWholeWords", "match_whole_words", "whole_words", default=None)
        
        selective_logic = get_field(entry, "selectiveLogic", "selective_logic", default=0)
        exclude_recursion = get_field(entry, "excludeRecursion", "exclude_recursion", default=False)
        
        group = get_field(entry, "category", "group", "tag", "folder", default="")
        
        st_entry = {
            "uid": idx,
            "key": keys,
            "keysecondary": keysecondary,
            "comment": comment,
            "content": content,
            "constant": constant,
            "selective": len(keysecondary) > 0,
            "selectiveLogic": selective_logic,
            "addMemo": True,
            "order": order,
            "position": position,
            "disable": not enabled,
            "excludeRecursion": exclude_recursion,
            "probability": probability,
            "useProbability": probability < 100,
            "depth": depth,
            "group": group,
            "scanDepth": None,
            "caseSensitive": case_sensitive,
            "matchWholeWords": match_whole,
            "automationId": "",
            "role": None,
            "vectorized": False,
            "displayIndex": idx
        }
        entries[str(idx)] = st_entry
    
    return {
        "name": lorebook_name,
        "description": f"{lorebook_name} World Info",
        "extensions": {},
        "entries": entries
    }


def extract_entries(data):
    """Extract entry list from various input structures."""
    if isinstance(data, list):
        return data
    
    if isinstance(data, dict):
        # Check common container keys
        for key in ["entries", "items", "data", "lorebook", "worldInfo", "world_info"]:
            if key in data:
                container = data[key]
                if isinstance(container, list):
                    return container
                if isinstance(container, dict):
                    return list(container.values())
        # Single entry
        return [data]
    
    return []


def main():
    if len(sys.argv) < 3:
        script = sys.argv[0]
        print(f"Usage: python {script} <input.json> <output_name>")
        print(f"Example: python {script} my_lore.json MyWorld")
        print("         Creates: MyWorld.json")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_name = sys.argv[2]
    output_file = f"{output_name}.json"
    
    try:
        with open(input_file, "r", encoding="utf-8") as f:
            raw_data = json.load(f)
    except FileNotFoundError:
        print(f"Error: '{input_file}' not found")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON - {e}")
        sys.exit(1)
    
    entries = extract_entries(raw_data)
    
    if not entries:
        print("Error: No entries found in input")
        sys.exit(1)
    
    result = convert_to_sillytavern(entries, output_name)
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"Converted {len(entries)} entries -> {output_file}")


if __name__ == "__main__":
    main()
