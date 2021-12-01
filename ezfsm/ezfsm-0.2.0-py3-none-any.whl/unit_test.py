from ezfsm import *    # This step is best to import all

tfs = [
    ["a", "b", lambda: True, lambda: print("a -> b")]
]

sm = StateMachine(tfs)    # You can also use SM instead of Statemachine

sm.Build()    # compile


#  Ususally, other general FSM does not need to be compiled
#  But this step is set to standardize the data format and improve efficiency. It can make writing more convenient
#  Statemachine without compilation cannot execute most operations.


while not sm.IsFinish(): sm.Execute()    # You can also use sm() instead of sm.Execute()

# if you want to view the graph, you must pip install graphviz and download the graphviz software.

graph = sm.StateGraph()    # get the graphviz.Digraph object
graph.view()