import json
from pathlib import Path
from graphviz import Digraph


def json_to_diagram(json_file: str, config_file: str, output: str = "architecture", 
                   show_edge_labels: bool = True, layout: str = 'tree'):
    """
    Diagram generator using config.json for all styling.
    """
    with open(json_file) as f:
        data = json.load(f)
    
    with open(config_file) as f:
        config = json.load(f)
    
    generate_diagram(data, config, output, show_edge_labels, layout)

def generate_diagram(data, config, output: str, show_edge_labels: bool, layout: str):
    """Generate diagram with config-driven styling."""
    dot = Digraph(name=data.get('topic'), engine='dot')
    
    global_config = config.get('global', {})
    
    # Global attributes
    if layout == 'tree':
        dot.attr(rankdir='LR', 
                bgcolor=global_config.get('bgcolor', '#F1F5F9'),
                fontname=global_config.get('fontname', 'Arial'),
                splines='curved', 
                dpi=global_config.get('dpi', '300'),
                nodesep='0.4', ranksep='1.0')
    else:
        dot.attr(rankdir='LR',
                bgcolor=global_config.get('bgcolor', '#F1F5F9'),
                fontname=global_config.get('fontname', 'Arial'),
                splines='ortho', 
                dpi=global_config.get('dpi', '300'))
    
    dot.attr('node', fontname=global_config.get('fontname', 'Arial'), fontsize='10', margin='0.12')
    dot.attr('edge', fontname=global_config.get('fontname', 'Arial'), fontsize='9',
            labelfontcolor=global_config.get('edge_fontcolor', '#1E293B'))
    
    # Config maps
    type_mapping = config.get('type_mapping', {})
    node_styles = config.get('node_styles', {})
    edge_styles = config.get('edge_styles', {})
    
    # Add nodes
    for name, comp in data['components'].items():
        comp_type = comp.get('type', 'unknown')
        
        # Get style from type_mapping + node_styles
        type_config = type_mapping.get(comp_type, {})
        shape_name = type_config.get('shape', 'rounded_rectangle')
        fillcolor = type_config.get('fillcolor', '#6B7280')
        
        shape_config = node_styles.get(shape_name, {})
        
        comp_label = f"{name}\\n({comp_type})"
        
        dot.node(
            name,
            label=comp_label,
            shape=shape_config.get('shape', 'box'),
            style=shape_config.get('style', 'filled'),
            fillcolor=fillcolor,
            color='#1E293B',
            penwidth=shape_config.get('penwidth', '1.2'),
            width=shape_config.get('width', '1.2'),
            height=shape_config.get('height', '0.8'),
            fontcolor=global_config.get('node_fontcolor', 'white')
        )
    
    # Add edges
    for i, rel in enumerate(data['relationships']):
        line_type = rel.get('line', 'solid')
        
        # Get edge style from config
        edge_config = edge_styles.get(line_type, {})
        edge_color = edge_config.get('color', '#3B82F6')
        edge_style = edge_config.get('style', 'solid')
        edge_penwidth = edge_config.get('penwidth', '2')
        
        arrow = 'normal' if rel.get('arrow', True) else 'none'
        
        # Label priority: label > type
        edge_label = rel.get('label')
        if not edge_label and show_edge_labels:
            edge_label = rel.get('type', '').replace('_', ' ').title()
        
        tailport = f"{i % 4 + 1}:e" if layout == 'tree' else None
        headport = f"{(i + 2) % 4 + 1}:w"
        
        # FIXED: Removed labelfloat=True (boolean error)
        dot.edge(
            rel['from'], rel['to'],
            label=edge_label or '',
            style=edge_style,
            arrowhead=arrow,
            color=edge_color,
            penwidth=edge_penwidth,
            fontcolor=global_config.get('edge_fontcolor', '#1E293B'),
            tailport=tailport,
            headport=headport
        )
    
    png_file = Path(f"{output}.png")
    dot.render(str(png_file.with_suffix('')), format='png', cleanup=True, view=False)
    print(f"✅ Generated from config: {png_file}")


# Usage - Fixed signature call
json_to_diagram('file.json', 'config.json', 'ecommerce_final', layout='tree')
