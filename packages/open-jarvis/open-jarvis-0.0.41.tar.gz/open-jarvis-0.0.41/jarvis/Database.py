#
# Copyright (c) 2020 by Philipp Scheer. All Rights Reserved.
#

import types
import couchdb2
import requests
import traceback


class Database:
    Exception = requests.ConnectionError

    def __init__(self, username: str = "jarvis", password: str = "jarvis", name: str = "jarvis", hostname: str = "127.0.0.1", port: int = 5984) -> None:
        self.host = hostname
        self.port = port
        self.user = username
        self.name = name

        try:
            self.server = couchdb2.Server(
                f"http://{self.host}:{self.port}/", username=self.user, password=password)
        except Database.Exception:
            from jarvis import Logger
            Logger.Logger.e1("database", "refused",
                             "connection refused, database not running", traceback.format_exc(), database_entry=False)
            exit(1)

    def table(self, table_name: str, pure: bool = False):
        # A database is also a table in couchdb, so we make a trick:
        #   prefix all tables with a given database name
        return Table(self.server, table_name if pure else f"{self.name}-{table_name}")

    def delete(self):
        for db in self.server:
            if str(db).startswith(f"{self.name}-"):
                db.destroy()

    def drop(self):
        return self.delete()

    @property
    def up(self):
        return self.server.up()


class Table:
    def __init__(self, server: couchdb2.Server, table_name: str) -> None:
        self.server = server
        self.name = table_name
        if self.name in self.server:
            self.table = self.server.get(self.name)
        else:
            self.table = self.server.create(self.name)

    def get(self, id: str) -> dict:
        return self.table.get(id)

    def all(self) -> list:
        all_list = DocumentList(self)
        for doc in self.table:
            all_list.add(dict(doc))
        return all_list

    def insert(self, document: dict) -> any:
        return self.table.put(document)

    def filter(self, filter: any = {}) -> list:
        """
        Filters a table
        `filter` can be either a lamba or object
        """
        doc_list = DocumentList(self)
        if (isinstance(filter, types.LambdaType)):
            for document in self.all():
                if filter.__call__(document):
                    doc_list.add(document)
        if (isinstance(filter, dict)):
            if len(filter) == 0:
                return self.all()
            for document in self.all():
                for key in filter:
                    if key in document and document[key] == filter[key]:
                        doc_list.add(document)
        return doc_list

    def delete(self, document):
        self.table.purge([document])

    def drop(self):
        return self.table.destroy()


class DocumentList:
    def __init__(self, table: Table) -> None:
        self.table = table
        self.document_list = []

    def add(self, item: dict) -> None:
        self.document_list.append(item)

    def set(self, new_document: dict) -> None:
        for document in self.document_list:
            if "_id" not in new_document:
                new_document["_id"] = document["_id"]
                new_document["_rev"] = document["_rev"]
            self.table.insert(new_document)

    def update(self, new_document: dict) -> None:
        for document in self.document_list:
            def merge_dicts(x, y):
                z = x.copy()
                z.update(y)
                return z
            self.table.insert(merge_dicts(document, new_document))

    def delete(self) -> None:
        for document in self.document_list:
            self.table.delete(document)

    @property
    def found(self):
        return len(self.document_list) != 0

    def __getitem__(self, key: int):
        return self.document_list[key]

    def __list__(self):
        return self.document_list
