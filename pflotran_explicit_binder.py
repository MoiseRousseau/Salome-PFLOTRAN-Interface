import h5py
import sys

def bindExplicit(pflotranOut, domain):
  #extract data from pflotran output
  f = h5py.File(pflotranOut, 'r')
  timeStep = [x for x in f.keys() if "Time" in x]
  dataset = [x for x in f[timeStep[0]].keys()]
  f.close()
  
  #get data from domain
  g = h5py.File(domain, 'r')
  nVertices = len(g['Domain/Vertices'])
  nElements = g['Domain/Cell_number'][0]
  nElemDescription = len(g['Domain/Cells'])
  
  #get prefix 
  s = pflotranOut.split('/')[-1]
  s = s.split('.')[:-1]
  prefix = ''
  for x in s: prefix += x
  
  #generate XMF files for each timestep
  count = 0
  for timeStr in timeStep:
    generateXMFFile(prefix, timeStr, dataset, nVertices,
                    nElements, nElemDescription,
                    pflotranOut, domain, count)
    count += 1
  return
    

   
def generateXMFFile(prefix, timeStr, dataset, nVertices, 
                    nElements, nElemDescription, 
                    pflotranOut, domain, count):
  
  print("write "+prefix+'-{0:0>3}.xmf'.format(count))
  #write file
  f = open(prefix+'-{0:0>3}.xmf'.format(count),'w')
  writeHeader(f)
  writeTime(f, timeStr)
  writeTopology(f, nElements, nElemDescription, domain)
  writeGeometry(f, nVertices, domain)
  for attr in dataset:
    writeAttribute(f, attr, pflotranOut, nElements, timeStr)
  writeEnd(f)
  f.close()
  return
  
  
  

def writeTime(f, time):
  t = time.split()[2]
  f.write('<Time Value = "%s" />\n' %(t))
  return
  
def writeHeader(f):
  f.write('<?xml version="1.0" ?>\n')
  f.write("<!DOCTYPE Xdmf SYSTEM \"Xdmf.dtd\" []>\n")
  f.write("<Xdmf>\n<Domain>\n<Grid Name=\"Mesh\">\n")
  return
  
def writeTopology(f, nElem, lenCells, h5domain):
  f.write("<Topology Type=\"Mixed\" NumberOfElements=\"%s\">\n" %(nElem))
  f.write("<DataItem Format=\"HDF\" DataType=\"Int\" Dimensions=\"%s\">\n" %(lenCells))
  f.write("%s:/Domain/Cells\n" %(h5domain))
  f.write("</DataItem>\n</Topology>\n")
  return
  
def writeGeometry(f, n, domain):
  f.write('<Geometry GeometryType="XYZ">\n')
  f.write('<DataItem Format="HDF" Dimensions="{} 3">\n'.format(n))
  f.write('{}:/Domain/Vertices\n'.format(domain))
  f.write('</DataItem>\n</Geometry>\n')
  return
  
def writeAttribute(f, attr, pflotranOut, nCells, timeStr):
  f.write('<Attribute Name="{}" AttributeType="Scalar" Center="Cell">\n'.format(attr))
  f.write('<DataItem Dimensions="{} 1" Format="HDF">\n'.format(nCells))
  f.write('{}:/{}/{}\n'.format(pflotranOut, timeStr, attr))
  f.write('</DataItem>\n</Attribute>\n')
  return

def writeEnd(f):
  f.write("</Grid>\n</Domain>\n</Xdmf>")
  return


  
#def computeCellVelocity(faceVelocity, ):
#  #we need face velocity, cell topology and that's all
#  
#  return velocity
#  
#def computeVelocityAtCenter(pflotranOut,domain):
#  f = h5py.File(pflotranOut, 'r')
#  timeStep = [x for x in f.keys() if "Time" in x]
#  dataset = [x for x in f[timeStep[0]].keys()]
#  f.close()
#  if "Velocity" not in dataset:
#    return
#  
#  return
  
  
if __name__ == '__main__':
  if len(sys.argv) != 3:
    print("Utilisation:")
    print("{} [name_of_PFLOTRAN_output] [name_of_Salome_domain_h5_file]\n".format(sys.argv[0]))
  else:  
  #computeVelocityAtCenter(sys.argv[1], sys.argv[2])
    bindExplicit(sys.argv[1], sys.argv[2])
    print("END")
  

  
