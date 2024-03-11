import os
import FAT32 
import NTFS 

def printGroupInfo():
    print('+' + '-'*49 + '+')
    print('| FAT and NTFS File System Management Tool')
    print('| Operating Systems - Project 1')
    print('| VNU-HCM University of Science')
    print('| Authors: 22127113 - 22127199 - 22127472 - 22127487')
    print('+' + '-'*49 + '+')

def main():
    os.system('cls' if os.name == 'nt' else 'clear')
    printGroupInfo()
    drive = "\\\\.\\" 
    letter = input("Partition letter: ")
    drive = drive + letter + ":"
    if (b'FAT32' in FAT32.read_sector(drive)):
        FAT32.read_FAT32(drive)
    elif (b'NTFS' in NTFS.read_sector(drive)):
        NTFS.read_NTFS(drive)
    else:
        print("File system must be FAT32 or NTFS")

if __name__ == "__main__":
    main()
