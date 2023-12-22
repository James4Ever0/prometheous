import hashlib
import os
from contextlib import contextmanager
from typing import Callable

import pydantic
import tinydb
from beartype import beartype


@beartype
def read_file_bytes(filename: str):
    with open(filename, "rb") as f:
        content = f.read()
    return content


@beartype
def hash_file(filename: str):
    content = read_file_bytes(filename)
    hash_obj = hashlib.md5(content)
    ret = hash_obj.hexdigest()
    return ret


@beartype
class CacheManager:
    path = "path"
    hash = "hash"
    source = "source"
    target = "target"

    def __init__(self, db_path: str):
        self.init_db(db_path)

    def init_db(self, db_path: str):
        self.db_path = db_path
        self.db = tinydb.TinyDB(db_path)

    def init_query(self):
        self.query = tinydb.Query()
        self.source_path_query, self.source_hash_query = self.construct_query_by_key(
            self.source
        )
        self.target_path_query, self.target_hash_query = self.construct_query_by_key(
            self.target
        )

    def source_hash_eq(self, other: str):
        return self.source_hash_query == other

    def source_path_eq(self, other: str):
        return self.source_path_query == other

    def target_hash_eq(self, other: str):
        return self.target_hash_query == other

    def target_path_eq(self, other: str):
        return self.target_path_query == other

    def construct_query_by_key_and_subkey(self, key: str, subkey: str):
        key_query = getattr(self.query, key)
        subkey_query = getattr(key_query, subkey)
        return subkey_query

    def construct_query_by_key(self, key: str):
        path_query = self.construct_query_by_key_and_subkey(key, self.path)
        hash_query = self.construct_query_by_key_and_subkey(key, self.hash)
        return path_query, hash_query

    def abc(self, source_path: str, target_path: str):
        ...

    def get_record_by_computing_source_hash(self, source_path: str):
        source_hash = hash_file(source_path)
        record = self.db.get(
            self.source_hash_eq(source_hash)
        )  # not necessarily directly pointing to the filepath
        return record, source_hash

    @classmethod
    def get_record_file_path_and_hash(cls, record: dict, key: str):
        filepath = record[key][cls.source]
        filehash = record[key][cls.hash]
        return filepath, filehash

    @classmethod
    def get_record_source_path_and_hash(cls, record: dict):
        return cls.get_record_file_path_and_hash(record, cls.source)

    @classmethod
    def get_record_target_path_and_hash(cls, record: dict):
        return cls.get_record_file_path_and_hash(record, cls.target)

    @classmethod
    def verify_record_file_hash(cls, record: dict, key: str):
        filepath, filehash = cls.get_record_file_path_and_hash(record, key)
        verified = verify_filehash(filepath, filehash)
        return verified

    @classmethod
    def verify_record_source_hash(cls, record: dict):
        verified = cls.verify_record_file_hash(record, cls.source)
        return verified

    @classmethod
    def verify_record_target_hash(cls, record: dict):
        verified = cls.verify_record_file_hash(record, cls.target)
        return verified

    @classmethod
    def construct_upsert_data(
        cls, source_path: str, source_hash: str, target_path: str, target_hash: str
    ):
        data = {
            cls.source: {cls.path: source_path, cls.hash: source_hash},
            cls.target: {cls.path: target_path, cls.hash: target_hash},
        }
        return data

    def upsert_data(
        self, source_path: str, source_hash: str, target_path: str, target_hash: str
    ):
        data = self.construct_upsert_data(
            source_path, source_hash, target_path, target_hash
        )
        self.db.upsert(
            data, cond=self.source_path_query(self.source_path_eq(source_path))
        )



@contextmanager
def CacheContextManager(db_path: str):
    manager = CacheManager(db_path)
    try:
        yield manager
    finally:
        del manager

@beartype
def verify_filehash(filepath: str, filehash: str):
    if os.path.exists(filepath):
        current_hash = hash_file(filepath)
        if current_hash == filehash:
            return True
    return False



class TargetGeneratorParameter(pydantic.BaseModel):
    target_dir_path: str
    source_path: str


@beartype
def generate_and_hash_target(
    param: TargetGeneratorParameter,
    target_path_generator: Callable,
    target_file_geneator: Callable,
):
    target_path = target_path_generator(param)
    ret = target_file_geneator(param.source_path, target_path)
    target_hash = hash_file(target_path)
    return target_path, target_hash


@beartype
def verify_record_target(record: dict, manager: CacheManager):
    record_target_path, record_target_hash = manager.get_record_target_path_and_hash(
        record
    )
    target_verified = verify_filehash(record_target_path, record_target_hash)
    return target_verified, record_target_path, record_target_hash


@beartype
def fix_record_if_source_filename_link_is_missing(
    source_path: str,
    source_hash: str,
    record_target_path: str,
    record_target_hash: str,
    manager: CacheManager,
):
    pointed_record = manager.db.get(
        manager.source_path_eq(source_path)
        and manager.target_path_eq(record_target_path)
    )
    if pointed_record is None:
        # insert record
        manager.upsert_data(
            source_path, source_hash, record_target_path, record_target_hash
        )


@beartype
def check_if_target_exists_with_source_in_record(
    record: dict, source_path: str, source_hash: str, manager: CacheManager
):
    has_record = False
    target_verified, record_target_path, record_target_hash = verify_record_target(
        record, manager
    )
    if target_verified:
        # we should check if we have source filename pointing to this target.
        fix_record_if_source_filename_link_is_missing(
            source_path, source_hash, record_target_path, record_target_hash, manager
        )
        has_record = True
    else:
        manager.db.remove(manager.target_path_eq(record_target_path))
    return has_record


@beartype
def check_if_source_exists_in_record(source_path: str, manager: CacheManager):
    has_record = False
    record, source_hash = manager.get_record_by_computing_source_hash(source_path)
    if record:
        has_record = check_if_target_exists_with_source_in_record(
            record, source_path, source_hash, manager
        )
    return has_record, source_hash


class SourceIteratorAndTargetGeneratorParam(pydantic.BaseModel):
    source_dir_path: str
    target_dir_path: str
    db_path: str


@beartype
def iterate_source_dir_and_generate_to_target_dir(
    param: SourceIteratorAndTargetGeneratorParam,
    source_walker: Callable,
    target_path_generator: Callable,
    target_file_geneator: Callable,
):
    with CacheContextManager(param.db_path) as manager:
        for dirpath, fpath in source_walker(param.source_dir_path):
            # use object to pass value around.
            print("processing:", fpath)
            source_path = os.path.join(param.source_dir_path, fpath)
            has_record, source_hash = check_if_source_exists_in_record(
                source_path, manager
            )
            if has_record:
                continue
            target_path, target_hash = generate_and_hash_target(
                TargetGeneratorParameter(
                    target_dir_path=param.target_dir_path, source_path=source_path
                ),
                target_path_generator,
                target_file_geneator,
            )
            manager.upsert_data(source_path, source_hash, target_path, target_hash)

