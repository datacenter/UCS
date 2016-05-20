from ModelDisplay import ModelDisplay
from collections import defaultdict

class TextDisplay(ModelDisplay):    
    def __init__(self,system):
        ModelDisplay.__init__(self,system)

    def display_header(self,system):
        print "\n"   
        print "System : " + system.Name
        print "Number of chassis : " + str(system.get_number_chassis())
        print "Number of blades : " + str(system.get_number_blades()) + "\n"

    def display_chassis(self,chas):
        print "Chassis ID : " + str(chas.Id) + "\t"
        print "Model : " + str(chas.Model)
        print "Number of Blades : " + str(chas.get_number_blades()) + "\n"

    def display_blade(self,blade):
        print "Name : " + blade.Name + "\t\t" + "Sku : " + blade.Sku + "\t" +"Blade Serial : " + blade.Serial + "\t" + "Total Memory : " + blade.TotalMemory

    def display_proc(self,proc):
        print "\t\t" + "Proc Id : " + proc.Id + "\t" +  "Name : " + proc.Name + "\t\t" "Speed : " +   proc.Speed + "\t" + "Sku : " + proc.Sku + "\t" + "\t" + "Cores : " + proc.Cores

    def display_memory(self,memory):
        def_dico_mem = defaultdict(int)
        for elem in memory:
            def_dico_mem[elem] += 1  
        for key, value in def_dico_mem.iteritems():
            print "\t\t" + "Dimm Number : " + str(value) + "\t\t" + "Dimm Name : " + key.Name + "\t\t" + "Dimm Sku : " + key.Sku

    def display_storage_controller(self,ctrl):
        print "\t\t" + "Storage Ctrl Id : " + ctrl.Id + "\t"  +  "Storage Ctrl Name : " + ctrl.Name

    def display_disk(self,disk):
        print "\t\t\t" + "Disk Model : " + disk.Model + "\t" "Disk SKU : " + disk.Sku + "\t" + "Disk Name : " + disk.Name.split('/')[0] + "\t" + "Disk Manuf : " + disk.Manuf

    def display_adaptor(self,adp):
        print "\t\t" + "Adaptor Id : " + adp.Id + "\t" + "Adaptor Model : " + adp.Model + "\t" + "Adaptor Sku : " + adp.Sku + "\t" + "Adaptor Name : " + adp.Name

    def display_end_of_blade(self):
        print"\n"

    def display(self):
        pass
