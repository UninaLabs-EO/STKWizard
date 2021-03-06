import numpy as np

from STKBridge.Connection import STK
from STKBridge.eval import evaluator, double_evaluator, winMean_evaluator, winMultiple_evaluator, striano_evaluator

class Pipeline(STK):

     def __init__(self):
          super().__init__()
          print("STK initialized.")
     

     # def genSol(self, X: list):
     #      assert(len(X)==6)
          
     #      a, i, RAAN, NumPlanes, NumSatxPlane, RAANincerement = X 
     #      nSats = NumPlanes * NumSatxPlane

     #      SeedDict = {'a':a, 'e':0,'i':i, 'w':0, 'RAAN':RAAN, 'M':10.5}
     #      ConstDict = {'NumPlanes':NumPlanes, 'NumSatsPerPlane':NumSatxPlane, 'InterPlaneTrueAnomalyIncrement': 5, 'RAANIncrement': RAANincerement, 'ColorByPlane': 'Yes'}
     #      #####################################################
     #      super().addSatellite(SatName='mysat', params=SeedDict)
     #      super().addSensor(SatName='mysat', SenName='Sensor1', params={'coneAngle':15, 'angularResolution':0.1, 'AzEl':[90,-90], 'maxRange':1200})
     #      super().WalkerDelta(SatName='mysat', params=ConstDict)
     #      super().CreateConstellationObject(ConstellationName='Sensors')
     #      super().CreateChainObject(pathObjToAdd=['Constellation/AllUsers', 'Constellation/Sensors'], chainName='Chain')
     #      usersList, AccessDict = super()._computeChain(chainName='Chain')
     #      # mWin, mGap = evaluator(usersList, AccessDict)
     #      # solution_old = [mWin, mGap, ConstDict['NumSatsPerPlane']*ConstDict['NumPlanes']]
     #      # solution_old2 = user_evaluator(usersList, AccessDict, nSats)
     #      score = double_evaluator(usersList, AccessDict, nSats) 
     #      super()._reset()
     #      return score # [score, nUsers]

     def genSol2(self, X: list, reset=True, SELECT = 1, CONE_ANGLE = 50):
          """
          parms: SELECT --> 0: WinMean || 1: WinMultiple || 2: Double Users || 3: Striano Mode
                 CONE_ANGLE --> Coninc Angle of Transmitter/Receiver
          """
          assert(len(X)==4)

          a1, a2, RAAN1, RAAN2 = X 
          nSats = 60
          # Inclination:
          # cos(i) = - (a/12352)^(7/2)

          def computeInc(a):
               cosi = -(a/12352)**(7/2)
               i = np.arccos(cosi)*180/np.pi
               return i

          i1, i2 = computeInc(a1), computeInc(a2)
          NumPlanes, NumSatxPlane = 1, 30
          RAANincerement = 0

          ##################################################### 1st Walker
          SeedDict = {'a':a1, 'e':0,'i':i1, 'w':0, 'RAAN':RAAN1, 'M':10.5}
          ConstDict = {'NumPlanes':NumPlanes, 'NumSatsPerPlane':NumSatxPlane, 'InterPlaneTrueAnomalyIncrement': 0, 'RAANIncrement': RAANincerement, 'ColorByPlane': 'Yes'}
          super().addSatellite(SatName='1seed', params=SeedDict)
          super().addSensor(SatName='1seed', SenName='Sensor1', params={'coneAngle':CONE_ANGLE, 'angularResolution':0.1, 'AzEl':[90,-90], 'maxRange':1200})
          super().WalkerDelta(SatName='1seed', params=ConstDict)

          ##################################################### 2nd Walker
          SeedDict = {'a':a2, 'e':0,'i':i2, 'w':0, 'RAAN':RAAN2, 'M':10.5}
          ConstDict = {'NumPlanes':NumPlanes, 'NumSatsPerPlane':NumSatxPlane, 'InterPlaneTrueAnomalyIncrement': 0, 'RAANIncrement': RAANincerement, 'ColorByPlane': 'Yes'}
          super().addSatellite(SatName='2seed', params=SeedDict)
          super().addSensor(SatName='2seed', SenName='Sensor1', params={'coneAngle':CONE_ANGLE, 'angularResolution':0.1, 'AzEl':[90,-90], 'maxRange':1200})
          super().WalkerDelta(SatName='2seed', params=ConstDict)

          ##################################################### Constellation + Chain
          super().CreateConstellationObject(ConstellationName='Sensors')
          super().CreateChainObject(pathObjToAdd=['Constellation/AllUsers', 'Constellation/Sensors'], chainName='Chain')
          usersList, AccessDict = super()._computeChain(chainName='Chain')
          # mWin, mGap = evaluator(usersList, AccessDict)
          # solution_old = [mWin, mGap, ConstDict['NumSatsPerPlane']*ConstDict['NumPlanes']]
          # solution_old2 = user_evaluator(usersList, AccessDict, nSats)
          
          if SELECT == 0:
               score, nUsers = winMean_evaluator(usersList, AccessDict, nSats)
          elif SELECT == 1:
               score, nUsers = winMultiple_evaluator(usersList, AccessDict, nSats)
          elif SELECT == 2:
               score, nUsers = double_evaluator(usersList, AccessDict, nSats)
          elif SELECT == 3:
               score, nUsers = striano_evaluator(usersList, AccessDict, nSats)
          
          if reset: 
               super()._reset()

          return [score, nUsers] 


     def genSol3(self, X: list, SELECT, reset=True, CONE_ANGLE = 50):
               """
               parms: SELECT --> 0: WinMean || 1: WinMultiple || 2: Double Users || 3: Striano Mode
                    CONE_ANGLE --> Coninc Angle of Transmitter/Receiver
               """
               assert(len(X)==6)

               sat1, sat2, a1, a2, RAAN1, RAAN2 = X 
               nSats = sat1+sat2

               def computeInc(a):
                    cosi = -(a/12352)**(7/2)
                    i = np.arccos(cosi)*180/np.pi
                    return i

               i1, i2 = computeInc(a1), computeInc(a2)
               NumPlanes, NumSatxPlane = 1, sat1
               RAANincerement = 0

               ##################################################### 1st Walker
               if sat1> 0:
                    SeedDict = {'a':a1, 'e':0,'i':i1, 'w':0, 'RAAN':RAAN1, 'M':10.5}
                    ConstDict = {'NumPlanes':NumPlanes, 'NumSatsPerPlane':NumSatxPlane, 'InterPlaneTrueAnomalyIncrement': 0, 'RAANIncrement': RAANincerement, 'ColorByPlane': 'Yes'}
                    super().addSatellite(SatName='1seed', params=SeedDict)
                    super().addSensor(SatName='1seed', SenName='Sensor1', params={'coneAngle':CONE_ANGLE, 'angularResolution':0.1, 'AzEl':[90,-90], 'maxRange':1200})
                    super().WalkerDelta(SatName='1seed', params=ConstDict)

               ##################################################### 2nd Walker
               NumPlanes, NumSatxPlane = 1, sat2
               if sat2 > 0:
                    SeedDict = {'a':a2, 'e':0,'i':i2, 'w':0, 'RAAN':RAAN2, 'M':10.5}
                    ConstDict = {'NumPlanes':NumPlanes, 'NumSatsPerPlane':NumSatxPlane, 'InterPlaneTrueAnomalyIncrement': 0, 'RAANIncrement': RAANincerement, 'ColorByPlane': 'Yes'}
                    super().addSatellite(SatName='2seed', params=SeedDict)
                    super().addSensor(SatName='2seed', SenName='Sensor1', params={'coneAngle':CONE_ANGLE, 'angularResolution':0.1, 'AzEl':[90,-90], 'maxRange':1200})
                    super().WalkerDelta(SatName='2seed', params=ConstDict)

               ##################################################### Constellation + Chain
               super().CreateConstellationObject(ConstellationName='Sensors')
               super().CreateChainObject(pathObjToAdd=['Constellation/AllUsers', 'Constellation/Sensors'], chainName='Chain')
               usersList, AccessDict = super()._computeChain(chainName='Chain')
               # mWin, mGap = evaluator(usersList, AccessDict)
               # solution_old = [mWin, mGap, ConstDict['NumSatsPerPlane']*ConstDict['NumPlanes']]
               # solution_old2 = user_evaluator(usersList, AccessDict, nSats)
               
               if SELECT == 0:
                    score, nUsers = winMean_evaluator(usersList, AccessDict, nSats)
               elif SELECT == 1:
                    score, nUsers = winMultiple_evaluator(usersList, AccessDict, nSats)
               elif SELECT == 2:
                    score, nUsers = double_evaluator(usersList, AccessDict, nSats)
               elif SELECT == 3:
                    score, nUsers = striano_evaluator(usersList, AccessDict, nSats)
               
               if reset: 
                    super()._reset()

               # return score, nUsers, usersList, AccessDict 
               return [score, nUsers] 


     def createReport3(self, X: list, SELECT, reset=True, CONE_ANGLE = 50):
               """
               parms: SELECT --> 0: WinMean || 1: WinMultiple || 2: Double Users || 3: Striano Mode
                    CONE_ANGLE --> Coninc Angle of Transmitter/Receiver
               """
               assert(len(X)==6)

               sat1, sat2, a1, a2, RAAN1, RAAN2 = X 
               nSats = sat1+sat2

               def computeInc(a):
                    cosi = -(a/12352)**(7/2)
                    i = np.arccos(cosi)*180/np.pi
                    return i

               i1, i2 = computeInc(a1), computeInc(a2)
               NumPlanes, NumSatxPlane = 1, sat1
               RAANincerement = 0

               ##################################################### 1st Walker
               if sat1> 0:
                    SeedDict = {'a':a1, 'e':0,'i':i1, 'w':0, 'RAAN':RAAN1, 'M':10.5}
                    ConstDict = {'NumPlanes':NumPlanes, 'NumSatsPerPlane':NumSatxPlane, 'InterPlaneTrueAnomalyIncrement': 0, 'RAANIncrement': RAANincerement, 'ColorByPlane': 'Yes'}
                    super().addSatellite(SatName='1seed', params=SeedDict)
                    super().addSensor(SatName='1seed', SenName='Sensor1', params={'coneAngle':CONE_ANGLE, 'angularResolution':0.1, 'AzEl':[90,-90], 'maxRange':1200})
                    super().WalkerDelta(SatName='1seed', params=ConstDict)

               ##################################################### 2nd Walker
               NumPlanes, NumSatxPlane = 1, sat2
               if sat2 > 0:
                    SeedDict = {'a':a2, 'e':0,'i':i2, 'w':0, 'RAAN':RAAN2, 'M':10.5}
                    ConstDict = {'NumPlanes':NumPlanes, 'NumSatsPerPlane':NumSatxPlane, 'InterPlaneTrueAnomalyIncrement': 0, 'RAANIncrement': RAANincerement, 'ColorByPlane': 'Yes'}
                    super().addSatellite(SatName='2seed', params=SeedDict)
                    super().addSensor(SatName='2seed', SenName='Sensor1', params={'coneAngle':CONE_ANGLE, 'angularResolution':0.1, 'AzEl':[90,-90], 'maxRange':1200})
                    super().WalkerDelta(SatName='2seed', params=ConstDict)

               ##################################################### Constellation + Chain
               super().CreateConstellationObject(ConstellationName='Sensors')
               super().CreateChainObject(pathObjToAdd=['Constellation/AllUsers', 'Constellation/Sensors'], chainName='Chain')
               usersList, AccessDict = super()._computeChain(chainName='Chain')
               # mWin, mGap = evaluator(usersList, AccessDict)
               # solution_old = [mWin, mGap, ConstDict['NumSatsPerPlane']*ConstDict['NumPlanes']]
               # solution_old2 = user_evaluator(usersList, AccessDict, nSats)
               
               if SELECT == 0:
                    score, nUsers = winMean_evaluator(usersList, AccessDict, nSats)
               elif SELECT == 1:
                    score, nUsers = winMultiple_evaluator(usersList, AccessDict, nSats)
               elif SELECT == 2:
                    score, nUsers = double_evaluator(usersList, AccessDict, nSats)
               elif SELECT == 3:
                    score, nUsers = striano_evaluator(usersList, AccessDict, nSats)
               
               if reset: 
                    super()._reset()

               return score, nUsers, usersList, AccessDict 


     def createReport(self, X: list, reset=True):
          assert(len(X)==4)
          
          a1, a2, RAAN1, RAAN2 = X 
          nSats = 60
          # Inclination:
          # cos(i) = - (a/12352)^(7/2)

          def computeInc(a):
               cosi = -(a/12352)**(7/2)
               i = np.arccos(cosi)*180/np.pi
               return i

          i1, i2 = computeInc(a1), computeInc(a2)
          NumPlanes, NumSatxPlane = 1, 30
          RAANincerement = 0

          ##################################################### 1st Walker
          SeedDict = {'a':a1, 'e':0,'i':i1, 'w':0, 'RAAN':RAAN1, 'M':10.5}
          ConstDict = {'NumPlanes':NumPlanes, 'NumSatsPerPlane':NumSatxPlane, 'InterPlaneTrueAnomalyIncrement': 0, 'RAANIncrement': RAANincerement, 'ColorByPlane': 'Yes'}
          super().addSatellite(SatName='1seed', params=SeedDict)
          super().addSensor(SatName='1seed', SenName='Sensor1', params={'coneAngle':60, 'angularResolution':0.1, 'AzEl':[90,-90], 'maxRange':1200})
          super().WalkerDelta(SatName='1seed', params=ConstDict)

          ##################################################### 2nd Walker
          SeedDict = {'a':a2, 'e':0,'i':i2, 'w':0, 'RAAN':RAAN2, 'M':10.5}
          ConstDict = {'NumPlanes':NumPlanes, 'NumSatsPerPlane':NumSatxPlane, 'InterPlaneTrueAnomalyIncrement': 0, 'RAANIncrement': RAANincerement, 'ColorByPlane': 'Yes'}
          super().addSatellite(SatName='2seed', params=SeedDict)
          super().addSensor(SatName='2seed', SenName='Sensor1', params={'coneAngle':60, 'angularResolution':0.1, 'AzEl':[90,-90], 'maxRange':1200})
          super().WalkerDelta(SatName='2seed', params=ConstDict)

          ##################################################### Constellation + Chain
          super().CreateConstellationObject(ConstellationName='Sensors')
          super().CreateChainObject(pathObjToAdd=['Constellation/AllUsers', 'Constellation/Sensors'], chainName='Chain')
          usersList, AccessDict = super()._computeChain(chainName='Chain')
          # mWin, mGap = evaluator(usersList, AccessDict)
          # solution_old = [mWin, mGap, ConstDict['NumSatsPerPlane']*ConstDict['NumPlanes']]
          # solution_old2 = user_evaluator(usersList, AccessDict, nSats)
          # score, nUsers = double_evaluator(usersList, AccessDict, nSats)
          if reset: 
               super()._reset()
          return [usersList, AccessDict] 


     def test(self, X: list):
          assert(len(X)==6)
          
          a, i, RAAN, NumPlanes, NumSatxPlane, RAANincerement = X 

          SeedDict = {'a':a, 'e':0,'i':i, 'w':0, 'RAAN':RAAN, 'M':10.5}
          ConstDict = {'NumPlanes':NumPlanes, 'NumSatsPerPlane':NumSatxPlane, 'InterPlaneTrueAnomalyIncrement': 5, 'RAANIncrement': RAANincerement, 'ColorByPlane': 'Yes'}
          #####################################################
          super().addSatellite(SatName='mysat', params=SeedDict)
          super().addSensor(SatName='mysat', SenName='Sensor1', params={'coneAngle':15, 'angularResolution':0.1, 'AzEl':[90,-90], 'maxRange':1200})
          super().WalkerDelta(SatName='mysat', params=ConstDict)
          super().CreateConstellationObject(ConstellationName='Sensors')
          super().CreateChainObject(pathObjToAdd=['Constellation/AllUsers', 'Constellation/Sensors'], chainName='Chain')
          usersList, AccessDict = super()._computeChain(chainName='Chain')
          mWin, mGap = evaluator(usersList, AccessDict)
          solution = [mWin, mGap, ConstDict['NumSatsPerPlane']*ConstDict['NumPlanes']]
          return solution[0]