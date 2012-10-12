""" capgen.py
    Generates standard capacitor symbols using the configuration found
    in capgen.conf.  Makes both a horizontal and a vertical version.
    Will not overwrite an exisiting symbol. """

# -------------------------- Begin configuration ---------------------

hfile = 'capgen_h.tpl' # Horizontal capacitor template
vfile = 'capgen_v.tpl' # Vertical capacitor template
confile = 'capgen.conf' # Specific capacitor configuration file
""" Fill in the naming convention for footprints """
footdict = {'1206_capacitor.fp':'1206',
            '0603_capacitor.fp':'0603'}
""" Fill in the naming convention for dielectrics """
dieldict = {'x7r':'x7r',
            'x5r':'x5r',
            'np0':'np0',
            'c0g':'c0g'}

# -------------------------- End configuration -----------------------
import os
import math
import shutil

""" getconf()
    Open the capacitor configuration file and return its contents in a
    dictionary """
def getconf():
    if (not os.access(confile,os.F_OK)):
        print ('getconf: could not find the configuration file ' + confile)
        return
    capdict = {}
    fin = open(confile,'r')
    rawfile = fin.read()
    for line in rawfile.split('\n'):
        if line.strip().startswith('value'):
            capdict['value'] = line.split('=')[1].strip()
        if line.strip().startswith('dielectric'):
            capdict['dielectric'] = line.split('=')[1].strip()
        if line.strip().startswith('voltage'):
            capdict['voltage'] = line.split('=')[1].strip()
        if line.strip().startswith('precision'):
            capdict['precision'] = line.split('=')[1].strip()
        if line.strip().startswith('part'):
            capdict['part'] = line.split('=')[1].strip()
        if line.strip().startswith('footprint'):
            capdict['footprint'] = line.split('=')[1].strip()
    return capdict

""" makename(dictionary containing capacitor characteristics)
    Creates the filename from the parameters.
    --- Every value will have three significant figures.
    --- Name examples: 1u0_x7r_50v_1206.sym, 2n2_np0_20v_1206 """
def makename(capdict):
    value = float(capdict['value'])
    if (value * 1e6 >= 1): # Value is above 1uf
        uval = int(math.floor(value * 1e6))
        nval = int((value - uval/1e6) * 1e9)
        name = str(uval) + 'u' + str(nval)
    elif (value * 1e9 >= 1): # Value is above 1nf
        nval = int(math.floor(value * 1e9))
        pval = int(round((value - nval/1e9) * 1e12))
        name = str(nval) + 'n' + str(pval)
    elif (value * 1e12 >= 1): # Value is above 1pf
        pval = int(math.floor(value * 1e12))
        name = str(pval) + 'p'
    while len(name) < (int(capdict['precision']) + 1):
        name += '0' # Pad to specified precision
    while len(name) > (int(capdict['precision']) + 1):
        if name.endswith(('u','n','p')):
            break
        else:
            name = name[0:-1] # Reduce to specified precision
    name += '_' + dieldict[capdict['dielectric']]
    name += '_' + capdict['voltage'] + 'v'
    name += '_' + footdict[capdict['footprint']]
    return name

""" makevalue(dictionary containing capacitor characteristics)
    Format the capacitor value from the configuration file into the
    string shown on a schematic. """
def makevalue(capdict):
    value = float(capdict['value'])
    if (value * 1e6 >= 1): # Value is above 1uf
        uval = int(math.floor(value * 1e6))
        nval = int((value - uval/1e6) * 1e9)
        valstr = str(uval) + '.' + str(nval)
        while len(valstr) < (int(capdict['precision']) + 1):
            valstr += '0' # Pad to specified precision
        while len(valstr) > (int(capdict['precision']) + 1):
            valstr = valstr[0:-1] # Reduce to specified precision
        if valstr.endswith('.'):
            valstr = valstr[0:-1] # Get rid of the decimal point
        valstr += 'u'
    elif (value * 1e9 >= 1): # Value is above 1nf
        nval = int(math.floor(value * 1e9))
        pval = int(round((value - nval/1e9) * 1e12))
        valstr = str(nval) + '.' + str(pval)
        while len(valstr) < (int(capdict['precision']) + 1):
            valstr += '0' # Pad to specified precision
        while len(valstr) > (int(capdict['precision']) + 1):
            valstr = valstr[0:-1] # Reduce to specified precision
        if valstr.endswith('.'):
            valstr = valstr[0:-1] # Get rid of the decimal point
        valstr += 'n'
    elif (value * 1e12 >= 1): # Value is above 1pf
        pval = int(math.floor(value * 1e12))
        valstr = str(pval) + '.'
        while len(valstr) < (int(capdict['precision']) + 1):
            valstr += '0' # Pad to specified precision
        while len(valstr) > (int(capdict['precision']) + 1):
            valstr = valstr[0:-1] # Reduce to specified precision
        if valstr.endswith('.'):
            valstr = valstr[0:-1] # Get rid of the decimal point
        valstr += 'p'
    return valstr

""" makehorz(dictionary containing capacitor characteristics)
    Make the horizontal symbol """
def makehorz(capdict):
    outname = capdict['name'] + '_horz.sym'
    if os.access(outname,os.F_OK):
        print ('capgen.makehorz: ' + outname + ' already exists.')
        return
    else:
        print('capgen.makehorz: creating ' + outname)
        fot = open(outname,'w')
        fot.close() # Just touch the file -- don't leave it open
        shutil.copyfile(hfile,outname)
        fot = open(outname,'a') # Open for appending
        fot.write('T 0 1400 8 10 0 0 0 0 1' + '\n') # Footprint
        fot.write('footprint=' + capdict['footprint'] + '\n')
        fot.write('T 0 1195 8 10 0 0 0 0 1' + '\n') # Part number
        fot.write('part=' + capdict['part'] + '\n')
        fot.write('T 1200 0 8 10 1 1 0 0 1' + '\n') # Value
        fot.write('value=' + makevalue(capdict) + '\n')
        fot.close()
    return

""" makevert(dictionary containing capacitor characteristics)
    Make the vertical symbol """
def makevert(capdict):
    outname = capdict['name'] + '_vert.sym'
    if os.access(outname,os.F_OK):
        print ('capgen.makevert: ' + outname + ' already exists.')
        return
    else:
        print('capgen.makevert: creating ' + outname)
        fot = open(outname,'w')
        fot.close() # Just touch the file -- don't leave it open
        shutil.copyfile(vfile,outname)
        fot = open(outname,'a') # Open for appending
        fot.write('T 100 1400 8 10 0 0 0 0 1' + '\n') # Footprint
        fot.write('footprint=' + capdict['footprint'] + '\n')
        fot.write('T 100 1200 8 10 0 0 0 0 1' + '\n') # Part number
        fot.write('part=' + capdict['part'] + '\n')
        fot.write('T 500 400 8 10 1 1 0 0 1' + '\n') # Value
        fot.write('value=' + makevalue(capdict) + '\n')
        fot.close()
    return


""" main() """
def main():
    capdict = getconf()
    capdict['name'] = makename(capdict)
    makehorz(capdict)
    makevert(capdict)

if __name__ == "__main__":
    main()
