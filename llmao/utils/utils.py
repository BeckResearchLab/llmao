import sqlite3

# Add examples questions: queries here
Queries = {
    'Look up 2 chemicals in the AOP database':'SELECT ChemicalName, ChemicalID from chemical_info LIMIT 2;',
}

# Question bank for random question button
Questions = list(Queries.keys())

# query to get all tables and columns from the AOP database
info_query = """
    SELECT m.name as tableName, 
    p.name as columnName
    FROM sqlite_master m
    left outer join pragma_table_info((m.name)) p
    on m.name <> p.name
    order by tableName, columnName
    ;
    """

# connect to db, execute query, and close connection
db_name = '//home/ubuntu/llmao/llmao/aopdb_08-25-2020.db'
sqliteConnection = sqlite3.connect(db_name)
cursor = sqliteConnection.cursor()
cursor.execute(info_query)
info_dict = cursor.fetchall()
cursor.close()
sqliteConnection.close()
AOP_Info = {}

for entry in info_dict:
    table = entry[0]
    # if the table has already been added to the AOP dictionary
    if table in AOP_Info:
        AOP_Info[table].append(entry[1])
    # else create a dictionary entry for the table
    else:
        AOP_Info[table] = [entry[1]]