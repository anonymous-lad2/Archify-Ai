"""
Enhanced SVG diagram generator with hierarchical layout and modern styling.
Generates professional architecture diagrams with proper component positioning.
"""

import json
import math
from pathlib import Path
from typing import Dict, List, Tuple, Set


class EnhancedSVGGenerator:
    """Generate professional architecture diagrams with hierarchical layout."""
    
    def __init__(self, config_file: str = 'backend/utils/design_rules.json'):
        self.config = {}
        self.type_mapping = {}
        self.node_styles = {}
        self.edge_styles = {}
        self.global_config = {}
        self.default_palette = {
            'client': '#7C3AED',
            'gateway': '#059669', 
            'microservice': '#DC2626',
            'database': '#B91C1C',
            'cache': '#F59E0B',
            'queue': '#8B5CF6',
            'external': '#06B6D4',
            'infrastructure': '#1D4ED8'
        }
        self._load_config(config_file)
    
    def _load_config(self, config_file: str):
        """Load design rules from config file."""
        try:
            with open(config_file) as f:
                self.config = json.load(f)
                self.type_mapping = self.config.get('type_mapping', {})
                self.node_styles = self.config.get('node_styles', {})
                self.edge_styles = self.config.get('edge_styles', {})
                self.global_config = self.config.get('global', {})
        except Exception as e:
            print(f"⚠️ Could not load config: {e}. Using defaults.")
    
    def generate_diagram_svg(self, data: dict, output: str = 'architecture') -> str:
        """Generate SVG diagram with hierarchical layout."""
        components = data.get('components', {})
        relationships = data.get('relationships', [])
        topic = data.get('topic', 'Architecture')
        
        if not components:
            return self._generate_empty_diagram(topic)
        
        # Calculate hierarchical layout
        node_positions = self._calculate_hierarchical_layout(components, relationships)
        
        # Generate SVG with modern styling
        svg_parts = []
        svg_parts.append(self._svg_header())
        
        # Add background with gradient
        svg_parts.append(self._generate_background())
        
        # Add title
        svg_parts.append(self._generate_title(topic))
        
        # Add edges with bezier curves
        svg_parts.append(self._generate_modern_edges(components, relationships, node_positions))
        
        # Add nodes with shadows and modern shapes
        svg_parts.append(self._generate_modern_nodes(components, node_positions))
        
        svg_parts.append('</svg>')
        
        svg_content = '\n'.join(svg_parts)
        
        if output:
            svg_file = Path(f"{output}.svg")
            with open(svg_file, 'w') as f:
                f.write(svg_content)
            print(f"✅ Enhanced SVG diagram generated: {svg_file}")
        
        return svg_content
    
    def _calculate_hierarchical_layout(self, components: Dict, relationships: List) -> Dict[str, Tuple[float, float]]:
        """
        Calculate hierarchical layout based on component types and relationships.
        Layers: Client -> Gateway -> Services -> Data
        """
        # Categorize components by layer
        layers = {
            'client': [],
            'gateway': [],
            'service': [],
            'data': []
        }
        
        component_names = list(components.keys())
        
        for name, comp in components.items():
            comp_type = comp.get('type', 'infrastructure').lower()
            
            if comp_type in ['client']:
                layers['client'].append(name)
            elif comp_type in ['gateway', 'external']:
                layers['gateway'].append(name)
            elif comp_type in ['database', 'cache', 'queue']:
                layers['data'].append(name)
            else:
                layers['service'].append(name)
        
        # Canvas dimensions
        canvas_width = 1400
        canvas_height = 900
        margin_x = 150
        margin_y = 150
        layer_height = 180
        
        positions = {}
        current_y = margin_y
        
        # Position each layer
        for layer_name in ['client', 'gateway', 'service', 'data']:
            layer_components = layers[layer_name]
            if not layer_components:
                continue
            
            num_in_layer = len(layer_components)
            spacing = (canvas_width - 2 * margin_x) / max(num_in_layer, 1)
            
            for i, comp_name in enumerate(layer_components):
                x = margin_x + (i + 0.5) * spacing
                y = current_y
                positions[comp_name] = (x, y)
            
            current_y += layer_height
        
        return positions
    
    def _generate_background(self) -> str:
        """Generate modern gradient background."""
        return '''
        <defs>
            <linearGradient id="bgGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" style="stop-color:#f8fafc;stop-opacity:1" />
                <stop offset="100%" style="stop-color:#e2e8f0;stop-opacity:1" />
            </linearGradient>
            <filter id="shadow" x="-50%" y="-50%" width="200%" height="200%">
                <feGaussianBlur in="SourceAlpha" stdDeviation="4"/>
                <feOffset dx="0" dy="2" result="offsetblur"/>
                <feComponentTransfer>
                    <feFuncA type="linear" slope="0.2"/>
                </feComponentTransfer>
                <feMerge>
                    <feMergeNode/>
                    <feMergeNode in="SourceGraphic"/>
                </feMerge>
            </filter>
            <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
                <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
                <feMerge>
                    <feMergeNode in="coloredBlur"/>
                    <feMergeNode in="SourceGraphic"/>
                </feMerge>
            </filter>
        </defs>
        <rect width="100%" height="100%" fill="url(#bgGradient)"/>
        '''
    
    def _generate_title(self, topic: str) -> str:
        """Generate title with modern styling."""
        return f'''
        <g id="title">
            <rect x="20" y="20" width="{len(topic) * 15 + 40}" height="50" rx="8" 
                  fill="white" filter="url(#shadow)"/>
            <text x="40" y="52" font-size="24" font-weight="600" fill="#1e293b" 
                  font-family="system-ui, -apple-system, sans-serif">{topic}</text>
        </g>
        '''
    
    def _generate_modern_nodes(self, components: Dict, positions: Dict) -> str:
        """Generate nodes with modern shapes, shadows, and styling."""
        svg_parts = []
        
        for name, comp in components.items():
            if name not in positions:
                continue
            
            x, y = positions[name]
            comp_type = comp.get('type', 'infrastructure').lower()
            description = comp.get('description', '')
            color = comp.get('color') or self.default_palette.get(comp_type, '#6B7280')
            shape = comp.get('shape', 'rounded_rectangle')
            
            # Generate shape based on type
            shape_svg = self._draw_shape(x, y, shape, color, name, comp_type, description)
            svg_parts.append(shape_svg)
        
        return '\n'.join(svg_parts)
    
    def _draw_shape(self, x: float, y: float, shape: str, color: str, 
                    name: str, comp_type: str, description: str) -> str:
        """Draw different shapes for different component types."""
        
        if shape == 'cylinder' or comp_type == 'database':
            return self._draw_cylinder(x, y, color, name, comp_type, description)
        elif shape == 'hexagon' or comp_type == 'gateway':
            return self._draw_hexagon(x, y, color, name, comp_type, description)
        elif shape == 'circle':
            return self._draw_circle(x, y, color, name, comp_type, description)
        elif shape == 'lightning' or comp_type == 'queue':
            return self._draw_queue(x, y, color, name, comp_type, description)
        else:
            return self._draw_rounded_rect(x, y, color, name, comp_type, description)
    
    def _draw_rounded_rect(self, x: float, y: float, color: str, 
                          name: str, comp_type: str, description: str) -> str:
        """Draw rounded rectangle component."""
        width, height = 180, 110
        
        return f'''
        <g class="component" filter="url(#shadow)">
            <rect x="{x - width/2}" y="{y - height/2}" width="{width}" height="{height}" 
                  rx="12" fill="{color}" stroke="#1e293b" stroke-width="2"/>
            <rect x="{x - width/2}" y="{y - height/2}" width="{width}" height="35" 
                  rx="12" fill="rgba(0,0,0,0.1)"/>
            <text x="{x}" y="{y - height/2 + 24}" text-anchor="middle" 
                  font-size="15" font-weight="600" fill="white" 
                  font-family="system-ui, -apple-system, sans-serif">{name}</text>
            <text x="{x}" y="{y + 5}" text-anchor="middle" 
                  font-size="11" fill="rgba(255,255,255,0.9)" 
                  font-family="system-ui, -apple-system, sans-serif">{comp_type}</text>
            <text x="{x}" y="{y + 25}" text-anchor="middle" 
                  font-size="10" fill="rgba(255,255,255,0.7)" 
                  font-family="system-ui, -apple-system, sans-serif">
                {(description[:25] + '...') if len(description) > 25 else description}
            </text>
        </g>
        '''
    
    def _draw_cylinder(self, x: float, y: float, color: str, 
                      name: str, comp_type: str, description: str) -> str:
        """Draw cylinder shape for databases."""
        width, height = 160, 120
        ellipse_ry = 20
        
        return f'''
        <g class="component" filter="url(#shadow)">
            <ellipse cx="{x}" cy="{y - height/2 + ellipse_ry}" rx="{width/2}" ry="{ellipse_ry}" 
                     fill="{color}" stroke="#1e293b" stroke-width="2"/>
            <rect x="{x - width/2}" y="{y - height/2 + ellipse_ry}" 
                  width="{width}" height="{height - 2*ellipse_ry}" 
                  fill="{color}" stroke="none"/>
            <rect x="{x - width/2}" y="{y - height/2 + ellipse_ry}" 
                  width="{width}" height="{height - 2*ellipse_ry}" 
                  fill="none" stroke="#1e293b" stroke-width="2"/>
            <ellipse cx="{x}" cy="{y + height/2 - ellipse_ry}" rx="{width/2}" ry="{ellipse_ry}" 
                     fill="{color}" stroke="#1e293b" stroke-width="2"/>
            <text x="{x}" y="{y - 5}" text-anchor="middle" 
                  font-size="15" font-weight="600" fill="white" 
                  font-family="system-ui, -apple-system, sans-serif">{name}</text>
            <text x="{x}" y="{y + 15}" text-anchor="middle" 
                  font-size="11" fill="rgba(255,255,255,0.8)" 
                  font-family="system-ui, -apple-system, sans-serif">{comp_type}</text>
        </g>
        '''
    
    def _draw_hexagon(self, x: float, y: float, color: str, 
                     name: str, comp_type: str, description: str) -> str:
        """Draw hexagon shape for gateways."""
        size = 90
        points = []
        for i in range(6):
            angle = math.pi / 3 * i
            px = x + size * math.cos(angle)
            py = y + size * math.sin(angle)
            points.append(f"{px},{py}")
        
        return f'''
        <g class="component" filter="url(#shadow)">
            <polygon points="{' '.join(points)}" 
                     fill="{color}" stroke="#1e293b" stroke-width="2"/>
            <text x="{x}" y="{y - 8}" text-anchor="middle" 
                  font-size="15" font-weight="600" fill="white" 
                  font-family="system-ui, -apple-system, sans-serif">{name}</text>
            <text x="{x}" y="{y + 12}" text-anchor="middle" 
                  font-size="11" fill="rgba(255,255,255,0.8)" 
                  font-family="system-ui, -apple-system, sans-serif">{comp_type}</text>
        </g>
        '''
    
    def _draw_circle(self, x: float, y: float, color: str, 
                    name: str, comp_type: str, description: str) -> str:
        """Draw circle shape."""
        radius = 70
        
        return f'''
        <g class="component" filter="url(#shadow)">
            <circle cx="{x}" cy="{y}" r="{radius}" 
                    fill="{color}" stroke="#1e293b" stroke-width="2"/>
            <text x="{x}" y="{y - 5}" text-anchor="middle" 
                  font-size="14" font-weight="600" fill="white" 
                  font-family="system-ui, -apple-system, sans-serif">{name}</text>
            <text x="{x}" y="{y + 15}" text-anchor="middle" 
                  font-size="10" fill="rgba(255,255,255,0.8)" 
                  font-family="system-ui, -apple-system, sans-serif">{comp_type}</text>
        </g>
        '''
    
    def _draw_queue(self, x: float, y: float, color: str, 
                   name: str, comp_type: str, description: str) -> str:
        """Draw stacked rectangles for queue/message systems."""
        width, height = 170, 100
        offset = 8
        
        return f'''
        <g class="component" filter="url(#shadow)">
            <rect x="{x - width/2 + offset*2}" y="{y - height/2 - offset*2}" 
                  width="{width}" height="{height}" rx="8" 
                  fill="{color}" opacity="0.3" stroke="#1e293b" stroke-width="1"/>
            <rect x="{x - width/2 + offset}" y="{y - height/2 - offset}" 
                  width="{width}" height="{height}" rx="8" 
                  fill="{color}" opacity="0.6" stroke="#1e293b" stroke-width="1"/>
            <rect x="{x - width/2}" y="{y - height/2}" 
                  width="{width}" height="{height}" rx="8" 
                  fill="{color}" stroke="#1e293b" stroke-width="2"/>
            <text x="{x}" y="{y - 5}" text-anchor="middle" 
                  font-size="15" font-weight="600" fill="white" 
                  font-family="system-ui, -apple-system, sans-serif">{name}</text>
            <text x="{x}" y="{y + 15}" text-anchor="middle" 
                  font-size="11" fill="rgba(255,255,255,0.8)" 
                  font-family="system-ui, -apple-system, sans-serif">{comp_type}</text>
        </g>
        '''
    
    def _generate_modern_edges(self, components: Dict, relationships: List, 
                              positions: Dict) -> str:
        """Generate edges with bezier curves and modern styling."""
        svg_parts = []
        
        for rel in relationships:
            from_name = rel.get('from')
            to_name = rel.get('to')
            
            if from_name not in positions or to_name not in positions:
                continue
            
            x1, y1 = positions[from_name]
            x2, y2 = positions[to_name]
            
            line_type = rel.get('line', 'solid')
            rel_type = rel.get('type', 'request')
            arrow = rel.get('arrow', True)
            
            # Use bezier curves for better visual flow
            edge_svg = self._draw_bezier_edge(x1, y1, x2, y2, line_type, rel_type, arrow)
            svg_parts.append(edge_svg)
        
        return '\n'.join(svg_parts)
    
    def _draw_bezier_edge(self, x1: float, y1: float, x2: float, y2: float, 
                         line_type: str, rel_type: str, arrow: bool) -> str:
        """Draw bezier curve edge."""
        # Calculate control points for smooth curve
        dx = x2 - x1
        dy = y2 - y1
        
        # Control points at 1/3 and 2/3 with vertical offset
        cx1 = x1 + dx * 0.3
        cy1 = y1 + dy * 0.3 + 30
        cx2 = x1 + dx * 0.7
        cy2 = y1 + dy * 0.7 + 30
        
        # Edge color based on relationship type
        color_map = {
            'request': '#3B82F6',
            'response': '#10B981',
            'sync_call': '#3B82F6',
            'async_event': '#8B5CF6',
            'read_write': '#EF4444'
        }
        color = color_map.get(rel_type, '#6B7280')
        
        stroke_dasharray = ''
        if line_type == 'dashed':
            stroke_dasharray = ' stroke-dasharray="8,4"'
        elif line_type == 'dotted':
            stroke_dasharray = ' stroke-dasharray="2,3"'
        
        path = f'M {x1},{y1} C {cx1},{cy1} {cx2},{cy2} {x2},{y2}'
        
        svg = f'''
        <g class="edge">
            <path d="{path}" fill="none" stroke="{color}" 
                  stroke-width="2.5" opacity="0.7"{stroke_dasharray}/>
        '''
        
        if arrow:
            # Calculate arrow at end point
            angle = math.atan2(y2 - cy2, x2 - cx2)
            arrow_size = 12
            
            p1x = x2 - arrow_size * math.cos(angle - math.pi/6)
            p1y = y2 - arrow_size * math.sin(angle - math.pi/6)
            p2x = x2 - arrow_size * math.cos(angle + math.pi/6)
            p2y = y2 - arrow_size * math.sin(angle + math.pi/6)
            
            svg += f'''
            <polygon points="{x2},{y2} {p1x},{p1y} {p2x},{p2y}" 
                     fill="{color}" opacity="0.8"/>
            '''
        
        # Add label
        mid_x = (x1 + x2) / 2
        mid_y = (y1 + y2) / 2 + 20
        label = rel_type.replace('_', ' ').title()
        
        svg += f'''
            <rect x="{mid_x - len(label)*3.5}" y="{mid_y - 12}" 
                  width="{len(label)*7}" height="20" rx="4" 
                  fill="white" opacity="0.9"/>
            <text x="{mid_x}" y="{mid_y + 3}" text-anchor="middle" 
                  font-size="11" fill="#1e293b" font-weight="500"
                  font-family="system-ui, -apple-system, sans-serif">{label}</text>
        </g>
        '''
        
        return svg
    
    def _svg_header(self) -> str:
        """Generate SVG header."""
        return '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1400 900" width="1400" height="900">'''
    
    def _generate_empty_diagram(self, topic: str) -> str:
        """Generate empty diagram placeholder."""
        return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1400 900" width="1400" height="900">
        <rect width="100%" height="100%" fill="#f8fafc"/>
        <text x="700" y="450" text-anchor="middle" font-size="24" fill="#64748b">
            No components found for: {topic}
        </text>
        </svg>'''


def generate_svg_diagram(data: dict, output: str = 'architecture', 
                        config_file: str = 'backend/utils/design_rules.json') -> str:
    """Generate enhanced SVG diagram."""
    generator = EnhancedSVGGenerator(config_file)
    return generator.generate_diagram_svg(data, output)