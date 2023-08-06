import os
from sys import argv
from .folderreader import FolderReader


def main(folder_name, debug=False, energy_limit=5, skip=[],
         goto_reaction=None):
    folder_name = folder_name.rstrip('/')
    FR = FolderReader(folder_name=folder_name, debug=debug,
                      energy_limit=energy_limit)
    FR.write(skip=skip, goto_reaction=goto_reaction)
    return FR.pub_id


if __name__ == '__main__':
    folder_name = argv[1]
    main(folder_name)
