import FAT32
from tabulate import tabulate

def read_NTFS(partitionPath):

    boot_sector = FAT32.read_sector(partitionPath)

    fs_type = FAT32.read_boot_sector_value(boot_sector, "0x03", 8).decode('ascii')
    sec_size = FAT32.bytes_to_integer(FAT32.read_boot_sector_value(boot_sector, '0x0B', 2))
    clus_size = FAT32.bytes_to_integer(FAT32.read_boot_sector_value(boot_sector, '0x0D', 1))
    start_sec_logic_drive = FAT32.bytes_to_integer(FAT32.read_boot_sector_value(boot_sector, '0x1C', 4))
    secs_per_logic_drive = FAT32.bytes_to_integer(FAT32.read_boot_sector_value(boot_sector, '0x28', 8))
    res_sec = FAT32.bytes_to_integer(FAT32.read_boot_sector_value(boot_sector, '0x0E', 2))
    start_clus_MFT = FAT32.bytes_to_integer(FAT32.read_boot_sector_value(boot_sector, '0x30', 8))
    start_clus_MFTMirror = FAT32.bytes_to_integer(FAT32.read_boot_sector_value(boot_sector, '0x38', 8))
    size_MFT_entry = FAT32.bytes_to_integer(FAT32.read_boot_sector_value(boot_sector, '0x40', 1))


    data = [
        ["File System Type", fs_type],
        ["Sector Size", "{:d} bytes".format(sec_size)],
        ["Cluster Size", "{:d} bytes".format(clus_size)],
        ["Start Sector of Logic Drive", "{:d} bytes".format(start_sec_logic_drive)],
        ["Sectors per Logic Drive", "{:d} bytes".format(secs_per_logic_drive)],
        ["Reserved Sectors", "{:d} bytes".format(res_sec)],
        ["Start Cluster of MFT", start_clus_MFT],
        ["Start Cluster of MFTMirror", start_clus_MFTMirror],
        ["Size of MFT Entry", "{:d} bytes".format(size_MFT_entry)]
    ]

    table = tabulate(data, headers=["Property", "Value"], tablefmt="pretty")
    print(table)
