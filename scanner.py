import serial
import Image
import time

class microwavescanner:
    portname="/dev/ttyUSB0"
    filename="export.png"
    serialport=serial.Serial(portname)
    scanvalues=[]
    x_min=0
    x_max=0
    y_min=0
    y_max=0
    step_size=0
    image_max_value=0
    image_min_value=100000
    image=[]
    
    
    def __init__(self,portname, filename, x_min, x_max, y_min,y_max, stepsize ):
        self.portname=portname
        self.serialport=serial.Serial(portname)
        initstring=self.serialport.readline()
        print "Received: " + initstring
        if (x_min<x_max):
            self.x_min=x_min
            self.x_max=x_max
        else:
            self.x_min=x_max
            self.x_max=x_min
            
        if (y_min<y_max):
            self.y_min=y_min
            self.y_max=y_max
        else:
            self.y_min=y_max
            self.y_max=y_min
        self.step_size=stepsize
            
    def GetValueFromString(self,scanstring):
        value=0
        #print "Received Analog: " + scanstring
        if (str.index(scanstring,"A")==0):
            scanstring=str.strip(scanstring,"A")
            scanstring=str.strip(scanstring)
            value=int(scanstring)
        return value
            

    def scan(self):
        self.scanvalues=[]
        
        for x in range(self.x_min , self.x_max,self.step_size):
            self.serialport.write("X" + str(x) + chr(13))
            scancolumn=[]
            for y in range(self.y_max,self.y_min,-1*self.step_size):
                self.serialport.write("Y" +str(y)+chr(13))
                value=0
                for r in range(0,4):
                    self.serialport.write("R0"+chr(13))
                    scanstring=self.serialport.readline()
                    value=value+self.GetValueFromString(scanstring)
                print "X="+str(x)+"  value="+str(value)
                scancolumn.append(value)
                if (value>self.image_max_value):
                    self.image_max_value=value
                if (value<self.image_min_value):
                    self.image_min_value=value
            self.scanvalues.append(scancolumn)  
            for y in range (self.y_min,self.y_max,self.step_size):
                self.serialport.write("Y" +str(y)+chr(13))
                time.sleep(0.03)

    def makeimage(self):
        xlen=len(self.scanvalues)
        ylen=len(self.scanvalues[0])
        img=Image.new('RGB',(xlen,ylen),"black")
        pixels=img.load()
        
        scale=255.0/(self.image_max_value-self.image_min_value)
        
        for x in range(0,xlen):
            for y in range(0,ylen):
                val=self.scanvalues[x][y]
                val=val-self.image_min_value
                print "X="+str(x) +" Y="+str(y)+ " Value=" +str(val)  
                val=int(val*scale)
                if val>255:
                    val=255
                    print 'Pixel out of range: Lmited to value 255.'
                if val<0:
                    val=0
                    print 'Pixel out of range. Limited to value 0.' 
                                
                pixels[x,y]=(val,val,val)
        print "min="+str(self.image_min_value) + " max=" + str(self.image_max_value)
        print "scale="+str(scale)
        self.image= img
            
    def saveimage(self, filename):
        self.image.save(filename+"bmp","bmp")
    
    def savedata(self, filename):
        pass
    
    def showimage(self):
        if self.image:
            self.image.show()

def main():
    scanner=microwavescanner("/dev/ttyUSB0","testfile",30,150,30,150,1)
    scanner.scan()
    scanner.makeimage()
    #scanner.saveimage("testfile")
    scanner.savedata("testfile"+".csv")
    scanner.showimage()

if __name__ == "__main__":
    main()