import json
import os
import matplotlib.pyplot as plt
import networkx as nx

# Load the AST from the existing parser_output.json
def load_ast_from_file(file_path="backend/main_compiler/parser_module/parser_output.json"):
    """Load the AST from the given JSON file."""
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            return json.load(f)
    else:
        print(f"Error: File {file_path} not found.")
        return None

# Function to generate the visual representation of the AST
def generate_ast_image(ast, output_path="backend/main_compiler/parser_module/visual_ast.png"):
    """Generate a visual representation of the AST and save as an image."""
    if ast is None:
        print("AST is empty, cannot generate image.")
        return
    
    # Use networkx to create a graph
    G = nx.DiGraph()  # Directed graph for AST

    # Recursive function to traverse the AST and add nodes/edges
    def add_nodes_and_edges(node, parent=None, node_id=None):
        if not isinstance(node, dict):
            return

        # Create a unique identifier for this node
        if node_id is None:
            node_id = len(G.nodes())
        
        # Get meaningful node information
        node_type = node.get("type", "Unknown")
        node_value = ""
        
        # Try to get value or name if available
        if "value" in node:
            node_value = f": {node['value']}"
        elif "name" in node:
            node_value = f": {node['name']}"
            
        node_label = f"{node_type}{node_value}"
        node_name = f"{node_id}"

        # Add node to the graph
        G.add_node(node_name, label=node_label)

        if parent is not None:
            G.add_edge(parent, node_name)  # Add edge between parent and current node

        # Traverse children nodes if present
        child_id = len(G.nodes())
        for key, value in node.items():
            # Skip non-structural properties
            if key in ["type", "value", "name", "position"]:
                continue
                
            if isinstance(value, dict):  # If it's another node
                add_nodes_and_edges(value, node_name, child_id)
                child_id += 1
            elif isinstance(value, list):  # If it's a list of nodes
                for child in value:
                    if isinstance(child, dict):
                        add_nodes_and_edges(child, node_name, child_id)
                        child_id += 1

    # Start from the root of the AST
    add_nodes_and_edges(ast)

    if not G.nodes():
        print("No nodes were created. Check if the AST structure is as expected.")
        return

    # Draw the graph - use a basic layout instead of graphviz
    plt.figure(figsize=(16, 12))
    
    # Try different layout algorithms that work well for trees
    try:
        pos = nx.nx_pydot.pydot_layout(G, prog='dot')  # Try pydot first
    except:
        try:
            pos = nx.drawing.nx_pydot.graphviz_layout(G, prog='dot')  # Try another option
        except:
            # Fall back to basic layouts if others fail
            try:
                pos = nx.drawing.layout.kamada_kawai_layout(G)
            except:
                pos = nx.spring_layout(G, k=0.9, iterations=50)  # Basic spring layout as fallback
    
    # Get labels from node attributes
    labels = nx.get_node_attributes(G, 'label')
    
    # Draw nodes and edges
    nx.draw(G, pos, with_labels=True, labels=labels, 
            node_size=3000, node_color='lightblue', 
            font_size=10, font_weight='bold',
            arrows=True, arrowsize=20,
            edge_color='gray')
    
    plt.title("Abstract Syntax Tree Visualization")
    
    # Save the plot to the specified file
    plt.savefig(output_path, format="PNG", dpi=300)
    print(f"AST visualization saved to {output_path}")

def main():
    # Load AST from parser_output.json
    ast = load_ast_from_file()

    # If AST is successfully loaded, generate and save the image
    if ast:
        generate_ast_image(ast)

if __name__ == "__main__":
    main()