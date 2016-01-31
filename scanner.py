import serial
import io
import Image
import time
import numpy as numpy

class CommunicationsError(Exception):
    def __init__(self, value):
        self.value = value
        
    def __str__(self):
        return repr(self.value)

class microwavescanner:
    portname="/dev/ttyUSB0"
    portspeed=115200
    serialport=serial.Serial(portname,portspeed)
    scanvalues= numpy.zeros([1,1])
    x_min=0
    x_max=0
    x_home=0
    y_min=0
    y_max=0
    y_home=0
    signalstrength_read_count=16
    image_max_value=0
    image_min_value=-1
    image=[]
        
    def __init__(self,portname, oversampling):
        self.portname=portname
        self.serialport=serial.Serial(self.portname,self.portspeed)
        self.x_home=self.RequestValueFromScanner("QHX")
        self.y_home=self.RequestValueFromScanner("QHY")
        self.x_max=self.RequestValueFromScanner("QRX")
        self.y_max=self.RequestValueFromScanner("QRY")
        self.scanvalues=numpy.zeros([self.x_max,self.y_max])
        self.signalstrength_read_count=oversampling
        
    def RequestValueFromScanner(self,requeststring):
        valuestring=self.sendcommand(requeststring)
        return self.GetValueFromString(requeststring,valuestring)
    
    def RequestValueFromScanner_Parameter(self,requeststring,parameter):
        valuestring=self.sendcommand(requeststring+str(parameter))
        return self.GetValueFromString(requeststring,valuestring)    
              
            
    def GetValueFromString(self,requeststring,scanstring):
        value=0.0
        answerstring=str.strip(requeststring,"Q")
        if (str.index(scanstring,answerstring)==0):
            scanstring=scanstring.replace( answerstring,"")
            scanstring=str.strip(scanstring)
            value=int(scanstring)
        else:
            raise CommunicationsError("Expected Response: " + answerstring + " Received: " + scanstring)
        return value
            
    def scan(self):
        self.scanvalues=numpy.zeros([self.x_max+1,self.y_max+1])
        x=self.x_home
        x_direction=1
        if self.x_home>0:
            x_direction=-1
        
        y=self.y_home
        y_direction=1
        self.sendcommand("GH")
        
        if self.y_home>0:
            y_direction=-1
            
        for xcounter in range(self.x_min+1 , self.x_max+1):
            self.sendcommand("GX" + str(x))
            y=self.y_home
            for ycounter in range(self.y_min,self.y_max+1):
                self.sendcommand("GY" +str(y))                
                value=self.RequestValueFromScanner_Parameter("QS",self.signalstrength_read_count)
                self.scanvalues[x,y]=numpy.double(value)
                print "X="+str(x)+ " Y="+ str(y) +" value="+str(self.scanvalues[x,y])
                if (self.image_min_value<0):
                    self.image_min_value=value
                if (value>self.image_max_value):
                    self.image_max_value=value
                if (value<self.image_min_value):
                    self.image_min_value=value                
                y=y+y_direction
                
            #y_direction=y_direction*-1
            x=x+x_direction
    
    def sendcommand(self,commandstring):
        self.serialport.write(commandstring+chr(13))
        return self.serialport.readline()
        
    def makeimage(self):

        img=Image.new('RGB',(self.x_max,self.y_max),"black")
        pixels=img.load()
        
        scale=255.0/(self.image_max_value-self.image_min_value)
        
        for x in range(0,self.x_max):
            for y in range(0,self.y_max):
                val=self.scanvalues[x,y]
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
        numpy.savetxt(filename,self.scanvalues)
    
    def showimage(self):
        if self.image:
            self.image.show()
    
    def park(self):
        self.sendcommand("GH")

def main():
    scanner=microwavescanner("/dev/ttyUSB0",64)
    scanner.scan()
    scanner.park()
    scanner.makeimage()
    #scanner.saveimage("testfile")
    scanner.savedata("testfile"+".csv")
    scanner.showimage()

if __name__ == "__main__":
    main()