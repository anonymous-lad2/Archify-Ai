#!/usr/bin/env python3
"""
Architecture Diagram Generator - JSON Spec as Argument
Updated: nodes → components, edges → relationships
Usage: python arch_gen.py --config config.json --spec '{"components":{...},"relationships":[...]}' [--output demo.png]
"""

import argparse
import json
import graphviz
from pathlib import Path

def get_component_attrs(config, component_type, label):
    """Resolve component attributes from config."""
    mapping = config['type_mapping'].get(component_type, {})
    shape_key = mapping.get('shape', config['global']['default_node_style'])
    styles = config['node_styles'][shape_key].copy()
    styles.update(mapping)
    styles['label'] = label
    styles['fontcolor'] = config['global']['node_fontcolor']
    styles['fontname'] = config['global']['fontname']
    return styles

def generate_diagram(config_path, spec, output='architecture.png'):
    """Generate from JSON config + spec dict with components and relationships."""
    # Load config
    with open(config_path) as f:
        config = json.load(f)
    
    # If spec is a string, parse it as JSON
    if isinstance(spec, str):
        try:
            spec = json.loads(spec)
        except json.JSONDecodeError as e:
            print(f"❌ Error parsing spec JSON: {e}")
            raise
    
    # Validate spec has required keys
    if 'components' not in spec or 'relationships' not in spec:
        print("❌ Spec must contain 'components' and 'relationships' keys")
        raise ValueError("Invalid spec format")
    
    # Create DOT
    dot = graphviz.Digraph('architecture', format='png')
    g = config['global']
    dot.attr(rankdir='LR', bgcolor=g['bgcolor'], fontname=g['fontname'], dpi=str(g['dpi']))
    dot.attr('node', fontname=g['fontname'], fontsize='11')
    
    # Components (formerly nodes)
    for cid, info in spec['components'].items():
        attrs = get_component_attrs(config, info['type'], info['label'])
        dot.node(cid, **attrs)
    
    # Relationships (formerly edges): {"from": "A", "to": "B", "type": "http", "label": "API"}
    for rel in spec['relationships']:
        src = rel['from']
        tgt = rel['to']
        rel_type = rel.get('type', g['default_edge_style'])
        rel_attrs = config['edge_styles'][rel_type].copy()
        rel_attrs['fontcolor'] = g['edge_fontcolor']
        rel_attrs['fontname'] = g['fontname']
        if rel.get('label'):
            rel_attrs['label'] = rel['label']
        dot.edge(src, tgt, **rel_attrs)
    
    # Clusters
    if 'clusters' in spec and spec['clusters']:
        for cluster in spec['clusters']:
            with dot.subgraph(name=f'cluster_{cluster["id"]}') as c:
                c.attr(style='filled', color='lightgrey', label=cluster['label'])
                for cid in cluster['components']:
                    c.node(cid)
    
    # Render
    dot.render(output, cleanup=True)
    print(f"✅ Diagram generated: {output}")
    print(f"📋 DOT source: {output.replace('.png', '.dot')}")
    print(f"📊 Components: {len(spec['components'])}, Relationships: {len(spec['relationships'])}, Clusters: {len(spec.get('clusters', []))}")
    return dot.source

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="JSON Architecture Generator - Spec as Argument")
    parser.add_argument('--config', required=True, help='JSON config file path')
    parser.add_argument('--spec', required=True, help='JSON spec as string (inline JSON or file path)')
    parser.add_argument('--output', default='architecture.png', help='Output PNG file path')
    args = parser.parse_args()
    
    # Check if spec is a file path or JSON string
    spec_input = args.spec
    if spec_input.startswith('{') or spec_input.startswith('['):
        # Treat as JSON string
        spec = spec_input
    else:
        # Try to load as file
        try:
            with open(spec_input) as f:
                spec = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            # Fallback: treat as JSON string
            spec = spec_input
    
    generate_diagram(args.config, spec, args.output)
