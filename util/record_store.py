import argparse
import logging
import os

class RecordStore:
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    def __init__(self, root):
        self.root = root
        self.leaf_folders = self._find_leaf_folders(self.root)

    @staticmethod
    def _find_leaf_folders(root):
        leaf_folders = []
        leaf_folders = next(os.walk(root))[1]
        # for entry in os.scandir(root):
        #     path = entry.path
        #     RecordStore.logger.debug(f'path : {path}')
        #     if entry.is_dir() and (entry.name not in [folder[0] for folder in leaf_folders]):
        #         RecordStore.logger.info(f'append path : {path}')
        #         leaf_folders.append((entry.name, os.path.relpath(entry.path, root)))
        return leaf_folders

    def get_leaf_folders(self):
        return self.leaf_folders

    def traverse_directory(self, name):
        for dirpath, dirnames, filenames in os.walk(self.root):
            RecordStore.logger.info(f'try to find ({name}) in folder ({dirpath}/{dirnames})')
            print(f'try to find ({name}) in folder ({dirnames})')
            if name in dirnames:
                RecordStore.logger.info("Directory path:", os.path.join(os.path.abspath(dirpath), name))
                print(f'find {os.path.join(os.path.abspath(dirpath), name)}')
                return os.path.abspath(os.path.join(os.path.abspath(dirpath), name))
        return None

    def find_path_by_name(self, name):
        RecordStore.logger.info(f'find name {name} in path list')
        if name is None:
            return None

        for folder in self.leaf_folders:
            RecordStore.logger.debug(f'try to find ({name}) in folder ({folder})')
            if name == folder:
                return folder
        # for folder, path in self.leaf_folders:
        #     if folder == name:
        #         return path
        return None

    def find_abs_path_by_name(self, name):
        rel = self.find_path_by_name(name)
        if rel:
            return os.path.join(self.absolute_root_path, rel)
        return None
    @property
    def absolute_root_path(self):
        return os.path.abspath(self.root)
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', default='.', help='Root directory to search')
    parser.add_argument('--folder_name', required=True, help='Name of the folder to search for')

    args = parser.parse_args()

    record_store = RecordStore(args.root)

    # 取得子目錄列表
    # leaf_folders = record_store.get_leaf_folders()
    # print(f'print leaf folders information ({len(leaf_folders)}):')
    # for path in leaf_folders:
    #     print(f' {path}')

    # 查找特定名子的子目錄
    name = args.folder_name
    path = record_store.find_path_by_name(name)
    path = record_store.traverse_directory(name)
    if path is not None:
        print(f'找到 "{name}" 的子目錄: {path}')
        print(f'ABS : {record_store.traverse_directory(name)}')
    else:
        print(f'未找到 "{name}" 的子目錄')

    # 取得根目錄的絕對路徑
    absolute_root = record_store.absolute_root_path
    print(f'根目錄的絕對路徑: {absolute_root}')