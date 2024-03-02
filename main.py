from FAT32 import *
from NTFS import *

def main():
    drive = "\\\\.\\" 
    letter = input("Partition letter: ")
    drive = drive + letter + ":"
    file_system = input("Type of file system: ").lower()
    if (file_system == "fat32"):
        read_FAT32(drive)
    elif (file_system == "ntfs"):
        read_NTFS(drive)
    else:
        print("File system must be FAT32 or NTFS")

if __name__ == "__main__":
    main()
