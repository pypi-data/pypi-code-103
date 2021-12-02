import neo4j
from neo4j import GraphDatabase


class LabelGraphDB(object):

    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def run(self, command, parameters=None):
        with self.driver.session(default_access_mode=neo4j.WRITE_ACCESS) as session:
            result = session.run(command, parameters)
            return list(result)

    def clear_graph(self):
        self.run('MATCH (n) DETACH DELETE n')

    # def create_nodes_and_relations(self, pairs):
    #     query = '''
    #         UNWIND $pairs AS row
    #         WITH row.first as prev, row.second as next, row.relation as rel
    #         MERGE (r1:Region {task: prev.task, start: prev.start, end: prev.end, label: prev.label, text: prev.text, type: prev.type})
    #         MERGE (r2:Region {task: next.task, start: next.start, end: next.end, label: next.label, text: next.text, type: next.type})
    #         MERGE (r1)-[:rel]->(r2)
    #         RETURN count(*) as total
    #     '''
    #     return self.run(query, parameters={'pairs': pairs})

    def create_nodes_and_relations(self, pairs):
        query = '''
            UNWIND $pairs as p
            CREATE (x:Region)-[r:p.relation]->(y:Region)
            SET r1 = p.first.values
            SET r2 = p.second.values
            RETURN x,r,y
        '''
        return self.run(query, parameters={'pairs': pairs})

    def close(self):
        self.driver.close()

    def _safe_int(self, i):
        return int(i) if i is not None else -1

    def _convert(self, result, task):
        return {
            "id": result['id'],
            "task": task,
            "label": result["value"][result["type"]][0],
            "start": self._safe_int(result["value"].get("start")),
            "end": self._safe_int(result["value"].get("end")),
            "text": result["value"].get("text", "null"),
            "type": result["from_name"]
        }

    def build_graph(self, predictions):
        # create ID map
        pairs = []
        for prediction in predictions:
            results = prediction['result']
            regions = {r['id']: self._convert(r, prediction["task"]) for r in results if 'id' in r}
            relations = [(r['from_id'], r['to_id']) for r in results if r['type'] == 'relation']
            for from_id, to_id in relations:
                pairs.append({
                    'first': regions[from_id],
                    'second': regions[to_id],
                    'relation': 'next'
                })
        count = self.create_nodes_and_relations(pairs)
        print(f'{count} nodes created.')


class LabelGraph(object):

    def query(self, command, parameters):
        db = LabelGraphDB('bolt://localhost:7687', 'neo4j', 'password')
        print(command, parameters)
        result = db.run(command, parameters)
        db.close()
        return result

    def build_graph(self, predictions):
        db = LabelGraphDB('bolt://localhost:7687', 'neo4j', 'password')
        db.clear_graph()
        db.build_graph(predictions)
        db.close()
