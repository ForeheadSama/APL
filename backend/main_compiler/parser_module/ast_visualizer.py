import json
import os

import matplotlib
matplotlib.use('Agg')  # SET THE BACKEND TO AGG TO ENABLE IMAGE GENERATION WITHOUT GUI
import matplotlib.pyplot as plt

import networkx as nx  # IMPORT NETWORKX FOR GRAPH REPRESENTATION

# FUNCTION TO LOAD THE ABSTRACT SYNTAX TREE (AST) FROM A JSON FILE
def load_ast_from_file(file_path="backend/main_compiler/parser_module/parser_output.json"):
    """LOAD THE AST FROM THE GIVEN JSON FILE."""
    if os.path.exists(file_path):  # CHECK IF FILE EXISTS
        with open(file_path, "r") as f:
            return json.load(f)  # LOAD JSON CONTENT AS A PYTHON DICTIONARY
    else:
        print(f"Error: File {file_path} not found.")
        return None

# FUNCTION TO GENERATE A VISUAL REPRESENTATION OF THE AST
def generate_ast_image(ast, output_path="backend/main_compiler/parser_module/visual_ast.png"):
    """GENERATE A VISUAL REPRESENTATION OF THE AST AND SAVE AS AN IMAGE."""
    if ast is None:
        print("AST is empty, cannot generate image.")
        return
    
    # CREATE A DIRECTED GRAPH FOR THE AST
    G = nx.DiGraph()

    # RECURSIVE FUNCTION TO ADD NODES AND EDGES TO THE GRAPH
    def add_nodes_and_edges(node, parent=None, node_id=None):
        if not isinstance(node, dict):  # ENSURE NODE IS A DICTIONARY
            return

        # CREATE A UNIQUE IDENTIFIER FOR THIS NODE
        if node_id is None:
            node_id = len(G.nodes())
        
        # EXTRACT MEANINGFUL INFORMATION FROM THE NODE
        node_type = node.get("type", "Unknown")
        node_value = ""
        
        # RETRIEVE VALUE OR NAME IF AVAILABLE
        if "value" in node:
            node_value = f": {node['value']}"
        elif "name" in node:
            node_value = f": {node['name']}"
            
        node_label = f"{node_type}{node_value}"
        node_name = f"{node_id}"

        # ADD NODE TO THE GRAPH
        G.add_node(node_name, label=node_label)

        if parent is not None:
            G.add_edge(parent, node_name)  # CONNECT THE NODE TO ITS PARENT

        # TRAVERSE CHILD NODES IF PRESENT
        child_id = len(G.nodes())
        for key, value in node.items():
            # IGNORE NON-STRUCTURAL PROPERTIES
            if key in ["type", "value", "name", "position"]:
                continue
                
            if isinstance(value, dict):  # IF CHILD IS A DICTIONARY, RECURSE
                add_nodes_and_edges(value, node_name, child_id)
                child_id += 1
            elif isinstance(value, list):  # IF CHILD IS A LIST, PROCESS EACH ITEM
                for child in value:
                    if isinstance(child, dict):
                        add_nodes_and_edges(child, node_name, child_id)
                        child_id += 1

    # START BUILDING GRAPH FROM THE ROOT NODE
    add_nodes_and_edges(ast)

    if not G.nodes():
        print("No nodes were created. Check if the AST structure is as expected.")
        return

    # CREATE FIGURE FOR GRAPH VISUALIZATION
    plt.figure(figsize=(16, 12))
    
    # ATTEMPT TO USE DIFFERENT GRAPH LAYOUTS
    try:
        pos = nx.nx_pydot.pydot_layout(G, prog='dot')  # TRY PYDOT LAYOUT
    except:
        try:
            pos = nx.drawing.nx_pydot.graphviz_layout(G, prog='dot')  # FALLBACK TO GRAPHVIZ
        except:
            try:
                pos = nx.drawing.layout.kamada_kawai_layout(G)  # USE KAMADA-KAWAI LAYOUT
            except:
                pos = nx.spring_layout(G, k=0.9, iterations=50)  # USE SPRING LAYOUT AS LAST RESORT
    
    # EXTRACT LABELS FOR EACH NODE
    labels = nx.get_node_attributes(G, 'label')
    
    # DRAW GRAPH NODES AND EDGES
    nx.draw(G, pos, with_labels=True, labels=labels, 
            node_size=3000, node_color='lightblue', 
            font_size=10, font_weight='bold',
            arrows=True, arrowsize=20,
            edge_color='gray')
    
    plt.title("Abstract Syntax Tree Visualization")
    
    # SAVE THE GENERATED GRAPH AS AN IMAGE
    plt.savefig(output_path, format="PNG", dpi=300)
    print(f"AST visualization saved to {output_path}")

# MAIN FUNCTION TO LOAD THE AST AND GENERATE ITS VISUAL REPRESENTATION
def main():
    
    # LOAD AST FROM FILE
    ast = load_ast_from_file()

    # IF AST IS VALID, GENERATE AND SAVE ITS IMAGE
    if ast:
        generate_ast_image(ast)

# ENTRY POINT FOR THE SCRIPT
if __name__ == "__main__":
    main()
