import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.GraphExecutorStatic import logging, State, GraphBuilder, GraphExecutor, ProcessingNode, AggregatorNode, GraphExecutionError, routing_function

def node1_func(state: State) -> State:
    state.data["node1"] = "processed"
    return state

def node2_func(state: State) -> State:
    state.data["node2"] = "processed"
    return state

def node3_func(state: State) -> State:
    logging.info("node3_func: Processing state...")
    state.data["node3"] = "processed"
    logging.info("node3_func: State processed.")
    return state

def node4_func(state: State) -> State:
    logging.info("node4_func: Processing state...")
    state.data["node4"] = "processed"
    # Decide next route based on state. Default to "end" if not specified.
    next_route = state.data.get("route", "end")
    state.data["next"] = next_route
    logging.info(f"node4_func: State processed. Next route set to '{next_route}'.")
    return state

# Routing function: returns the node id as a string.
@routing_function
def route1(state: State) -> str:
    return state.data.get("next", "end")

def main() -> None:
    logging.info("Starting main function to build and execute graph...")
    builder = GraphBuilder()

    # Create aggregator nodes.
    aggregator1 = AggregatorNode("aggregator1")
    aggregator2 = AggregatorNode("aggregator2")
    builder.add_aggregator(aggregator1)
    builder.add_aggregator(aggregator2)

    # Create additional processing nodes.
    node1 = ProcessingNode("node1", node1_func)
    node2 = ProcessingNode("node2", node2_func)
    node3 = ProcessingNode("node3", node3_func)
    node4 = ProcessingNode("node4", node4_func)

    # Add processing nodes.
    builder.add_node(node1)
    builder.add_node(node2)
    builder.add_node(node3)
    builder.add_node(node4)

    # Construct graph edges:
    # start -> aggregator1
    builder.add_concrete_edge("start", "aggregator1")
    # aggregator1 -> node1
    builder.add_concrete_edge("aggregator1", "node1")
    # node1 -> node2 and node1 -> node3
    builder.add_concrete_edge("node1", "node2")
    builder.add_concrete_edge("node1", "node3")
    # node2 -> aggregator2 and node3 -> aggregator2
    builder.add_concrete_edge("node2", "aggregator2")
    builder.add_concrete_edge("node3", "aggregator2")
    # aggregator2 -> node4
    builder.add_concrete_edge("aggregator2", "node4")
    # node4 -> {aggregator1, end} via a conditional edge.
    builder.add_conditional_edge("node4", ["aggregator1", "end"], route1)

    # Validate and build the graph.
    graph = builder.build_graph()

    # Define an initial state.
    initial_state = State(data={"route": "end"})  # Change "route" to "aggregator1" to loop back.

    # Create and run the GraphExecutor.
    executor = GraphExecutor(graph, initial_state, max_workers=4)
    try:
        final_state = executor.execute()
        logging.info(f"Final state after graph execution: {final_state}")
    except GraphExecutionError as e:
        logging.error(f"Graph execution failed: {e}")

if __name__ == "__main__":
    main()
