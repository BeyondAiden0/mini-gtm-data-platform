import re

import duckdb


# protect the SQL query from reserved keywords.
def quoteIdent(name: str) -> str:
    return '"' + name.replace('"', '""') + '"'

# builds the SQL table reference
def tableSql(schema: str, table: str) -> str:
    return f"{quoteIdent(schema)}.{quoteIdent(table)}"

# determine if the user input is an email, id, or name
def classifyInput(userInput: str) -> str:
    userInput = userInput.strip()

    if "@" in userInput:
        return "email"
    if re.fullmatch(r"\d+", userInput):
        return "id"
    return "name"

# fetch schema details from DuckDB for only the schemas we want to search
def discoverColumns(conn: duckdb.DuckDBPyConnection, schemas: str) -> list[dict]:

    rows = conn.execute(
        f"""
        select table_schema, table_name, column_name, data_type
        from information_schema.columns
        where table_schema in ?
        order by table_schema, table_name, ordinal_position
        """,
        [schemas],
    ).fetchall()

    columns = []
    for schema, table, column, dataType in rows:
        columns.append(
            {
                "schema": schema,
                "table": table,
                "column": column,
                "dataType": dataType,
                "fullTable": f"{schema}.{table}",
            }
        )
    return columns

# finds the full column list to one specific table that is needed
def getTableColumns(columns: list[dict], schema: str, table: str) -> list[dict]:
    res = []

    for col in columns:
        if col["schema"] == schema and col["table"] == table:
            res.append(col)
    return res

# give a meaning to a column based on its name, part of the dynamic schema discovery
def getColumnRole(column: dict) -> str | None:
    columnName = column["column"].lower()
    tableName = column["table"].lower()

    if "email" in columnName:
        return "email"
    if columnName in {"account_id", "converted_account_id"}:
        return "accountId"
    if columnName.endswith("_id") and any(word in columnName for word in ["account", "contact", "lead", "opp"]):
        return "id"
    if columnName in {"account_name", "company"}:
        return "accountName"
    if columnName == "name" and "account" in tableName:
        return "accountName"
    if columnName in {"first_name", "last_name"}:
        return "personName"
    if columnName in {"opp_name", "opportunity_name"}:
        return "opportunityName"

    return None

# get matching rows, if its email or id, try to get the exact match. Otherwise, fuzzy match
def getMatchingRows(
    conn: duckdb.DuckDBPyConnection,
    column: dict,
    columns: list[dict],
    value: str,
    inputType: str,
) -> list[dict]:
    tableColumns = getTableColumns(columns, column["schema"], column["table"])
    selectColumns = [col["column"] for col in tableColumns]
    searches = ", ".join(quoteIdent(col) for col in selectColumns)

    if inputType in {"email", "id"}:
        operator = "="
        searchValue = value.lower()
    else:
        operator = "like"
        searchValue = f"%{value.lower()}%"

    rows = conn.execute(
        f"""
        select {searches}
        from {tableSql(column["schema"], column["table"])}
        where lower(cast({quoteIdent(column["column"])} as varchar)) {operator} ?
        order by
            case when lower(cast({quoteIdent(column["column"])} as varchar)) = ? then 0 else 1 end
        limit 10
        """,
        [searchValue, value.lower()],
    ).fetchall()

    return [dict(zip(selectColumns, row)) for row in rows]

# look up the actual account records from the schema
def getAccountById(conn: duckdb.DuckDBPyConnection, accountId: int) -> dict | None:
    row = conn.execute(
        f"""
        select account_id, name
        from marts.dim_accounts
        where account_id = ?
        limit 1
        """,
        [accountId],
    ).fetchone()

    if not row:
        return None

    return {"accountId": row[0], "accountName": row[1]}

# turn a matched row into an account result
def resolveRowToAccount(
    conn: duckdb.DuckDBPyConnection,
    row: dict,
) -> dict | None:
    for accountKey in ["account_id", "converted_account_id"]:
        if row.get(accountKey) not in (None, ""):
            account = getAccountById(conn, row[accountKey])
            if account:
                return account

            return {
                "accountId": row[accountKey],
                "accountName": row.get("account_name") or row.get("name") or row.get("company"),
            }

    if row.get("account_name") or row.get("company"):
        return {
            "accountId": None,
            "accountName": row.get("account_name") or row.get("company"),
        }

    return None

# reformat the result into a readable label
def rowLabel(row: dict) -> str:
    labelParts = []
    for key in ["first_name", "last_name", "email", "company", "name", "account_name", "opp_name"]:
        if row.get(key) not in (None, ""):
            labelParts.append(str(row[key]))
    return ", ".join(labelParts)

# gives a matching confidence score for the result
def scoreCandidate(inputType: str, role: str, exactMatch: bool, sourceTable: str) -> int:
    score = 20 if exactMatch else 10

    if inputType == "email" and role == "email":
        score += 60
    elif inputType == "id" and role == "accountId":
        score += 60
    elif inputType == "id" and role == "id":
        score += 35
    elif inputType == "name" and role == "accountName":
        score += 55
    elif inputType == "name" and role in {"personName", "opportunityName"}:
        score += 25

    if "dim_accounts" in sourceTable.lower():
        score += 10

    return score

# create the dict of candidates and add it to the candidate list
def addCandidate(
    candidates: list[dict],
    account: dict,
    column: dict,
    row: dict,
    inputType: str,
    role: str,
    exactMatch: bool,
) -> None:
    candidates.append(
        {
            "accountId": account["accountId"],
            "accountName": account["accountName"],
            "confidence": scoreCandidate(inputType, role, exactMatch, column["fullTable"]),
            "reason": f"{'Exact' if exactMatch else 'Partial'} {role} match",
            "sourceTable": column["fullTable"],
            "sourceColumn": column["column"],
            "matchedValue": row.get(column["column"]),
            "matchedRecord": rowLabel(row),
        }
    )

# makes sure theres no duplicate account matches
def removeDuplicates(candidates: list[dict]) -> list[dict]:
    bestByAccount = {}

    for candidate in candidates:
        key = (candidate["accountId"], candidate["accountName"])
        currentBest = bestByAccount.get(key)
        if not currentBest or candidate["confidence"] > currentBest["confidence"]:
            bestByAccount[key] = candidate

    return sorted(bestByAccount.values(), key=lambda candidate: candidate["confidence"], reverse=True)

# search the schema for the user input
def searchSchemas(conn: duckdb.DuckDBPyConnection, userInput: str, schemas: str) -> list[dict]:
    value = userInput.strip()
    inputType = classifyInput(value)
    columns = discoverColumns(conn, schemas)
    candidates = []

    for column in columns:
        role = getColumnRole(column)
        if not role:
            continue

        rows = getMatchingRows(conn, column, columns, value, inputType)
        for row in rows:
            account = resolveRowToAccount(conn, row)
            if account:
                exactMatch = str(row.get(column["column"], "")).lower() == value.lower()
                addCandidate(candidates, account, column, row, inputType, role, exactMatch)

    return removeDuplicates(candidates)

# search marts if possible, otherwise staging
def findAccountCandidates(conn: duckdb.DuckDBPyConnection, userInput: str) -> list[dict]:
    candidates = searchSchemas(conn, userInput, "marts")

    if candidates:
        return candidates

    return searchSchemas(conn, userInput, "staging")

