import os
from tabulate import tabulate

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
    name += read_name(sector, index +1, index + 11) + read_name(sector, index + 14, index + 26) + read_name(sector, index + 28, index + 32)
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
    os.system('cls')
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
    enter = input("\nPress Enter to go back")

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
    


def execute(drive, Sb, Sf, Sc, first_clus):
    while (True):
        os.system('cls')
        clus = first_clus
        filename_list = []
        filename = ""
        expand_list = []
        status_list = []
        size_list = []
        clus_start_list = []

        # Read RDET and SDET
        while(clus != to_dec("0FFFFFFF")):
            first_sec = Sb + Sf * 2 + Sc * (clus - 2)
            for i in range(Sc):
                sector = read_sector(drive, first_sec + i)
                for j in range(0, 512, 32):
                    if (sector[j] == 0 or sector[j] == to_dec("E5")):
                        continue
                    if (sector[j + to_dec("B")] == to_dec("0F")):
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
        print_info(filename_list, status_list, size_list, clus_start_list)

        # Read SDET
        while (True):
            id = int(input("Enter id of file/directory you want to open. Enter 0 to go back: "))
            if (id == 0): 
                return
            if (id >= len(filename_list)):
                print("There is no file/directory with id", id)
            elif (status_list[id] == "Directory"):    
                execute(drive, Sb, Sf, Sc, clus_start_list[id])
                break
            elif (status_list[id] == "Archive" and expand_list[id] == "TXT"):
                print_txt(drive, Sb, Sf, Sc, clus_start_list[id], size_list[id])
                break
            else:
                print("You cannot open this file/directory")


def read_FAT32(drive):
    
    # Read Boot sector
    boot_sector = read_sector(drive)
    bytes_per_sec = 512
    Sc = boot_sector[to_dec("D")]
    Sb = hexstr_to_dec(dec_to_hexstr(boot_sector[to_dec("F")]) + dec_to_hexstr(boot_sector[to_dec("E")]))
    Sv = hexstr_to_dec(dec_to_hexstr(boot_sector[to_dec("23")]) + dec_to_hexstr(boot_sector[to_dec("22")]) + dec_to_hexstr(boot_sector[to_dec("21")]) + dec_to_hexstr(boot_sector[to_dec("20")]))
    Sf = hexstr_to_dec(dec_to_hexstr(boot_sector[to_dec("27")]) + dec_to_hexstr(boot_sector[to_dec("26")]) + dec_to_hexstr(boot_sector[to_dec("25")]) + dec_to_hexstr(boot_sector[to_dec("24")]))
    first_clus_rdet = hexstr_to_dec(dec_to_hexstr(boot_sector[to_dec("2F")]) + dec_to_hexstr(boot_sector[to_dec("2E")]) + dec_to_hexstr(boot_sector[to_dec("2D")]) + dec_to_hexstr(boot_sector[to_dec("2C")]))

    # Print Boot sector
    print("Bytes per sector: ",  bytes_per_sec)
    print("Sc = ", Sc)
    print("Sb = ", Sb)
    print("Sv = ", Sv)
    print("Sf = ", Sf)
    print("First cluster of rdet = ", first_clus_rdet)

    enter = input("Press Enter to open root directory tree")
    execute(drive, Sb, Sf, Sc, first_clus_rdet)

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