import sys
import os
import struct
from tabulate import tabulate

def read_boot_sector_value(boot_sector, hex_offset, num_bytes):
    dec_offset = int(int(hex_offset, 16))
    # Trích xuất giá trị từ boot sector dựa trên offset và số bytes
    value = struct.unpack_from(f"<{num_bytes}s", boot_sector, dec_offset)[0]
    return value

def bytes_to_integer(byte_string):
    # Sử dụng struct.unpack để giải mã giá trị từ chuỗi bytes
    format_string = f"<{len(byte_string)}B"  # Xác định định dạng cho số lượng byte cụ thể
    integer_value = struct.unpack(format_string, byte_string)
    
    # Chuyển đổi tuple thành một số nguyên
    result = sum(b << (8 * i) for i, b in enumerate(integer_value))
    
    return result

def pad_hex(s):
    return s[2:].zfill(2)

def to_dec(hex):
    return int(int(hex, 16))

def dec_to_hexstr(dec):
    return pad_hex(hex(dec))

def hexstr_to_dec(hexstr):
    return(int(int(hexstr, 16)))

def get_FAT_sector(drive, Sb, sector_no):
    element = ""
    sector = read_sector(drive, Sb + sector_no)
    arr = []
    for j in range(512):
        element += dec_to_hexstr(sector[j])[::-1]
        if ( (j + 1) % 4 == 0):
            element = element[::-1]
            arr.append(element)
            element = ""
    return arr

def read_name(sector, start, end):
    name = ""
    char = ''
    for i in range(start, end):
        char = chr(sector[i])
        if (sector[i] != 0 and sector[i] != to_dec("FF")):
            name += char
    return name

def read_subentry(sector, index):
    name = ""
    name += read_name(sector, index + 1, index + 11) + read_name(sector, index + 14, index + 26) + read_name(sector, index + 28, index + 32)
    return name

def read_status(sector, index):
    status = ""
    if (sector[index] == 32):
        status = "Archive"
    if (sector[index] == 16):
        status = "Directory"
    if (sector[index] == 8):
        status = "VolLabel"
    if (sector[index] == 4):
        status = "System"
    if (sector[index] == 2):
        status = "Hidden"
    if (sector[index] == 0):
        status = "ReadOnly"
    return status

def read_sec_addr(drive, Sb, Sf, Sc, clus_start):
    sec_list = []
    clus = clus_start
    while (clus != to_dec("0FFFFFFF")):
        first_sec = Sb + Sf * 2 + Sc * (clus - 2)
        for i in range(Sc):
            sec_list.append(first_sec + i)
        FAT = get_FAT_sector(drive, Sb, (clus//128))
        clus = hexstr_to_dec(FAT[clus % 128])
    return sec_list

def print_txt(drive, Sb, Sf, Sc, first_clus, size):
    # os.system('cls')
    content = ""
    word_count = 0
    clus = first_clus
    while(clus != to_dec("0FFFFFFF")):
        first_sec = Sb + Sf * 2 + Sc * (clus - 2)
        for i in range(Sc):
            if (word_count >= size):
                break
            sector = read_sector(drive, first_sec + i)
            for j in range(512):
                if (word_count >= size):
                    break
                content += chr(sector[j])
                word_count += 1
        FAT = get_FAT_sector(drive, Sb, (clus//128))
        clus = hexstr_to_dec(FAT[clus % 128])
    print(content)    
    # enter = input("\nPress Enter to go back")

def print_info(filename_list, status_list, size_list, clus_start_list):
    id_list = []
    for i in range(len(filename_list)):
        id_list.append(i)
    tree = {
        "Id": id_list,
        "Name": filename_list,
        "Status": status_list,
        "Size": size_list,
        "Starting cluster": clus_start_list
    }
    print(tabulate(tree, headers = ["Id", "Name", "Status", "Size", "Starting cluster"]))
    


def execute(drive, Sb, Sf, Sc, first_clus, Nf, isPrint = True, path = ""):
    while (True):
        # os.system('cls')
        clus = first_clus
        filename_list = []
        filename = ""
        expand_list = []
        status_list = []
        size_list = []
        clus_start_list = []

        # Read RDET and SDET
        while(clus != to_dec("0FFFFFFF")):
            first_sec = Sb + Sf * Nf + Sc * (clus - 2)
            for i in range(Sc):
                sector = read_sector(drive, first_sec + i)
                for j in range(0, 512, 32):
                    if j >= len(sector):
                        break
                    if (sector[j] == 0 or sector[j] == to_dec("0xE5")):
                        continue
                    if (sector[j + to_dec("0x0B")] == to_dec("0x0F")):
                        filename = read_subentry(sector, j) + filename
                    else:
                        status = read_status(sector, j + to_dec("B"))
                        if (status != ""):
                            status_list.append(status)
                            expand = read_name(sector, j + 8, j + 11)
                            expand_list.append(expand)
                            if (filename == ""):
                                filename = read_name(sector, j, j + 8)
                                if (expand != "   "):
                                    filename += "." + expand
                            filename = filename.strip()
                            filename_list.append(filename)
                            size = hexstr_to_dec(dec_to_hexstr(sector[j + 31]) + dec_to_hexstr(sector[j + 30]) + dec_to_hexstr(sector[j + 29]) + dec_to_hexstr(sector[j + 28]))
                            size_list.append(size)
                            clus_start = hexstr_to_dec(dec_to_hexstr(sector[j + 21]) + dec_to_hexstr(sector[j + 20]) + dec_to_hexstr(sector[j + 27]) + dec_to_hexstr(sector[j + 26]))
                            clus_start_list.append(clus_start)
                        filename = ""
            FAT = get_FAT_sector(drive, Sb, (clus//128))
            clus = hexstr_to_dec(FAT[clus % 128])

        # Print RDET and SDET
        if (isPrint == True):
            print_info(filename_list, status_list, size_list, clus_start_list)
        # path = path + ":\\" 
        # Read SDET
        while True:
            user_input = input(f"{path}> ")
            tokens = user_input.split()

            while user_input == '':
                user_input = input(f"{path}> ")

            if user_input == "exit":
                sys.exit()
            elif user_input == "back" or user_input == "cd ..":
                return
            elif user_input == "ls":
                print_info(filename_list, status_list, size_list, clus_start_list)
            elif user_input == "clear":
                os.system('cls' if os.name == 'nt' else 'clear')
            elif tokens[0] == "cd" and len(tokens) > 1:
                folder_name = " ".join(tokens[1:])
                if (folder_name in filename_list and status_list[filename_list.index(folder_name)] == "Directory"):
                    execute(drive, Sb, Sf, Sc, clus_start_list[filename_list.index(folder_name)], Nf, False, path + "\\" + folder_name)
                else: 
                    print("Invalid directory:", folder_name)
            elif tokens[0] == "type" and len(tokens) > 1:
                __file_name = " ".join(tokens[1:])
                if __file_name in filename_list and status_list[filename_list.index(__file_name)] == "Archive" and expand_list[filename_list.index(__file_name)] == "TXT":
                    print_txt(drive, Sb, Sf, Sc, clus_start_list[filename_list.index(__file_name)], size_list[filename_list.index(__file_name)])
                elif __file_name in filename_list and status_list[filename_list.index(__file_name)] == "Archive":
                    print("You only can open .txt file")
                else: 
                    print("Invalid file name:", __file_name)
            else:
                print("Available commands:")
                print("  cd <directory>    : Change current directory to the specified one.")
                print("  type <file_name>  : Display the contents of the specified file.")
                print("  clear             : Clear the screen.")
                print("  help              : Display information about available commands.")
                print("  exit              : Exit the program.")
                print("  back              : Move back to the previous directory.")
                print("  cd ..             : Move back to the previous directory.")
                print("  ls                : List the contents of the current directory.")



def read_FAT32(drive):
    
    # Read Boot sector
    boot_sector = read_sector(drive)

    # read_boot_sector_value(boot_sector, "52", 8)

    bytes_per_sec = bytes_to_integer(read_boot_sector_value(boot_sector, "0x0B", 2))
    sectors_per_cluster = bytes_to_integer(read_boot_sector_value(boot_sector, "0x0D", 1))
    reserved_sector = bytes_to_integer(read_boot_sector_value(boot_sector, "0x0E", 2))
    number_of_FATs = bytes_to_integer(read_boot_sector_value(boot_sector, "0x10", 1))
    entrys_per_rdet = bytes_to_integer(read_boot_sector_value(boot_sector, "0x11", 2))
    sectors_per_volume = bytes_to_integer(read_boot_sector_value(boot_sector, "0x20", 4))
    sectors_per_fat = bytes_to_integer(read_boot_sector_value(boot_sector, "0x24", 4))
    first_clus_rdet = hexstr_to_dec(dec_to_hexstr(boot_sector[to_dec("2F")]) + dec_to_hexstr(boot_sector[to_dec("2E")]) + dec_to_hexstr(boot_sector[to_dec("2D")]) + dec_to_hexstr(boot_sector[to_dec("2C")]))

    # Print Boot sector
    data = [
        ("Type of file system detected", read_boot_sector_value(boot_sector, "0x52", 8).decode('ascii')),
        ("Bytes per sector", "{} bytes".format(bytes_per_sec)),
        ("Sectors per cluster (Sc)", "{} sectors".format(sectors_per_cluster)),
        ("Reserved sector (Sb)", "{} sectors".format(reserved_sector)),
        ("Number of FATs (Nf)", "{} fats".format(number_of_FATs)),
        ("Size of volume (Sv)", "{} sectors".format(sectors_per_volume)),
        ("Size of FAT (Sf)", "{} sectors".format(sectors_per_fat)),
        # ("First sector of FAT1", reserved_sector),
        # ("First sector of RDET", reserved_sector + (number_of_FATs * sectors_per_fat)),
        # ("First sector of data area", reserved_sector + (number_of_FATs * sectors_per_fat) + (entrys_per_rdet * 32 / 512)),
        ("First cluster of rdet", first_clus_rdet)
    ]

    # In bảng
    table = tabulate(data, headers=["Property", "Value"], tablefmt="pretty")
    print(table)
    print("\n")
    print("type help for assistance")
    print("\n")
    execute(drive, reserved_sector, sectors_per_fat, sectors_per_cluster, first_clus_rdet, number_of_FATs, False, drive[-2] + ":")

        
    

def read_sector(disk, sector_no=0):
    """Read a single sector of the specified disk.

    Keyword arguments:
    disk -- the physical ID of the disk to read.
    sector_no -- the sector number to read (default: 0).
    """
    # Static typed variable
    read = None
    # File operations with `with` syntax. To reduce file handeling efforts.
    with open(disk, 'rb') as fp:
        fp.seek(sector_no * 512)
        read = fp.read(512)
    return read




'''
reference: https://github.com/owenlo/ReadDisk-Python/blob/master/readdisk.py
'''