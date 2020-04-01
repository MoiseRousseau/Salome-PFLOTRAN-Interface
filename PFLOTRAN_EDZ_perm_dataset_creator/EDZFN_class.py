import numpy as np
from scipy.special import i0, i1 #bessel function



class EDZFractureNetwork:
  def __init__(self):
    self.iso = True
    self.concentrationParameter = 0
    self.permMatrix = 0
    self.model = None
    self.radius = None
    self.aperture = None
    self.attenuationLength = None
    self.initialDensity = None
    self.matrixCoupling = False
    self.mourzenckoAlpha = 0.037
    self.mourzenckoBeta = 0.155
    self.rho_cr = 2.4
    return
  
  #Set method  
  def setAttenuationLength(self,l):
    self.attenuationLength = l
    return
    
  def setInitialDensity(self,rho_0):
    self.initialDensity = rho_0
    return
    
  def setFractureProperties(self, R, aperture):
    self.radius = R
    self.aperture = aperture
    return
    
  def setMatrixPermeability(self, K):
    self.permMatrix = K
    return
    
  def setAnisotropy(self, K):
    self.iso = False
    self.concentrationParameter = K
    return

  def setEDZModel(self,model):
    possibleModel = ["PERM", "SNOW", "MOURZENCKO_EDZ"]
    if model in possibleModel:
      self.model = model 
    else:
      print('Possible model are: "PERM", "SNOW" and "MOURZENCKO_EDZ".')
    return
    
  def setPermMatrix(self,K):
    self.permMatrix = K
    return
    
  def setMatrixCoupling(self, b):
    self.matrixCoupling = b
    return

  #get method
  def getInitialDensity(self):
    return self.initialDensity
  def getAttLength(self):
    return self.attenuationLength
  def getArea(self):
    return self.area
  def getAperture(self):
    return self.aperture
  def getPermMatrix(self):
    return self.permMatrix
  def getModel(self):
    return self.model
  def getAnisotropy(self):
    return self.iso
  def getMatrixCoupling(self):
    return self.matrixCoupling
    
    
  #initial density calculation
  def computeInitialDensityFromTraceLength(self, traceLength):
    #Mourzenko, V. V., Thovert, J.-F., & Adler, P. M. (2012). Percolation and permeability of fracture networks in excavated damaged zones. Physical Review E, 86(2). doi:10.1103/physreve.86.026312 

    if self.iso:
      res = 4*traceLength / (self.radius**2 * np.pi**2)
    else:
      k = self.concentrationParameter
      l_r = self.attenuationLength / self.radius
      res = 4*traceLength / (self.radius**2 * np.pi**2 * self.__psi_c__(k,l_r))
    
    return res
    
  #Permeability calculation
  #Snow
  def __SnowPermeabilityIso__(rho, A, aperture):
    return rho*A*aperture**3/18
    
  #Mourzencko
  def __MourzenckoPermeabilityIsoReduced__(self,rho_r, a=0.037,b=0.155,rho_cr=2.4):
    #defaut parameter for circular fracture
    if rho_r < rho_cr:
      return 0.0 #not percolating
    else:
      res = a*(rho_r-rho_cr)**2/(1+b*(rho_r-rho_cr))
    return res
    
  #anisotropy correction
  def __AnisotropyMatrix__(self,k):
    perp = self.__psi_perp__(k)
    para = self.__psi_para__(k)
    K = np.array([[perp,0,0],[0,perp,0],[0,0,para]])
    return K
  
  #
  def computePermeability(self, distance, normal, makeRotation=True):
    #angle definition ?
    
    #Threshold for matrix perm
    thres = 0.1
    #compute density
    if not self.initialDensity or not self.attenuationLength:
      print('Density function with distance not set')
      raise ValueError('')
    rho = self.initialDensity * np.exp(-distance/self.attenuationLength)
    #print(rho)
    
    #compute perm
    if not self.radius or not self.aperture:
      print('Fracture properties not set')
      raise ValueError('')
      
    if self.model == 'SNOW':
      K = rho*np.pi*self.radius*self.radius*self.aperture**3/18
      
    elif self.model == 'MOURZENCKO_EDZ':
      #compute reduced parameter
      l_r = self.attenuationLength/self.radius
      rho_r = rho*np.pi*np.pi*self.radius**3
      if not self.iso: 
        rho_r = self.__phi__(self.concentrationParameter,l_r) * rho_r
      K_r = self.__MourzenckoPermeabilityIsoReduced__(rho_r, self.mourzenckoAlpha, self.mourzenckoBeta, self.rho_cr) #add not circular fracture here
      #convert to dimentional permeability
      K = K_r * self.aperture**3 / 12 / self.radius
      #print(K, K_r, rho_r, l_r)
    else:
      print('Model non defined')
      return
    
    if not self.iso:
      K_r_aniso = self.__AnisotropyMatrix__(self.concentrationParameter)
      K = K/self.__phi__(self.concentrationParameter, l_r)*K_r_aniso
    else:
      K_r_iso = np.array([[1,0,0],[0,1,0],[0,0,1]], dtype='f8')
      K = K*K_r_iso
    
    if self.matrixCoupling:
      #advanced coupling
      print('Not implemented yet')
      pass
    else: #simple addition
      K[0,0] += self.permMatrix
      K[1,1] += self.permMatrix
      K[2,2] += self.permMatrix
    
    if makeRotation and not self.iso:
      K = self.__rotatePermeabilityTensor__(K,normal)
    
    return K
      
  
  #rotation
  def __rotatePermeabilityTensor__(self, K, normal_):
    
    #found another vector perpendicular
    #random we don't care as kxx=kyy
    normal = normal_/np.linalg.norm(normal_)
    testVector = np.array([1,1,1])
    u = np.cross(normal,testVector)
    if np.linalg.norm(u) < 1e-4:
      testVector = np.array([-1,2,1])
      u = np.cross(normal,testVector)
    #u = np.array([2*normal[1]*normal[2],-normal[0]*normal[2],-normal[0]*normal[1]])
    u = u/np.linalg.norm(u)
    v = np.cross(normal,u) #we have thus u.v = normal
    
    #base change matrix P
    #we got the local coordinate expressed in the simulation base
    #P is the matrix with local vector coordinate expressed in simulation base in column
    #and X_sim = P X_local
    P = np.append(np.array([u]).T,np.array([v]).T,axis=1)
    P = np.append(P,np.array([normal]).T,axis=1)
    K = P @ K @ P.T
    
    return K
  
  
  #Mourzencko function
  def __psi_c__(self, k,l_reduced):
    E = np.sqrt(k**2+1/l_reduced/l_reduced)
    I01 = i1((E+k)/2) * i0((E-k)/2) + i0((E+k)/2) * i1((E-k)/2)
    res = 2*k/(E*np.sinh(k)) * I01
    return res
    
  def __phi__(self, k,l_reduced):
    psi_c = self.__psi_c__(k,l_reduced)
    psi_c_inf = 2/np.sinh(k) * i1(k)
    phi_inf = 2/(np.sinh(k)**2) * (i0(2*k) - i1(2*k)/k)
    return phi_inf*(psi_c/psi_c_inf)**2
    
  def __psi_perp__(self, k):
    res = 3/2 * (1+(1-k/np.tanh(k))/k/k)
    return res
    
  def __psi_para__(self, k):
    res = 3/k/k * (k/np.tanh(k)-1)
    return res
    
  
 #My reduced parameters
  def computeHydraulicLength(self):
    if self.iso:
      return 'TODO'
    l_r = self.attenuationLength/self.radius
    rho_0r = self.initialDensity * self.__phi__(self.concentrationParameter, l_r)*np.pi**2*self.radius**3
    l = np.log(rho_0r/(2*self.rho_cr))
    return self.attenuationLength*l

  def computeWallPermeability(self):
    if self.iso: 
      return 'TODO'
    else:
      l_r = self.attenuationLength/self.radius
      rho_0r = self.initialDensity * self.__phi__(self.concentrationParameter, l_r)*np.pi**2*self.radius**3
      rho_diff_r = rho_0r - self.rho_cr
      num = ( self.mourzenckoAlpha * rho_diff_r **2 * self.aperture**3 *   
             self.__psi_para__(self.concentrationParameter) )
      den = 12*self.radius * self.__phi__(self.concentrationParameter, l_r) * (1+self.mourzenckoBeta * rho_diff_r )
    return num/den

  def computeAnisoFactor(self):
    if self.iso: return 1
    coth_k = np.cosh(self.concentrationParameter)/np.sinh(self.concentrationParameter)
    num = 2*(self.concentrationParameter*coth_k-1)
    den = self.concentrationParameter**2 - self.concentrationParameter*coth_k+1
    return num/den
    
  def computePermeabilityFromReducedParameter(self, distance, normal):
    return
    
  def printReducedParameter(self):
    print("\nEDZ reduced parameters")
    print("Anisotropy factor: {}".format(self.computeAnisoFactor()))
    print("Hydraulic length: {} m".format(self.computeHydraulicLength()))
    print("Wall permeability: {} m^2".format(self.computeWallPermeability()))
    return


