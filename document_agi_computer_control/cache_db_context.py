import hashlib
import os
from contextlib import contextmanager
from typing import Any, Callable, Iterable, Literal, Optional, Tuple, Union
import uuid

import pydantic
import tinydb
from beartype import beartype
from tinydb.queries import QueryLike
import tempfile

UTF8 = "utf-8"


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
        self.init_query()

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
        filepath: str = record[key][cls.source]
        filehash: str = record[key][cls.hash]
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

    def has_document_matching_condition(self, cond: Optional[QueryLike] = None):
        candidates = []
        if cond is not None:
            candidates = self.db.search(cond)
        has_document = len(candidates) > 0
        return has_document

    def better_upsert(self, data: dict, cond: Optional[QueryLike] = None):
        has_document = self.has_document_matching_condition(cond)
        self.db.upsert(data, cond=cond if has_document else None)

    def upsert_data(
        self, source_path: str, source_hash: str, target_path: str, target_hash: str
    ):
        data = self.construct_upsert_data(
            source_path, source_hash, target_path, target_hash
        )
        self.better_upsert(
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
    target_path_generator: Callable[[TargetGeneratorParameter], str],
    target_file_geneator: Callable[[str, str], Any],
):
    target_path = target_path_generator(param)
    _ = target_file_geneator(param.source_path, target_path)
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
    return has_record, record_target_path


@beartype
def check_if_source_exists_in_record(
    source_path: str, manager: CacheManager
) -> Union[Tuple[Literal[True], str, str], Tuple[Literal[False], str, Literal[None]]]:
    has_record = False
    record_target_path = None
    record, source_hash = manager.get_record_by_computing_source_hash(source_path)
    if record:
        has_record, record_target_path = check_if_target_exists_with_source_in_record(
            record, source_path, source_hash, manager
        )
    return has_record, source_hash, record_target_path  # type:ignore


class SourceIteratorAndTargetGeneratorParam(pydantic.BaseModel):
    source_dir_path: str
    target_dir_path: str
    db_path: str


@beartype
def iterate_source_dir_and_generate_to_target_dir(
    param: SourceIteratorAndTargetGeneratorParam,
    source_walker: Callable[[str], Iterable[tuple[Any, str]]],
    target_path_generator: Callable[[TargetGeneratorParameter], str],
    target_file_geneator: Callable[[str, str], Any],
    join_source_dir: bool = True,
) -> list[str]:
    @beartype
    def process_source_and_return_target_path(
        manager: CacheManager,
        source_path: str,
        source_hash: str,
    ):
        target_path, target_hash = generate_and_hash_target(
            TargetGeneratorParameter(
                target_dir_path=param.target_dir_path, source_path=source_path
            ),
            target_path_generator,
            target_file_geneator,
        )
        manager.upsert_data(source_path, source_hash, target_path, target_hash)
        return target_path

    @beartype
    def get_target_path_by_checking_manager_or_processing(
        manager: CacheManager, source_path: str
    ):
        (
            has_record,
            source_hash,
            record_target_path,
        ) = check_if_source_exists_in_record(source_path, manager)
        if not isinstance(record_target_path, str) or (not has_record):
            target_path = process_source_and_return_target_path(
                manager,
                source_path,
                source_hash,
            )
        else:
            target_path = record_target_path
        return target_path

    @beartype
    def process_file_and_append_to_cache_paths(
        manager: CacheManager, fpath: str, processed_cache_paths: list[str]
    ):
        source_path = (
            os.path.join(param.source_dir_path, fpath) if join_source_dir else fpath
        )
        target_path = get_target_path_by_checking_manager_or_processing(
            manager, source_path
        )
        processed_cache_paths.append(target_path)

    @beartype
    def get_processed_cache_paths():
        processed_cache_paths: list[str] = []
        with CacheContextManager(param.db_path) as manager:
            for _, fpath in source_walker(param.source_dir_path):
                print("processing:", fpath)
                process_file_and_append_to_cache_paths(
                    manager, fpath, processed_cache_paths
                )
        return processed_cache_paths

    return get_processed_cache_paths()


@beartype
def make_and_return_dir_path(base_dir: str, subdir: str):
    dirpath = os.path.join(base_dir, subdir)
    os.mkdir(dirpath)
    return dirpath


@beartype
def make_source_and_target_dirs(base_dir: str):
    @beartype
    def make_and_return_dir_path_under_base_dir(subdir: str):
        return make_and_return_dir_path(base_dir, subdir)

    source_dir = make_and_return_dir_path_under_base_dir("source")
    target_dir = make_and_return_dir_path_under_base_dir("target")
    return source_dir, target_dir


@beartype
def read_file(fpath: str):
    with open(fpath, "r", encoding=UTF8) as f:
        return f.read()


@beartype
def write_file(fpath: str, content: str):
    with open(fpath, "w+", encoding=UTF8) as f:
        f.write(content)


def test_main():
    @beartype
    def target_file_generator(source_path: str, target_path: str):
        content = read_file(source_path)
        write_file(target_path, content)

    @beartype
    def target_path_generator(param: TargetGeneratorParameter):
        fname = str(uuid.uuid4())
        ret = os.path.join(param.target_dir_path, fname)
        return ret

    @beartype
    def prepare_test_param(temp_dir: str):
        source_dir, target_dir = make_source_and_target_dirs(temp_dir)
        db_path = os.path.join(temp_dir, "cache.db")
        param = SourceIteratorAndTargetGeneratorParam(
            source_dir_path=source_dir, target_dir_path=target_dir, db_path=db_path
        )
        return param

    @beartype
    def generate_test_source_walker(source_dir: str):
        @beartype
        def source_walker(dirpath: str):
            return [(dirpath, it) for it in os.listdir(source_dir)]

        return source_walker

    @beartype
    def prepare_test_file(source_dir: str):
        test_file_path = os.path.join(source_dir, "test_file.txt")
        write_file(test_file_path, "test")

    def test_in_temporary_directory():
        with tempfile.TemporaryDirectory() as temp_dir:
            param = prepare_test_param(temp_dir)
            prepare_test_file(param.source_dir_path)
            source_walker = generate_test_source_walker(param.source_dir_path)
            iterate_source_dir_and_generate_to_target_dir(
                param, source_walker, target_path_generator, target_file_generator
            )

    test_in_temporary_directory()


if __name__ == "__main__":
    test_main()
