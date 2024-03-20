import subprocess

script = 'python3 C:\\Users\\adani\\OneDrive\\Documentos\\GitHub\\SimulatorSPS\\OOP_for_SPS\\SPS_test.py'
td=200
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



