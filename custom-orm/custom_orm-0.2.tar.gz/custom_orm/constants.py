SELECT_QUERY = "SELECT {name} FROM {table} WHERE {p_key} = ?;"
UPDATE_QUERY = "UPDATE {table} SET {name} = ? WHERE {p_key} = ?;"
INSERT_QUERY = "INSERT INTO {table} ({keys}) VALUES ({values});"
DELETE_QUERY = "DELETE FROM {table} WHERE {p_key} = ?;"
