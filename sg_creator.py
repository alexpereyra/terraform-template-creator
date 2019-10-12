import pandas as pd
import boto3
import os, sys
import pickle
import shutil

csv_filename = input('Name of csv filename with ips: ')
# csv_filename = 'random_ips.csv'

existing_sg_filename = "existing_sg_dict.pkl"
http_tf_filename = 'create_sg_http.tf'
https_tf_filename = 'create_sg_https.tf'

#pickle functions to save dictionary
def save_obj(obj, name ):
    with open(name, 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

def load_obj(name ):
    with open(name, 'rb') as f:
        return pickle.load(f)

def initialize_tf_file(port):
    # create TF file and write resource info
    if port == '80':
        shutil.copyfile('sg_http_template.tf', http_tf_filename)
    elif port == '443':
        shutil.copyfile('sg_https_template.tf', https_tf_filename)
    else:
        print('ERR: unknown port')

def append_ingress(file_lines, port, cidr):
    # append ingress xml with port and CIDR
    file_lines.append('\tingress {\n')
    file_lines.append('\t\t' + '%-12s'%('from_port')   + '= ' + port + '\n')
    file_lines.append('\t\t' + '%-12s'%('to_port')     + '= ' + port + '\n')
    file_lines.append('\t\t' + '%-12s'%('protocol')    + '= "TCP"\n')
    file_lines.append('\t\t' + '%-12s'%('cidr_blocks') + '= ["' + cidr + '"]\n')
    file_lines.append('\t}\n\n')


# load saved dictionary
if os.path.isfile(existing_sg_filename):
    existing_sg = load_obj(existing_sg_filename)
    print('pkl file exists')
else:
    #this will run on first time
    #create empty dictionary
    existing_sg = { "80":[], "443":[]}
print(existing_sg)

# if first time running, create TF files
if not os.path.isfile(http_tf_filename):
    initialize_tf_file('80')

if not os.path.isfile(https_tf_filename):
    initialize_tf_file('443')

# parse CSV file
csv = pd.read_csv(csv_filename)

# read existing file into list of lines
http_tf_fp = open(http_tf_filename, 'r')
https_tf_fp = open(https_tf_filename, 'r')

http_tf_stored = http_tf_fp.readlines()
https_tf_stored = https_tf_fp.readlines()

http_tf_fp.close()
https_tf_fp.close()

http_tf_stored_len = len(http_tf_filename)
https_tf_stored_len = len(https_tf_filename)

last_line = ''
while '}' not in last_line:
    if not http_tf_stored:
        print('ERR: "}" not found in ' + http_tf_filename+ '!')
        sys.exit()
    else:
        last_line = http_tf_stored.pop()

last_line = ''
while '}' not in last_line:
    if not http_tf_stored:
        print('ERR: "}" not found in ' + https_tf_filename+ '!')
        sys.exit()
    else:
        last_line = https_tf_stored.pop()


for idx in range(0, csv.shape[0]):

    #assume string means there was a comma
    #if ',' in csv['Port'][idx]:
    if isinstance(csv['Port'][idx], str):
        port_list = csv['Port'][idx].split(",")
    else:
        port_list = str(csv['Port'][idx])

    cidr = csv['CIDR Block'][idx]

    #if the port list as port 80
    if '80' in port_list:
        #if CIDR is not in the port 80 list
        if cidr not in existing_sg['80']:
            #append http file with cidr
            append_ingress(http_tf_stored, '80', cidr)
            #add this cidr to existing http list
            existing_sg['80'].append(cidr)

    if '443' in port_list:
        if cidr not in existing_sg['443']:
            append_ingress(https_tf_stored, '443', cidr)
            existing_sg['443'].append(cidr)

#add last brace
http_tf_stored.append('}\n')
https_tf_stored.append('}\n')

# write files
http_tf_fp = open(http_tf_filename, 'w')
https_tf_fp = open(https_tf_filename, 'w')

http_tf_fp.writelines(http_tf_stored)
https_tf_fp.writelines(https_tf_stored)

http_tf_fp.close()
https_tf_fp.close()

# save the dictionary
save_obj(existing_sg, existing_sg_filename)
