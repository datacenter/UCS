from collections import defaultdict

def display_to_screen(self):
 
    print "\nSystem : " + self.Name
    print "Number of chassis : " + str(self.get_number_chassis())
    print "Number of blades : " + str(self.get_number_blades()) + "\n"
               
    for chas in self.Chassis:
        print "Chassis ID : " + str(chas.Id) + "\t"
        print "Model : " + str(chas.Model)
        print "Number of Blades : " + str(chas.get_number_blades()) + "\n"
        for blade in chas.Blades:
            print "Name : " + blade.Name + "\t\t" + "Sku : " + blade.Sku + "\t" +"Blade Serial : " + blade.Serial + "\t" + "Total Memory : " + blade.TotalMemory
            for proc in blade.Processors:
                print "\t\t" + "Proc Id : " + proc.Id + "\t" +  "Name : " + proc.Name + "\t\t" "Speed : " +   proc.Speed + "\t" + "Sku : " + proc.Sku + "\t" + "\t" + "Cores : " + proc.Cores
            
            def_dico_mem = defaultdict(int)
            for elem in blade.Memory:
                def_dico_mem[elem] += 1  
            for key, value in def_dico_mem.iteritems():
                print "\t\t" + "Dimm Number : " + str(value) + "\t\t" + "Dimm Name : " + key.Name + "\t\t" + "Dimm Sku : " + key.Sku
            
            for ctrl in blade.StorageCtrls:
                print "\t\t" + "Storage Ctrl Id : " + ctrl.Id + "\t"  +  "Storage Ctrl Name : " + ctrl.Name
                for disk in ctrl.Disks:
                    print "\t\t\t" + "Disk Model : " + disk.Model + "\t" "Disk SKU : " + disk.Sku + "\t" + "Disk Name : " + disk.Name.split('/')[0] + "\t" + "Disk Manuf : " + disk.Manuf
            for adp in blade.Adaptors:
                print "\t\t" + "Adaptor Id : " + adp.Id + "\t" + "Adaptor Model : " + adp.Model + "\t" + "Adaptor Sku : " + adp.Sku + "\t" + "Adaptor Name : " + adp.Name

            print"\n"