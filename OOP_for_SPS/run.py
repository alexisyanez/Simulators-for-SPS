import subprocess
import json
import numpy as np


script = 'python3 C:\\Users\\adani\\OneDrive\\Documentos\\GitHub\\SimulatorSPS\\OOP_for_SPS\\SPS_test.py'
td = np.arange(25, 525, 25)
obs = ['--no-obs','obs']
run=2000
ds=4
conf = ' --r '+str(run)+' --td '+str(td)+ ' --no-obs --ds 4'
cmd = script+conf
print(cmd)

file = open("results_td_"+str(td)+"_ds_"+str(ds)+".txt","w")

p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
out = p.communicate()[0].decode("utf-8")
result = out.split('\n')

for lin in result:
    if not lin.startswith('#'):
        file.writelines(lin)
#file.write(out)
#file.write(err)
#file.close()

#print(err)
        

data = {
    "firstName": "Jane",
    "lastName": "Doe",
    "hobbies": ["running", "sky diving", "singing"],
    "age": 35,
    "children": [
        {"firstName": "Alice", "age": 6},
        {"firstName": "Bob", "age": 8}
    ]
}

# Serialize the data to a JSON string
json_data = json.dumps(data, indent=4)

# Write the JSON string to a file (output.json)
with open('output.json', 'w') as f:
    f.write(json_data)



