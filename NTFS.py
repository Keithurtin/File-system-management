import sys

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
    boot_sector = read_sector(partitionPath, 0)
    print("-------------------Boot Sector-----------------------")
    print("Type of File System: ", get_bytes_from_offset(boot_sector, '3', 8).decode())
    print("Size of a sector: ", int.from_bytes(get_bytes_from_offset(boot_sector, 'B', 2), sys.byteorder), " (Byte)")
    print("Size of a cluster: ", int.from_bytes(get_bytes_from_offset(boot_sector, 'D', 1)), " (Sector)")
    print("Number of sectors on logical drive: ", int.from_bytes(get_bytes_from_offset(boot_sector, '28', 8), sys.byteorder), " (Sector)")
    print("Disk type ID: ", int.from_bytes(get_bytes_from_offset(boot_sector, '15', 1)))
    print("Starting cluster of MFT: ", int.from_bytes(get_bytes_from_offset(boot_sector, '30', 8), sys.byteorder))
    print("Size of a MFT entry: ", pow(2, abs(int.from_bytes(get_bytes_from_offset(boot_sector, '40', 1), signed=True)))," (Bytes)")
    print("----------------------------------------------------- \n")

#Read MFT to find $INDEX_ROOT and $INDEX_ALLOCATION metadata file
def read_MFT(partitionPath):
    boot_sector = read_sector(partitionPath, 0)
    cluster_MFT = int.from_bytes(get_bytes_from_offset(boot_sector, '30', 8), sys.byteorder)
    cluster_size = int.from_bytes(get_bytes_from_offset(boot_sector, 'D', 1))

    sector_MFT = read_sector(partitionPath, cluster_MFT * cluster_size)
    MFT_entry_size = pow(2, abs(int.from_bytes(get_bytes_from_offset(boot_sector, '40', 1), signed=True)))


def read_NTFS(partitionPath):
    read_partition_boot_sector(partitionPath)
