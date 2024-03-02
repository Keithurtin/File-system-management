from FAT32 import *


def main():
    drive = "\\\\.\\" 
    letter = input("Partition letter: ")
    drive = drive + letter + ":"
    file_system = input("Type of File System: ")
    if (file_system == "FAT32"):
        read_FAT32(drive)
    else:
        print("File system must be FAT32 or NTFS")

if __name__ == "__main__":
    main()
