import os
import re
import csv
import sys
import json
import yaml
import time
import socket
import connexion
import postgresql as psql

from flask import current_app
from urllib.parse import urlencode
from hashlib import md5
from bokeh.embed import server_document
from .processes import fetch_process, is_running, process_info
from .utils import column_filter

float_pattern = re.compile(r'^\d*\.\d+$')
int_pattern = re.compile(r'^-?\d+$')
NA_pattern = re.compile(r'^NA$')
queryfilters = re.compile(r'(.+)(<=?|>=?|!=|==)(.+)')

def init_column_mapping(row, schema):
    """Generate initial estimates of column data types"""
    defs = {column_filter(col): 'text' for col in row}
    # Apply predefined table schema
    defs.update({k: v for (k, v) in schema.items() if k in defs})
    for (col, val) in row.items():
        col = column_filter(col)
        if col not in schema:
            if int_pattern.match(val):
                try:
                    int(val)
                    print("Assigning int to", col, "based on", val)
                    defs[col] = 'integer'
                except ValueError:
                    print("ERROR: Int mismatch:", val)
            elif float_pattern.match(val):
                try:
                    float(val)
                    print("Assigning float to", col, "based on", val)
                    defs[col] = 'decimal'
                except ValueError:
                    print("ERROR: Float mismatch:", val)
    mapping = {}
    for (col, val) in defs.items():
        if 'int' in val:
            mapping[col] = int
        elif val == 'decimal':
            mapping[col] = float
        else:
            mapping[col] = str
    return (mapping, defs)


def column_mapping(row, mapping, schema):
    """Apply filtering to the current row.
    Detect if column data types need to be changed"""
    output = {}
    changes = {}
    for (col, val) in row.items():
        col = column_filter(col)
        if val == None or NA_pattern.match(str(val)):
            output[col] = None
            continue
        if col not in schema and mapping[col] == str:
            if int_pattern.match(val):
                try:
                    int(val)
                    print("Assigning int to", col, "based on", val)
                    mapping[col] = int
                    changes[col] = int
                except ValueError:
                    print("ERROR: Int mismatch:", val)
            elif float_pattern.match(val):
                try:
                    float(val)
                    print("Assigning float to", col, "based on", val)
                    mapping[col] = float
                    changes[col] = float
                except ValueError:
                    print("ERROR: Float mismatch:", val)
        try:
            output[col] = mapping[col](val)
        except ValueError:
            output[col] = None
    return (mapping, output, changes)

def old_file_read(db, CREATE_TABLE, tablekey, column_names, reader, mapping):
    with db.xact():
        db.execute(CREATE_TABLE)
        # table marked for insertion during original attempt, so don't need to here
        # prepare the insertion query
        insert = db.prepare("INSERT INTO %s (%s) VALUES (%s)" % (
            tablekey,
            ','.join(column_names),
            ','.join('$%d' % i for (_, i) in zip(
                column_names, range(1, sys.maxsize)
            ))
        ))
        update = "ALTER TABLE %s " % tablekey
        for row in reader:
            # process each row
            # We format the data in the row and update column data types, if
            # necessary
            (mapping, formatted, changes) = column_mapping(row, mapping, current_app.config['schema'])
            if len(changes):
                #Generate a query to alter the table schema, if any changes are required
                alter_cols = []
                for (k, v) in changes.items():
                    # if there were any changes to the data type, update the table
                    # since we only ever update a text column to int/decimal, then
                    # it's okay to nullify the data
                    typ = ''
                    if v == int:
                        typ = 'bigint' if k in {'start', 'stop'} else 'integer'
                    elif v == float:
                        typ = 'decimal'
                    alter_cols.append(
                        "ALTER COLUMN %s SET DATA TYPE %s USING %s::%s" % (
                            k, typ, k, typ
                        )
                    )
                # Re-generate the insert statement since the data types changed
                print("Alter:", update + ','.join(alter_cols))
                db.execute(update + ','.join(alter_cols))
                insert = db.prepare("INSERT INTO %s (%s) VALUES (%s)" % (
                    tablekey,
                    ','.join(column_names),
                    ','.join('$%d' % i for (_, i) in zip(
                        column_names, range(1, sys.maxsize)
                    ))
                ))
            # insert the row
            insert(*[formatted[column] for column in column_names])

def table_transaction(file_permissions, db, CREATE_TABLE, tablekey, all_tablecolumns, raw_reader, column_names, mapping):
    with db.xact():
        db.execute(CREATE_TABLE)
        db.prepare("LOCK TABLE %s IN ACCESS EXCLUSIVE MODE" % (tablekey))
        copy_query = "COPY %s (%s) FROM '%s' WITH FREEZE NULL 'NA' DELIMITER E'\t' CSV HEADER" % (tablekey, all_tablecolumns, raw_reader.name)
        #copy_query may result in psql.exceptions.InsufficientPrivilegeError when run; workaround attempted below
        if file_permissions:
            #mark the table for deletion when the server shuts down
            #don't need to mark table for deletion during second attempt
            if 'db-clean' not in current_app.config:
                current_app.config['db-clean'] = [tablekey]
            else:
                current_app.config['db-clean'].append(tablekey)
            #attempt file copy
            db.execute(copy_query)
        else:
            import subprocess
            filedest = "/tmp/"+os.path.basename(raw_reader.name)
            subprocess.run(["mktemp", filedest], stdout=subprocess.DEVNULL)
            subprocess.run(["cp", raw_reader.name, filedest])
            subprocess.run(["chmod", "666", filedest])
            copy_query = "COPY %s (%s) FROM '%s' WITH FREEZE NULL 'NA' DELIMITER E'\t' CSV HEADER" % (tablekey, all_tablecolumns, filedest)
            try:
                db.execute(copy_query)
                print("...Success")
            finally:
                subprocess.run(["rm", filedest])
        col_val_query = "SELECT "
        for col_name in column_names:
            col_val_query += "(select %s from %s where %s is not null limit 1), "%(col_name, tablekey, col_name)
        col_val_query = col_val_query[:-2]
        col_values = db.prepare(col_val_query)
        values = col_values()[0]
        update = "ALTER TABLE %s " % tablekey
        row = dict(zip(col_values.column_names, values))
        (mapping, formatted, changes) = column_mapping(row, mapping, current_app.config['schema'])
        if len(changes):
        #Generate a query to alter the table schema, if any changes are required
            alter_cols = []
            for (k, v) in changes.items():
                # if there were any changes to the data type, update the table
                # since we only ever update a text column to int/decimal, then
                # it's okay to nullify the data
                typ = ''
                if v == int:
                    typ = 'bigint' if k in {'start', 'stop'} else 'integer'
                elif v == float:
                    typ = 'decimal'
                alter_cols.append(
                    "ALTER COLUMN %s SET DATA TYPE %s USING %s::%s" % (
                        k, typ, k, typ
                    )
                )
            print("Alter:", update + ','.join(alter_cols))
            db.execute(update + ','.join(alter_cols))

def create_table(parentID, fileID, data, tablekey, db):
    # Open a reader to cache the file in the database
    if parentID != -1:
        process = fetch_process(parentID, data, current_app.config['storage']['children'])
        if not process[0]:
            return (
                {
                    "code": 400,
                    "message": "The requested process (%d) does not exist" % parentID,
                    "fields": "parentID"
                }, 400
            )
        if is_running(process):
            return (
                {
                    "code": 400,
                    "message": "The requested process (%d) is still running" % parentID,
                    "fields": "parentID"
                }, 400
            )
        if str(fileID) not in process[0]['files']:
            return (
                {
                    "code": 400,
                    "message": "The requested fileID (%s) does not exist for this process (%d)" % (fileID, parentID),
                    "fields": "fileID"
                }, 400
            )
        raw_reader = open(process[0]['files'][fileID]['fullname'])
    else:
        if str(fileID) not in data['visualize']:
            return (
                {
                    "code": 400,
                    "message": "The requested fileID (%s) does not exist in the visualize" % fileID,
                    "fields": "fileID"
                }, 400
            )
        raw_reader = open(data['visualize'][str(fileID)]['fullname'])
    if not raw_reader.name.endswith('.tsv'):
        ext = os.path.splitext(raw_reader.name)[1].lower()
        if len(ext) and ext[0] == '.':
            ext = ext[1:]
        return serve_as(raw_reader, ext)
    reader = csv.DictReader(raw_reader, delimiter='\t')

    tmp_reader = open(raw_reader.name)
    tmp = csv.DictReader(tmp_reader, delimiter='\t')
    try:
        init = next(tmp)
    except StopIteration:
        return []
    tmp_reader.close()

    # Get an initial estimate of column datatypes from the first row
    (mapping, column_names) = init_column_mapping(init, current_app.config['schema'])
    tablecolumns = "\n".join(  # use the estimated types to create the table
        "%s %s," % (colname, column_names[colname])
        for colname in column_names
    )[:-1]
    CREATE_TABLE = "CREATE TABLE %s (\
        rowid SERIAL PRIMARY KEY NOT NULL,\
        %s\
    )" % (tablekey, tablecolumns)
    all_tablecolumns = ', '.join(column_filter(col) for col in reader.fieldnames)
    try:
        table_transaction(True, db, CREATE_TABLE, tablekey, all_tablecolumns, raw_reader, column_names, mapping)
    except psql.exceptions.UniqueError: #If another transaction already created specified table, pass
        pass
    except psql.exceptions.InsufficientPrivilegeError as e:
        #can occur when postgres user unable to open file due to permissions; specifically for travis-ci tests
        #check if resulting from postgres user permissions
        if e.args[0].startswith("must be superuser"):
            print("WARNING: Postgres user is not a super user; visualization time may be slow")
            old_file_read(db, CREATE_TABLE, tablekey, column_names, reader, mapping) #use inefficient file-read-to-db method
        else:
            #attempt to resolve by copying file to /tmp/, changing its permissions, and accessing it there
            try:
                print("InsufficientPrivilegeError raised in accessing file.\nAttempting workaround...")
                table_transaction(False, db, CREATE_TABLE, tablekey, all_tablecolumns, raw_reader, column_names, mapping)
            except psql.exceptions.InsufficientPrivilegeError:
                print("Postgres could not access file.  Check to make sure that both the "
                    "file and your current postgres user has the appropriate permissions.")
                raise
    raw_reader.close()

def filterfile(parentID, fileID, count, page, filters, sort, direction):
    """Gets the file ID belonging to the parent.\
    For result files, the parentID is the process ID that spawned them.\
    For visualize files, the parentID is -1"""
    data = current_app.config['storage']['loader']()

    # first, generate the key
    tablekey = "data_%s_%s" % (
        (parentID if parentID >= 0 else 'visualize'),
        fileID
    )

    # check if the table exists:
    db = psql.open("localhost/pvacseq")
    fileID = str(fileID)
    with db.xact():
        query = db.prepare("SELECT 1 FROM information_schema.tables WHERE table_name = $1")
        response = query(tablekey)
    if not len(response):  # table does not exist
        table_errors = create_table(parentID, fileID, data, tablekey, db)
        if table_errors != None:
            return table_errors
    #with db.synchronizer:
    #    test_query = db.prepare("SELECT 1 FROM information_schema.tables WHERE table_name = $1")
    #    test_response = query(tablekey)
    with db.xact():
        typequery = db.prepare(
            "SELECT column_name, data_type FROM information_schema.columns WHERE table_name = $1"
        )
        column_defs = typequery(tablekey)
        column_maps = {}
        for (col, typ) in column_defs:
            if 'int' in typ:
                column_maps[col] = int
            elif typ == 'numeric'or typ == 'decimal':
                column_maps[col] = float
            else:
                column_maps[col] = str
    formatted_filters = []
    for i in range(len(filters)):
        f = filters[i].strip()
        if not len(f):
            continue
        result = queryfilters.match(f)
        if not result:
            return ({
                "code": 400,
                "message": "Encountered an invalid filter (%s)" % f,
                "fields": "filters"
            }, 400)
        colname = column_filter(result.group(1))
        if colname not in column_maps:
            return ({
                "code": 400,
                "message": "Unknown column name %s" % result.group(1),
                "fields": "filters"
            }, 400)
        op = result.group(2)
        typ = column_maps[colname]
        val = None
        try:
            val = column_maps[colname](
                result.group(3)
            )
        except ValueError:
            return ({
                "code": 400,
                "message": "Value %s cannot be formatted to match the type of column %s (%s)" % (
                    result.group(3),
                    result.group(1),
                    typ
                )
            }, 400)
        if typ == str and (op in {'==', '!='}):
            formatted_filters.append(
                json.dumps(colname) + (' not ' if '!' in op else ' ') + "LIKE '%s'" % (
                    json.dumps(val)[1:-1]
                )
            )
        else:  # type is numerical
            op = op.replace('==', '=')
            formatted_filters.append(
                '%s %s %s' % (
                    json.dumps(colname),
                    op,
                    json.dumps(val)
                )
            )
    raw_query = "SELECT %s FROM %s" % (
        ','.join([k[0] for k in column_defs]),
        tablekey
    )
    if len(formatted_filters):
        raw_query += " WHERE " + " AND ".join(formatted_filters)
    if sort:
        if column_filter(sort) not in column_maps:
            return ({
                'code': 400,
                'message': 'Invalid column name %s' % sort,
                'fields': 'sort'
            }, 400)
        raw_query += " ORDER BY %s" % (column_filter(sort))
        if direction:
            raw_query += " " + direction
    if count:
        raw_query += " LIMIT %d" % count
    if page:
        raw_query += " OFFSET %d" % (page * count)
    print("Query:", raw_query)
    import decimal
    with db.xact('SERIALIZABLE', 'READ ONLY DEFERRABLE'):
        query = db.prepare(raw_query)
        decimalizer = lambda x: (float(x) if type(x) == decimal.Decimal else x)
        result = [
            {
                colname: decimalizer(value) for (colname, value) in zip(
                    [k[0] for k in column_defs],
                    [val for val in row]
                )
            } for row in query.rows()
        ]
    db.close()
    return result


def fileschema(parentID, fileID):
    data = current_app.config['storage']['loader']()
    tablekey = "data_%s_%s" % (
        (parentID if parentID >= 0 else 'visualize'),
        fileID
    )

    # check if the table exists:
    db = psql.open("localhost/pvacseq")
    with db.xact():
        query = db.prepare("SELECT 1 FROM information_schema.tables WHERE table_name = $1")
        if not len(query(tablekey)):  # table does not exist
            return ({
                'code': 400,
                'message': "The requested file has not been loaded into the Postgres database",
                'fields': "fileID"
            }, 400)
        typequery = db.prepare("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = $1")
        result = {
            key: val for (key, val) in typequery(tablekey)
        }
    db.close()
    return result

def serve_as(reader, filetype):
    if filetype == 'json':
        return {
            'filetype':'json',
            'content':json.load(reader)
        }
    elif filetype == 'yaml' or filetype == 'yml':
        return {
            'filetype':'yaml',
            'content':yaml.load(reader.read())
        }
    elif filetype == 'log':
        return {
            'filetype':'log',
            'content':[line.rstrip() for line in reader.readlines()]
        }
    else:
        return {
            'filetype':'raw',
            'content':reader.read()
        }

def visualize(parentID, fileID):
    vis = visualize_script(parentID, fileID)
    return '<html><head></head><body>%s</body></html'%(vis if type(vis)!=tuple else vis[0])

def visualize_script(parentID, fileID):
    """Return an HTML document containing the requested table visualization"""
    from .files import results_getcols
    data = current_app.config['storage']['loader']()
    #first call filterfile to load the table if it's not loaded already
    result = filterfile(parentID, fileID, 1, 0, '', 'rowid', 'ASC')
    if type(result) != list:
        return (
            {
                'code':400,
                'message':json.dumps(result),
                'fields':'unknown',
            },
            400
        )
    if len(result) == 0 or type(result) == dict:
        return (
            'Results file contains no data - cannot visualize'
        )
    cols = results_getcols(parentID, fileID)
    if type(cols) != dict:
        return (
            {
                'code':400,
                'message':json.dumps(cols),
                'fields':'unknown'
            },
            400
        )

    proc_data = process_info(parentID)

    if type(proc_data)==dict and 'parameters' in proc_data and 'sample_name' in proc_data['parameters']:
        sample = proc_data['parameters']['sample_name']
    elif parentID == -1:
        sample = data['visualize'][str(fileID)]['display_name'].rsplit(".", 1)[0]
    else:
        sample = 'Unknown Sample'

    if current_app.PROXY_IP_ADDRESS is not None:
        IP = current_app.PROXY_IP_ADDRESS
    else:
        IP = current_app.IP_ADDRESS

    return (
        server_document(
            url="http://" + IP + ":5006/visualizations",
            arguments={
                'target-process': parentID,
                'target-file': fileID,
                'cols': json.dumps(cols),
                'samplename': sample
            }
        )
    )
