cik_data = open("CIK_Lookup_Data.txt", "r")
cik_lines = cik_data.readlines()

cik_numbers = open("CIK_Numbers.txt", "w")

for line in cik_lines:
    first_colon = line.index(':')
    second_colon = line.index(':', first_colon+2)
    cik_num = line[first_colon+1: second_colon]
    cik_numbers.write(cik_num + "\n")

cik_data.close()
cik_numbers.close()