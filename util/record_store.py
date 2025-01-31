import argparse
import logging
import os

class RecordStore:
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    def __init__(self, root):
        self.root = root
        self.leaf_folders : list[dict] = []
        self._find_leaf_folders(self.root)

    def _find_leaf_folders(self, root: str) -> list[dict]:
        self.leaf_folders = []

        for dirpath, dirnames, filenames in os.walk(root):
            '''
            if there is no dirnames under the path, which means there is no folder need to dig into
            if we try to find a certain folder, with certain key.
            just traverse the leaf_folders dict and if the key in side the list of sub_folder
            use join the get the whole path
            '''
            if len(dirnames) == 0:
                continue
            entry : dict = {
                "path" : dirpath,
                "sub_folder" : dirnames
            }
            self.leaf_folders.append(entry)
        return self.leaf_folders

    def get_leaf_folders(self):
        return self.leaf_folders

    def traverse_directory(self, name, root_folder=None):
        if name is None:
            return None

        if root_folder is None:
            root_folder = self.root

        for dirpath, dirnames, filenames in os.walk(self.root):
            RecordStore.logger.debug(f'try to find ({name}) in folder ({dirpath}/{dirnames})')
            #print(f'try to find ({name}) in folder ({dirnames})')
            if name in dirnames:
                RecordStore.logger.debug("Directory path:", os.path.join(os.path.abspath(dirpath), name))
                #print(f'find {os.path.join(os.path.abspath(dirpath), name)}')
                return os.path.abspath(os.path.join(os.path.abspath(dirpath), name))
        return None

    def find_path_by_name(self, name : str, root_folder=None):
        RecordStore.logger.info(f'find name {name} in path list')

        if name is None:
            return None

        for record in self.leaf_folders:
            RecordStore.logger.debug(f'try to find ({name}) under folder ({record.get("path")})')
            sub_folder = record.get('sub_folder')
            if name in sub_folder:
                return os.path.join(record.get('path'), name)
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
    # until = 1
    # count = 0
    # for dirpath, dirnames, filenames in os.walk(args.root):
    #     print(f'walk through ({count}):\n')
    #     print(f'\tdirpath : {dirpath}\n')
    #     print(f'\tdirnames : {dirnames}\n')
    #     print(f'\tfilenames : {filenames}\n')
    #     count += 1
    #     if count >= until:
    #         break

    # 取得子目錄列表
    # leaf_folders = record_store.get_leaf_folders()
    # print(f'print leaf folders information ({len(leaf_folders)}):')
    # for path in leaf_folders:
    #     print(f' {path}')

    # 查找特定名子的子目錄
    name = args.folder_name
    path = record_store.find_path_by_name(name)
    #path = record_store.traverse_directory(name)
    if path is not None:
        print(f'找到 "{name}" 的子目錄: {path}')
        print(f'ABS : {record_store.traverse_directory(name)}')
    else:
        print(f'未找到 "{name}" 的子目錄')

    # 取得根目錄的絕對路徑
    absolute_root = record_store.absolute_root_path
    print(f'根目錄的絕對路徑: {absolute_root}')