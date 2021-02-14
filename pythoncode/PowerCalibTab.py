import numpy as np

##################################################################
# I followed this descrition
# https://en.wikipedia.org/wiki/Bilinear_interpolation
# Speed	  W		   W 	   W 	  W   	   W 	   W	   W
#    0	   50	  100	  150	  200	  250	  300
#   10	   46	   97	  145	  194	  245	  285
#   20	   50	  100	  145	  197	  245	  290
#   30	   63	  102	  154	  196	  245	  295
#   40	  105	  120	  160	  210	  260	  305
#   50	  123	  130	  165	  210	  250	  310


def OpenPowerTab(Dateiname):
    try:
        Powertab=np.genfromtxt(Dateiname)
        return Powertab
    except:
        print("No correct Powertable available")




def CalcCorrFactor(Powertab,speed,power):
    try:
        Powertab
    except:
        P=1.0
    else:
        left=int(power/50)  #the power divided by 50W is the left value index
        upper=int(speed/10) #the speed divided by 10kmhis the upper value index 
        
        le=np.clip(left,1,5)    #Limit the Index to the horizontal table size 6
        up=np.clip(upper,1,4)  #Limit the Index to the vertical table size 5
        ri =le+1  #the right is one higher than te left
        lo =up+1 #the lower is one higher than the upper
        Q_12= Powertab[0,le]/Powertab[up,le]   #calculate the corr. factor for this table entry
        Q_11= Powertab[0,le]/Powertab[lo,le]   #calculate the corr. factor for this table entry
        Q_22= Powertab[0,ri]/Powertab[up,ri]   #calculate the corr. factor for this table entry
        Q_21= Powertab[0,ri]/Powertab[lo,ri]   #calculate the corr. factor for this table entry
        x1=Powertab[0,le]       # power of the left value
        x2=Powertab[0,ri]      # power of the right value
        y1=Powertab[lo,0]      # speed of the upper value
        y2=Powertab[up,0]      # speed of the lower value
        x=power
        y=speed
        R_1= (x2-x)/(x2-x1)*Q_11+(x-x1)/(x2-x1)*Q_21 # interpolating the corr. factor between the Left Values
        R_2= (x2-x)/(x2-x1)*Q_12+(x-x1)/(x2-x1)*Q_22 # interpolating the corr. factor between the Right Values
        P= (y2-y)/(y2-y1)*R_1+(y-y1)/(y2-y1)*R_2   # interpolating the result corr. factor from the iterpol.values
    return P

