#!/usr/bin/env python

""" ucs_inventory.py: Get and save UCS inventory information to text or xls file """

#from string import center

__author__      = "Franck Bonneau"
__reviewer__    = "Guillaume Morini"
__copyright__   = "Copyright 2016, Cisco"

import sys, traceback, argparse, os.path


# With Python version 2.7.9 and above, python embedded the certificate validation.
def sslWorkaround():
    isVerifyCertificate = False
    if not sys.version_info < (2,6):
        from functools import partial
        import ssl
        ssl.wrap_socket = partial(ssl.wrap_socket, ssl_version=ssl.PROTOCOL_TLSv1)
        if not sys.version_info < (2, 7, 9) and not isVerifyCertificate:
            ssl._create_default_https_context = ssl._create_unverified_context

sslWorkaround()

from UcsSdk import UcsHandle
from UcsSdk.MoMeta.TopSystem import TopSystem
from UcsSdk.MoMeta.EquipmentChassis import EquipmentChassis
from UcsSdk.MoMeta.ComputeBlade import ComputeBlade
from UcsSdk.MoMeta.ComputeBoard import ComputeBoard
from UcsSdk.MoMeta.ProcessorUnit import ProcessorUnit
from UcsSdk.MoMeta.StorageController import StorageController
from UcsSdk.MoMeta.StorageLocalDisk import StorageLocalDisk
from UcsSdk.MoMeta.AdaptorUnit import AdaptorUnit
from UcsSdk.MoMeta.MemoryArray import MemoryArray
from UcsSdk.MoMeta.MemoryUnit import MemoryUnit
from UcsSdk.MoMeta.EquipmentManufacturingDef import EquipmentManufacturingDef

from TextDisplay import TextDisplay
from XLSDisplay import XLSDisplay

class CatalogElem:
    def __init__(self, model, name, sku, revision, vendor):
        self.Pid = model
        self.Name = name
        self.Sku = sku
        self.Revision = revision
        self.Vendor = vendor
        
class Catalog:
    def __init__(self,handle):
        self.EquipManufDef = handle.GetManagedObject(None, EquipmentManufacturingDef.ClassId())
        self.CatalogElemList = []
        
    def CatalogAddElem(self, model, revision, vendor):
        for mo in self.EquipManufDef:
            if (model and revision and vendor and mo.Dn.find(model) != -1 and mo.Dn.find("revision-"+revision) != -1 and mo.Dn.find(vendor) != -1):
                    New_CatalogElem = CatalogElem(model, mo.Name, mo.Sku, revision, vendor)
                    self.CatalogElemList.append(New_CatalogElem)
                    return New_CatalogElem
    
    def IsCatalogElem(self, model, revision, vendor):
        for elem in self.CatalogElemList:
            if (elem.Name == model and elem.Revision == revision and elem.Vendor == vendor):
                return elem
            else:
                return -1
            

class System:

    def __init__(self, Target, User, Pass):
        
        self.Target = Target
        self.Username = User
        self.Password = Pass
        self.Sys = ""
        self.Name = ""
        self.handle = ""
        self.Chassis = []

        self.Connect()
        
        print "Starting to get information from system : " + self.Name
        
        try:
            self.Catalog = Catalog(self.handle)
            self.EquipManufDef = self.handle.GetManagedObject(None, EquipmentManufacturingDef.ClassId())
            for chassis in self.__get_sorted_chassis_list():
                print "\nCollect information from chassis # " + chassis.Id
                New_Chassis = Chassis(self.handle, chassis, self)
                self.Chassis.append(New_Chassis)         
            self.Disconnect()
           
        except:
            self.Disconnect()
            raise 
             
 
    def Connect(self):
        try:
            self.handle = UcsHandle() 
            self.handle.Login(self.Target,self.Username,self.Password)
            self.Sys = self.handle.GetManagedObject(None,TopSystem.ClassId(),{"Dn":"sys"})[0]
            self.Name = self.Sys.Name
        
        except Exception, err:
            print "Exception:", str(err)
            print '-'*60
            traceback.print_exc(file=sys.stdout)
            print '-'*60
            
    def Disconnect(self):
        self.handle.Logout()

    def __get_sorted_chassis_list(self):
        '''Get UCS Chassis list via established connection handle, sorted by Dn.
        Return a list of EquipmentChassis ManagedObjects'''
        return sorted(self.handle.GetManagedObject(None, EquipmentChassis.ClassId()), key=lambda chassis: chassis.Dn)
    
    def get_number_chassis(self):
        return len(self.Chassis)
    
    def get_number_blades(self):
        blades_num = 0
        for chas in self.Chassis:
            blades_num += chas.get_number_blades()
        return blades_num

class Chassis:
    
    def __init__(self, handle, chassis, system):
        self.Blades = []
        self.Id = chassis.Id
        self.Model = chassis.Model
        self.Dn = chassis.Dn
        self.system = system
                
        blades = self.__get_sorted_blades_from_chassis(handle, chassis)
        i=1
        for blade in blades:
            New_Blade = Blade(handle, blade, self)
            self.Blades.append(New_Blade)
            sys.stdout.write('\r')
            sys.stdout.write("[%-20s] %d%%" % ('='*int((float(i)/len(blades))*20), (float(i)/len(blades))*100))
            sys.stdout.flush()
            i=i+1
        
    def __get_sorted_blades_from_chassis(self, handle, chassis):
        '''Get UCS ComputeBlade list from specified EquipmentChassis via established connection handle, sorted by Dn.
        Return a list of ComputeBlade ManagedObjects'''
        return sorted(handle.ConfigResolveChildren(ComputeBlade.ClassId(), chassis.Dn, None).OutConfigs.GetChild(), key=lambda blade: blade.Dn)
    
    def get_number_blades(self):
        return len(self.Blades)

class Blade:
    
    def __init__(self, handle, blade, chassis):   
        self.board = self.__get_sorted_boards_from_blade(handle, blade)
        self.MemArrays = self.__get_sorted_memoryarrays_from_board(handle, self.board[0])
        self.ServerId = blade.ServerId
        self.SlotId = blade.SlotId
        self.Model = blade.Model
        self.Dn = blade.Dn
        self.Sku = ""
        self.Name = ""
        self.TotalMemory = blade.TotalMemory
        self.Serial = blade.Serial
        self.Processors = []
        self.Memory = []
        self.StorageCtrls = []
        self.Adaptors = []
        self.chassis = chassis
        
        CatalogElem = chassis.system.Catalog.IsCatalogElem(blade.Model, blade.Revision, blade.Vendor)
        if CatalogElem == -1 or CatalogElem == None:
            CatalogElem = chassis.system.Catalog.CatalogAddElem(blade.Model, blade.Revision, blade.Vendor)  
        self.Sku = CatalogElem.Sku
        self.Name = CatalogElem.Name
            
        for proc in self.__get_sorted_processors_from_board(handle, self.board[0]):
            New_Proc = Processor(handle, proc, self)
            self.Processors.append(New_Proc)
          
        for ctrl in self.__get_sorted_storagecontrollers_from_board(handle, self.board[0]):
            New_Ctrl = StorageCtrl(handle, ctrl, self)
            self.StorageCtrls.append(New_Ctrl)    
         
        for adaptor in self.__get_sorted_adaptors_from_blade(handle, blade):
            New_Adaptor = Adaptor(handle, adaptor, self)
            self.Adaptors.append(New_Adaptor)
        
        for MemArray in self.MemArrays:
            for Dim in self.__get_sorted_memoryunits_from_memoryarray(handle, MemArray):
                if Dim.Model != "":
                    New_Dimm = MemDimm(handle, Dim, self)
                    self.Memory.append(New_Dimm)
            
    def __get_sorted_boards_from_blade(self, handle, blade):
        '''Get UCS ComputeBoard list from specified ComputeBlade via established connection handle, sorted by Dn.
        Return a list of ComputeBoard ManagedObjects'''
        return sorted(handle.ConfigResolveChildren(ComputeBoard.ClassId(), blade.Dn, None).OutConfigs.GetChild(), key=lambda board: board.Dn)
        
    def __get_sorted_processors_from_board(self, handle, board):
        '''Get UCS ProcessorUnit list from specified ComputeBoard via established connection handle, sorted by Dn.
        Return a list of ProcessorUnit ManagedObjects'''
        return sorted(handle.ConfigResolveChildren(ProcessorUnit.ClassId(), board.Dn, None).OutConfigs.GetChild(), key=lambda processor: processor.Dn)
              
    def __get_sorted_storagecontrollers_from_board(self, handle, board):
        '''Get UCS StorageController list from specified ComputeBoard via established connection handle, sorted by Dn.
        Return a list of StorageController ManagedObjects'''
        return sorted(handle.ConfigResolveChildren(StorageController.ClassId(), board.Dn, None).OutConfigs.GetChild(), key=lambda storagecontroller: storagecontroller.Dn)

    def __get_sorted_adaptors_from_blade(self, handle, blade):
        '''Get UCS AdaptorUnit list from specified ComputeBlade via established connection handle, sorted by Dn.
        Return a list of AdaptorUnit ManagedObjects'''
        return sorted(handle.ConfigResolveChildren(AdaptorUnit.ClassId(), blade.Dn, None).OutConfigs.GetChild(), key=lambda adaptor: adaptor.Dn)
    
    def __get_sorted_memoryarrays_from_board(self, handle, board):
        '''Get UCS MemoryArray list from specified ComputeBoard via established connection handle, sorted by Dn.
        Return a list of MemoryArray ManagedObjects'''
        return sorted(handle.ConfigResolveChildren(MemoryArray.ClassId(), board.Dn, None).OutConfigs.GetChild(), key=lambda memoryarray: memoryarray.Dn)
    
    def __get_sorted_memoryunits_from_memoryarray(self, handle, memoryarray):
        '''Get UCS MemoryUnit list from specified MemoryArray via established connection handle, sorted by Dn.
        Return a list of MemoryUnit ManagedObjects'''
        return sorted(handle.ConfigResolveChildren(MemoryUnit.ClassId(), memoryarray.Dn, None).OutConfigs.GetChild(), key=lambda memoryunit: memoryunit.Dn)

class Processor:
    def __init__(self, handle, proc, blade):
        self.Id = proc.Id
        self.Model = proc.Model
        self.Sku = ""
        self.Name = ""
        self.Speed = proc.Speed
        self.Cores = proc.Cores
        
        CatalogElem = blade.chassis.system.Catalog.IsCatalogElem(self.Model, proc.Revision, proc.Vendor)
        if CatalogElem == -1:
            CatalogElem = blade.chassis.system.Catalog.CatalogAddElem(self.Model, proc.Revision, proc.Vendor)  
        self.Sku = CatalogElem.Sku
        self.Name = CatalogElem.Name
        
 
class StorageCtrl:
    def __init__(self, handle, ctrl, blade):
        self.Id = ctrl.Id
        self.Model = ctrl.Model
        self.Name = ""
        self.Disks = []
        self.blade = blade 
        
        CatalogElem = blade.chassis.system.Catalog.IsCatalogElem(self.Model, ctrl.Revision, ctrl.Vendor)
        if CatalogElem == -1:
            CatalogElem = blade.chassis.system.Catalog.CatalogAddElem(self.Model, ctrl.Revision, ctrl.Vendor)  
        self.Name = CatalogElem.Name

        disques = self.__get_sorted_disks_from_storagecontroller(handle, ctrl)
        
        for disk in disques:
            if disk.Model != "":
                New_Disk = Disk(handle, disk, self)
                self.Disks.append(New_Disk) 
              
    def __get_sorted_disks_from_storagecontroller(self, handle, storagecontroller):
        '''Get UCS StorageLocalDisk list from specified StorageController via established connection handle, sorted by Dn.
        Return a list of StorageLocalDisk ManagedObjects'''
        return sorted(handle.ConfigResolveChildren(StorageLocalDisk.ClassId(), storagecontroller.Dn, None).OutConfigs.GetChild(), key=lambda disk: disk.Dn)

class Disk:
    def __init__(self, handle, disk, stkctrl):
        self.Id = disk.Id
        self.stkctrl = stkctrl
        self.Model = disk.Model
        self.Sku = ""
        self.Name = ""
        self.Manuf = disk.Vendor
        
        CatalogElem = stkctrl.blade.chassis.system.Catalog.IsCatalogElem(self.Model, disk.Revision, disk.Vendor)
        if CatalogElem == -1:
            CatalogElem = stkctrl.blade.chassis.system.Catalog.CatalogAddElem(self.Model, disk.Revision, disk.Vendor)  
        self.Sku = CatalogElem.Sku
        self.Name = CatalogElem.Name
        
            
class Adaptor:
    def __init__(self, handle, adaptor, blade):
        self.Id = adaptor.Id
        self.Model = adaptor.Model
        self.Sku = ""
        self.Name = ""
        self.Blade = blade
        
        CatalogElem = blade.chassis.system.Catalog.IsCatalogElem(self.Model, adaptor.Revision, adaptor.Vendor)
        if CatalogElem == -1:
            CatalogElem = blade.chassis.system.Catalog.CatalogAddElem(self.Model, adaptor.Revision, adaptor.Vendor)  
        self.Sku = CatalogElem.Sku
        self.Name = CatalogElem.Name

class MemDimm:
    def __init__(self, handle, dimm, blade):
        self.Id = dimm.Id
        self.Model = dimm.Model
        self.Sku = ""
        self.Name = ""
        self.Capa = dimm.Capacity
        self.Clock = dimm.Clock
        self.Blade = blade
       
        CatalogElem = blade.chassis.system.Catalog.IsCatalogElem(self.Model, dimm.Revision, dimm.Vendor)
        if CatalogElem == -1:
            CatalogElem = blade.chassis.system.Catalog.CatalogAddElem(self.Model, dimm.Revision, dimm.Vendor)  
        self.Sku = CatalogElem.Sku
        self.Name = CatalogElem.Name
        
    def __hash__(self):
        return hash(self.Sku)
        
    def __eq__(self, other):
        return (self.Sku) == (other.Sku)

def main():
    
    output_file = ""
    
    parser = argparse.ArgumentParser(prog='UCS_inv2.py', description='Write UCS system inventory information to text or xls file.')
    parser.add_argument('-i', '--ip', dest='ip', action='store', required=True,
        help='UCS IP address')
    parser.add_argument('-u', '--username', dest='username', action='store', required=True,
        help='UCS Account Username')
    parser.add_argument('-p', '--password', dest='password', action='store', required=True,
        help='UCS Account Password')
    parser.add_argument('-d', '--display', choices=['yes', 'no'], default='yes',
        help='Display the UCS System information to console')
    parser.add_argument('-x', '--XlsOutFile', help='output file with xls entension')
   
    args = parser.parse_args()
    
    # In case of result is sent to output file, check that the file has xls extension and make unique file name
    if args.XlsOutFile:
        suffix = ".xls";
        if not args.XlsOutFile.endswith(suffix):
            print "\nSCRIPT STOPPED : The output file must have .xls extension."
            exit()
        if os.path.isfile(args.XlsOutFile):
            print "\nWarning : Output file " + args.XlsOutFile + " exists and will be suffixed\n"
            path, name = os.path.split(args.XlsOutFile)
            name, ext = os.path.splitext(name)

            i=1
            file_name = name + "_" + str(i) + ext
            while os.path.exists(file_name) and i<sys.maxint:
                i+=1
                file_name = name + "_" + str(i) + ext
            if not os.path.exists(file_name):
                print "Output file will be : " + file_name + "\n"
                output_file = file_name
            else:
                print "\nSCRIPT STOPPED : No available filename found."
                exit()                    
        else:
            output_file = args.XlsOutFile
      
    try:
        
        UCS_Sys = System(args.ip, args.username, args.password)
        
        if args.display=="yes":
            myDisplay=TextDisplay(UCS_Sys)
            myDisplay.display()
        
        if args.XlsOutFile:
            myDisplay=XLSDisplay(UCS_Sys)
            myDisplay.display(output_file)

                
    except KeyboardInterrupt:
        print "\nThe script has been interrupted ! \n"
    except Exception:
        print(traceback.format_exc())
    
    print "\nScript terminated.\n"

if __name__ == '__main__': 
    main()