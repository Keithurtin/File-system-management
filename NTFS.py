import FAT32
from tabulate import tabulate

def read_NTFS(partitionPath):
    boot_sector = FAT32.read_sector(partitionPath)

    data = [
        ["Type of File System", FAT32.read_boot_sector_value(boot_sector, "0x03", 8).decode('ascii')],
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
