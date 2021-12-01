from herre.wards.graphql import ParsedQuery

GET_GRAPH = ParsedQuery("""
    query GetGraph($id: ID, $template: ID){
        graph(id: $id, template: $template){
            diagram
            name
        }
        }
""")