from ModelDisplay import ModelDisplay
from collections import defaultdict
from xlwt import Workbook, XFStyle, Font, easyxf

class fakeDisk:
    def __init__(self):
        self.Name=''
        self.Sku=''
        self.Manuf=''

class XLSDisplay(ModelDisplay):    
    def __init__(self,system):
        self.system=system
        self.style2=easyxf('font: italic 1, bold 1 ;borders: right thick,')
        self.style3=easyxf('borders: top thick, right thick; align: horiz center')
        self.style4=easyxf('font : bold 1, color red; borders: top thick,right thick')
        self.style5=easyxf('borders: top thick; align: horiz center')
        self.style6=easyxf('font: italic 1, bold 1 ;')
        self.style7=easyxf('align: horiz center')
        self.style8=easyxf('borders: right thick; align: horiz center')
        self.style9=easyxf('borders: left thick; align: horiz center')
        self.style10=easyxf('borders: top thick, left thick; align: horiz center')
        self.style_title=easyxf('font: bold 1, color red;borders:left thick')
        self.inventory = Workbook()
        self.sheet1 = self.inventory.add_sheet('UCS-INVENTORY', cell_overwrite_ok=True)
        self.row_write=2
        self.column_write=0
        self.sheet = defaultdict(lambda:("",easyxf()))

    def write(self,i,j,text,style):
        self.sheet[i,j]=(text,style)

    def change_style(self,i,j,style):
        self.sheet[i,j]=(self.sheet[i,j][0],style)

    def inc(self,name):
        #Equivalent to name++
        setattr(self, name, getattr(self, name) + 1 )
        return getattr(self, name) - 1

    def display_header(self,system):
        title_row = self.sheet1.row(0)
        subtitle_row = self.sheet1.row(1)

        # Chassis columns formating 
        column_num = 0
        self.sheet1.col(column_num).width = 4500
        column_num+=1

        # Server columns formating
        self.sheet1.col(column_num).width = 5500
        self.write(0,column_num, 'Server',self.style_title)
        self.write(1,column_num,'',self.style_title)
        column_num+=1
        self.sheet1.col(column_num).width = 5500
        self.write(1,column_num,'Model',self.style6)
        column_num+=1
        self.sheet1.col(column_num).width = 5500
        self.write(1,column_num,'Serial',self.style2)
        column_num+=1

        # CPU columns formating
        self.write(0,column_num, 'CPU',self.style_title)
        self.write(1,column_num,'# CPU',self.style6)
        self.sheet1.col(column_num).width = 2000
        column_num+=1
        self.write(1,column_num,'CPU model',self.style6)
        self.sheet1.col(column_num).width = 8000
        column_num+=1
        self.write(1,column_num,'Cores',self.style6)
        self.sheet1.col(column_num).width = 2000
        column_num+=1
        self.write(1,column_num,'Speed',self.style2)
        self.sheet1.col(column_num).width = 2000
        column_num+=1

        # RAM columns formating
        self.sheet1.col(column_num).width = 2000
        self.write(0,column_num, 'RAM',self.style_title)
        self.write(1,column_num,'# DIMM',self.style6)
        column_num+=1
        self.sheet1.col(column_num).width = 4500
        self.write(1,column_num,' DIMM size (MB)',self.style6)
        column_num+=1
        self.sheet1.col(column_num).width = 4500
        self.write(1,column_num,'DIMM speed (MHz)',self.style6)
        column_num+=1
        self.sheet1.col(column_num).width = 20000
        self.write(1,column_num,'DIMM name',self.style2)
        column_num+=1
        
        # Storage columns formating
        self.sheet1.col(column_num).width = 15000
        self.write(0,column_num, 'Storage',self.style_title)
        self.write(1,column_num,'RAID ctrl',self.style6)
        column_num+=1
        self.sheet1.col(column_num).width = 20000
        self.write(1,column_num,'DISK ',self.style6)
        column_num+=1
        self.sheet1.col(column_num).width = 10000
        self.write(1,column_num,'DISK pid',self.style6)
        column_num+=1
        self.sheet1.col(column_num).width = 5000
        self.write(1,column_num,'DISK manuf',self.style2)
        column_num+=1
        
        # Adapter columns formating
        self.sheet1.col(column_num).width = 10000
        self.write(0,column_num, 'Adapters',self.style_title)
        self.write(1,column_num,'# Adapter',self.style6)
        column_num+=1
        self.sheet1.col(column_num).width = 10000
        self.write(0,column_num, '',self.style2)
        self.write(1,column_num,'Adapter sku',self.style2)
        column_num+=1
        self.max_column_num=column_num
        
    def display_chassis(self,chas):
        self.write(self.row_write,self.inc("column_write"), chas.Dn ,self.style4)

    def display_blade(self,blade):
        self.write(self.row_write,self.inc("column_write"),blade.Dn,self.style10)
        self.write(self.row_write,self.inc("column_write"),blade.Name,self.style5)
        self.write(self.row_write,self.inc("column_write"),blade.Serial,self.style3)

    def display_proc(self,proc):
        self.write(self.row_write,self.inc("column_write"),len(proc),self.style5)
        self.write(self.row_write,self.inc("column_write"),proc[0].Name,self.style5)
        self.write(self.row_write,self.inc("column_write"),proc[0].Cores,self.style5)
        self.write(self.row_write,self.inc("column_write"),proc[0].Speed,self.style3)


    def display_memory(self,memory):
        tmp=self.row_write
        def_dico_mem = defaultdict(int)
        for elem in memory:
            def_dico_mem[elem] += 1  
        for key, value in def_dico_mem.iteritems():
            self.write(self.row_write,self.inc("column_write"),str(value),self.style5)
            self.write(self.row_write,self.inc("column_write"), key.Capa,self.style5)
            self.write(self.row_write,self.inc("column_write"), key.Clock,self.style5)
            self.write(self.inc("row_write"),self.inc("column_write"), key.Name,self.style3)
        self.next_row_write=self.row_write
        self.row_write=tmp

    def display_storage_controller(self,elem,j):
        if j==0:
            style_elem=self.style5
        else:
            style_elem=self.style7
        self.write(self.inc("row_write"),self.inc("column_write"),elem.Name,style_elem)
     
    def display_disk(self,disk,i):
        if i==0:
            style_sto=self.style5
            style_sto2=self.style3
        else:
            style_sto=self.style7
            style_sto2=self.style8
        self.write(i-1+self.row_write,self.inc("column_write"),disk.Name,style_sto)
        self.write(i-1+self.row_write,self.inc("column_write"),disk.Sku,style_sto)
        self.write(i-1+self.row_write,self.inc("column_write"),disk.Manuf,style_sto2)

    def display_adaptor(self,adp,i):
        if i==0:
            style_adp=self.style5
            style_adp2=self.style3
        else:
            style_adp=self.style7
            style_adp2=self.style8
        self.write(self.row_write,self.inc("column_write"),adp.Name,style_adp)
        self.write(self.inc("row_write"),self.inc("column_write"),adp.Sku,style_adp2)

    def display_end(self,i):
        for j in range(self.max_column_num):
            self.write(i,j,'',self.style5)
        for (i,j) in self.sheet:
            self.sheet1.write(i,j,self.sheet[i,j][0],self.sheet[i,j][1])
        self.inventory.save(self.filename)
        print "\nResults saved in " + self.filename + "\n"

    def display(self,filename):
        self.filename=filename
        self.display_header(self.system)               
        for chas in self.system.Chassis:
            self.column_write=0
            self.display_chassis(chas)
            for blade in chas.Blades:
                self.column_write=1
                self.current_row_write=self.row_write
                self.display_blade(blade)
                self.display_proc(blade.Processors)
                self.display_memory(blade.Memory)
                self.current_column_write=self.column_write
                for j,ctrl in enumerate(blade.StorageCtrls):
                    self.column_write=self.current_column_write
                    self.display_storage_controller(ctrl,j)
                    self.current_column_write_2=self.column_write
                    if len(ctrl.Disks)==0:
                        self.display_disk(fakeDisk(),0)
                    for i,disk in enumerate(ctrl.Disks):
                        self.column_write=self.current_column_write_2
                        self.display_disk(disk,i)
                    self.next_row_write=max(self.next_row_write,self.row_write+max(len(ctrl.Disks),1))
                self.column_write=self.current_column_write+4
                self.row_write=self.current_row_write
                self.current_column_write=self.column_write
                for i,adp in enumerate(blade.Adaptors):
                    self.column_write=self.current_column_write
                    self.display_adaptor(adp,i)
                    self.next_row_write=max(self.next_row_write,self.row_write)
                for i in range(self.current_row_write+1,self.next_row_write-1):
                    for j in (1,4,8,12,16):
                        self.change_style(i,j,self.style9)
                    for j in (2,3,5,6,7,9,10,11,13,14,15):
                        self.change_style(i,j,self.style7)
                    self.change_style(i,17,self.style8)
                self.row_write=self.next_row_write-1
        self.display_end(self.row_write)
