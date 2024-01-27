import hashlib
import os
from contextlib import contextmanager
from typing import Any, Callable, Iterable, Optional, Tuple

import pydantic
import tinydb
from beartype import beartype
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
    class subkey:
        path = "path"
        hash = "hash"

    class key:
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
            self.key.source
        )
        self.target_path_query, self.target_hash_query = self.construct_query_by_key(
            self.key.target
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
        path_query = self.construct_query_by_key_and_subkey(key, self.subkey.path)
        hash_query = self.construct_query_by_key_and_subkey(key, self.subkey.hash)
        return path_query, hash_query

    def get_record_by_computing_source_hash(self, source_path: str):
        source_hash = hash_file(source_path)
        record = self.db.get(
            self.source_hash_eq(source_hash)
        )  # not necessarily directly pointing to the filepath
        return record, source_hash

    @classmethod
    def get_record_file_path_and_hash(cls, record: dict, key: str) -> tuple[str, str]:
        filepath = record[key][cls.subkey.path]
        filehash = record[key][cls.subkey.hash]
        return filepath, filehash

    @classmethod
    def get_record_source_path_and_hash(cls, record: dict):
        return cls.get_record_file_path_and_hash(record, cls.key.source)

    @classmethod
    def get_record_target_path_and_hash(cls, record: dict):
        return cls.get_record_file_path_and_hash(record, cls.key.target)

    @classmethod
    def verify_record_file_hash(cls, record: dict, key: str):
        filepath, filehash = cls.get_record_file_path_and_hash(record, key)
        verified = verify_filehash(filepath, filehash)
        return verified

    @classmethod
    def verify_record_source_hash(cls, record: dict):
        verified = cls.verify_record_file_hash(record, cls.key.source)
        return verified

    @classmethod
    def verify_record_target_hash(cls, record: dict):
        verified = cls.verify_record_file_hash(record, cls.key.target)
        return verified

    @classmethod
    def construct_upsert_data(
        cls, source_path: str, source_hash: str, target_path: str, target_hash: str
    ):
        data = {
            cls.key.source: {
                cls.subkey.path: source_path,
                cls.subkey.hash: source_hash,
            },
            cls.key.target: {
                cls.subkey.path: target_path,
                cls.subkey.hash: target_hash,
            },
        }
        return data

    def upsert_data(
        self, source_path: str, source_hash: str, target_path: str, target_hash: str
    ):
        data = self.construct_upsert_data(
            source_path, source_hash, target_path, target_hash
        )
        self.db.upsert(
            data,
            cond=self.source_path_eq(source_path),
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
) -> Tuple[bool, str, Optional[str]]:
    has_record = False
    record_target_path = None
    record, source_hash = manager.get_record_by_computing_source_hash(source_path)
    if record:
        has_record, record_target_path = check_if_target_exists_with_source_in_record(
            record, source_path, source_hash, manager
        )
    return has_record, source_hash, record_target_path


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
    ) -> str:
        (
            has_record,
            source_hash,
            record_target_path,
        ) = check_if_source_exists_in_record(source_path, manager)
        if not has_record or not isinstance(record_target_path, str):
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
            # to make this accountable, we need to convert it into list.
            items = list(source_walker(param.source_dir_path))
            items_count = len(items)
            print(f"\n>>>> PROCESSING PROGRESS: 0/{items_count}")
            for i, (_, fpath) in enumerate(items):
                print("processing:", fpath)
                # if file_empty(fpath):
                #     continue
                process_file_and_append_to_cache_paths(
                    manager, fpath, processed_cache_paths
                )
                print(f"\n>>>> PROCESSING PROGRESS: {i+1}/{items_count}")
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
    test_file_basename = "test_file.txt"
    test_db_basename = "cache.db"
    test_source_content = "test"

    @beartype
    def test_target_file_generator(source_path: str, target_path: str):
        content = read_file(source_path)
        write_file(target_path, content)

    @beartype
    def join_dir_path_with_test_file_basename(dir_path: str):
        ret = os.path.join(dir_path, test_file_basename)
        return ret

    @beartype
    def test_target_path_generator(param: TargetGeneratorParameter):
        ret = join_dir_path_with_test_file_basename(param.target_dir_path)
        return ret

    @beartype
    def prepare_test_param(temp_dir: str):
        source_dir, target_dir = make_source_and_target_dirs(temp_dir)
        db_path = os.path.join(temp_dir, test_db_basename)
        param = SourceIteratorAndTargetGeneratorParam(
            source_dir_path=source_dir, target_dir_path=target_dir, db_path=db_path
        )
        return param

    @beartype
    def generate_test_source_walker(source_dir: str):
        @beartype
        def test_source_walker(dirpath: str):
            return [(dirpath, it) for it in os.listdir(source_dir)]

        return test_source_walker

    @beartype
    def write_test_content_to_file(file_path: str):
        write_file(file_path, test_source_content)

    @beartype
    def assert_file_content_as_test_content(file_path):
        test_target_content = read_file(file_path)
        assert test_target_content == test_source_content

    @contextmanager
    @beartype
    def prepare_test_file_context(source_dir: str, target_dir: str):
        test_source_path = join_dir_path_with_test_file_basename(source_dir)
        test_target_path = join_dir_path_with_test_file_basename(target_dir)
        write_test_content_to_file(test_source_path)
        try:
            yield
        finally:
            assert_file_content_as_test_content(test_target_path)

    def test_and_assert(param: SourceIteratorAndTargetGeneratorParam):
        with prepare_test_file_context(param.source_dir_path, param.target_dir_path):
            test_source_walker = generate_test_source_walker(param.source_dir_path)
            iterate_source_dir_and_generate_to_target_dir(
                param,
                test_source_walker,
                test_target_path_generator,
                test_target_file_generator,
            )

    def test_in_temporary_directory():
        with tempfile.TemporaryDirectory() as temp_dir:
            param = prepare_test_param(temp_dir)
            test_and_assert(param)

    test_in_temporary_directory()
    print("test passed")


if __name__ == "__main__":
    test_main()
