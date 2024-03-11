import sys
import FAT32
from tabulate import tabulate

# Read sector
def read_sector(partitionPath, sector_no = 0):
    read = None
    with open(partitionPath, 'rb') as partition:
        partition.seek(sector_no * 512)
        read = partition.read(512)
    return read


#Use offset in hexadecimal to read
def get_bytes_from_offset(sector, hex_offset_str : str, size):
    return sector[int(int(hex_offset_str, 16)) : int(int(hex_offset_str, 16)) + size]

#Read and print information of boot sector
def read_partition_boot_sector(partitionPath):
    boot_sector = FAT32.read_sector(partitionPath)

    data = [
        ["Type of File System", get_bytes_from_offset(boot_sector, '3', 8).decode()],
        ["Size of a sector", "{:d} bytes".format(FAT32.bytes_to_integer(FAT32.read_boot_sector_value(boot_sector, '0x0B', 2)))],
        ["Size of a cluster", "{:d} bytes".format(FAT32.bytes_to_integer(FAT32.read_boot_sector_value(boot_sector, '0x0D', 1)))],
        ["Starting sector of the logic drive", "{:d} bytes".format(FAT32.bytes_to_integer(FAT32.read_boot_sector_value(boot_sector, '0x1C', 4)))],
        ["Sectors per logic drive", "{:d} bytes".format(FAT32.bytes_to_integer(FAT32.read_boot_sector_value(boot_sector, '0x28', 8)))],
        ["Reserved sector", "{:d} bytes".format(FAT32.bytes_to_integer(FAT32.read_boot_sector_value(boot_sector, '0x0E', 2)))],
        ["Starting cluster of MFT", FAT32.bytes_to_integer(FAT32.read_boot_sector_value(boot_sector, '0x30', 8))],
        ["Starting cluster of MFTMirror", FAT32.bytes_to_integer(FAT32.read_boot_sector_value(boot_sector, '0x38', 8))],
        ["Size of a MFT entry", "{:d} bytes".format(FAT32.bytes_to_integer(FAT32.read_boot_sector_value(boot_sector, '0x40', 1)))],
    ]

    table = tabulate(data, headers=["Property", "Value"], tablefmt="pretty")
    print(table)



#Read MFT to find $INDEX_ROOT and $INDEX_ALLOCATION metadata file
def read_MFT(partitionPath):
    boot_sector = read_sector(partitionPath, 0)
    cluster_MFT = int.from_bytes(get_bytes_from_offset(boot_sector, '30', 8), sys.byteorder)
    cluster_size = int.from_bytes(get_bytes_from_offset(boot_sector, 'D', 1))

    sector_MFT = read_sector(partitionPath, cluster_MFT * cluster_size)
    MFT_entry_size = pow(2, abs(int.from_bytes(get_bytes_from_offset(boot_sector, '40', 1), signed=True)))


def read_NTFS(partitionPath):
    read_partition_boot_sector(partitionPath)
