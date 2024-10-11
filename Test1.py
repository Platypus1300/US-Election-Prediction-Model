
import math
import numpy as np
import statistics as st
import matplotlib.pyplot as plt

from tqdm import tqdm


STDError = 0.02
DAY_CHANGE = 0.005
NUM = 100000



RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
LIGHT_BLUE = "\033[1;34m"  # Hellblau
RESET = "\033[0m"





class Party:

  def __init__(self, name):
    self.name = name


class Candidate:

  def __init__(self, name, party):
    self.name = name
    self.party = party


class Poll:

  def __init__(self, result, candidates, num, days):
    self.result = result
    self.normalResult()
    self.candidates = candidates
    self.num = num
    self.days = days
    self.variation = self.calcVariation()


  def normalResult(self):
    factor = 1/sum(self.result)
    for i in range(len(self.result)):
      self.result[i] = factor * self.result[i]

  def calcVariation(self):
    res = self.result[0]
    return math.sqrt((res*(1-res))/(self.num))
  
  def calcChance(self, n, error, candidate):
    i = self.candidates.index(candidate)
    res = self.result[i]
    s = np.random.normal(res, self.variation + error, n)
    count = np.sum(s >= 0.5)
    return count/n
  
  def getResult(self, candidate):
    i = self.candidates.index(candidate)
    return self.result[i]



class Forecast:

  def __init__(self, polls, candidates):
    self.polls = polls
    self.candidates = candidates
    self.result = self.calcAvg()
    self.days = min(poll.days for poll in self.polls)

  def addPoll(self, poll):
    self.polls.append(poll)
    self.result = self.calcAvg()
    self.days = min(poll.days for poll in self.polls)

  def calcAvg(self):
    days = min(poll.days for poll in self.polls)
    result = [0] * len(self.candidates)
    sum = 0
    for poll in self.polls:
      weight = 0.9 ** poll.days
      sum += weight
      for candidate in self.candidates:
        ind = poll.candidates.index(candidate)
        score = poll.result[ind] * weight
        result[ind] += score

    for i in range(len(result)):
      result[i] = result[i]/sum

    return result
    
    
  def calcChance(self, n, error, candidate, advanced):
    i = self.candidates.index(candidate)
    if(advanced == False):
      s = np.random.normal(self.result[i], error, n)
      count = np.sum(s >= 0.5)
      return count/n 
    else:
      #for _ in range(n):
        #a = np.random.normal(self.result[i], error, n)

        #for _ in range(self.days):
        #  day_change = np.random.normal(0, DAY_CHANGE)
        #  a = np.clip(a + day_change, 0, 1)
        #day_change = np.random.normal(0, (self.days ** 0.5) * DAY_CHANGE)
        #a = np.clip(a + day_change, 0, 1)

        #if(a > 0.5):
          #count += 1
      a = np.random.normal(self.result[i], error, n)
      b = np.random.normal(0, (self.days ** 0.5) * DAY_CHANGE, n)
      s = [a[i] + b[i] for i in range(len(a))]
      count = np.sum(np.array(s) >= 0.5)
      return count/n
    
  def simulate(self, error, candidate, advanced):
    i = self.candidates.index(candidate)
    if(advanced == False):
      s = np.random.normal(self.result[i], error)
      if(s > 0.5):
        return True
      else:
        return False
    else:
      #for _ in range(n):
        #a = np.random.normal(self.result[i], error, n)

        #for _ in range(self.days):
        #  day_change = np.random.normal(0, DAY_CHANGE)
        #  a = np.clip(a + day_change, 0, 1)
        #day_change = np.random.normal(0, (self.days ** 0.5) * DAY_CHANGE)
        #a = np.clip(a + day_change, 0, 1)

        #if(a > 0.5):
          #count += 1
      a = np.random.normal(self.result[i], error)
      b = np.random.normal(0, (self.days ** 0.5) * DAY_CHANGE)
      s = a + b
      if(s > 0.5):
        return True
      else:
        return False

    
  
  def printChance(self, n, error, candidate, advanced):
    r = self.calcChance(n, error, candidate, advanced)
    print("Candidate ", candidate.name, "has a ", round(100*r, 2), "% Chance of Winnig. Advaced: ", advanced)

  def printInfo(self, candidate):
    p = self.result[self.candidates.index(candidate)]
    print("The Variation is ", round(100*STDError, 2), "% the polling result was ", round(100*p, 2), "% and ", len(self.polls), " poll were taken into account.")
    self.printChance(NUM, STDError, candidate, False)
    self.printChance(NUM, STDError, candidate, True)
    


class State:

  def __init__(self, name, electoralVotes, forecast, candidates):
    self.name = name
    self.elVotes = electoralVotes
    self.forecast = forecast

  def changeName(self, name):
    self.name = name
  
  def changeElec(self, elec):
    self.elVotes = elec

  def getChance(self, n, error, candidate):
    r = self.forecast.calcChance(n, error, candidate, False)
    return r

  


  


class Model:

  def __init__(self, list, candidates):
    self.states = list
    self.candidates = candidates
    self.ElVotes = self.getElVotes()

  def getElVotes(self):
    return sum(state.elVotes for state in self.states)

  def getStateIndex(self, name):
    state = [state for state in self.states if state.name == name]
    if(len(state) == 0):
       print("State ", name, " not found!")
       return
    return self.states.index(state[0])
    
  def addPollByName(self, poll, name):
     state = [state for state in self.states if state.name == name]
     if(len(state) == 0):
       print("State ", name, " not found!")
       return
     state[0].forecast.addPoll(poll) 

  def simulate(self, error, candidate, advanced):
    count = 0
    for state in self.states:
      if(state.forecast.simulate(error, candidate, advanced)):
        count += state.elVotes
    if(count > 0.5 * self.ElVotes):
      return True, count
    else:
      return False, count
    
  def monteCarlo(self, n, error, candidate, advanced):
    count = 0
    stat = []
    for _ in range(n):
      a, b = self.simulate(error, candidate, advanced)
      count += a
      stat.append(b)
    print("The Candidate ", candidate.name, " won ", round(100 * count/n, 2), "% of Simulations. With a average of ", st.mean(stat), " Electoral Votes. Advanced: ", advanced)
    plt.hist(stat, bins=50, edgecolor='k', alpha=0.7)
    plt.axvline(x=270, color='r', linestyle='--', label='50% Grenze')
    plt.title('Verteilung der Stimmanteile für Kandidat am Wahltag')
    plt.xlabel('Stimmanteil Kandidat')
    plt.ylabel('Anzahl der Simulationen')
    plt.legend()
    plt.show()

  def TrumpVsHarris(self, n, error, advanced):
    count = 0
    stat = []
    for _ in tqdm(range(n)):
      a, b = self.simulate(error, Trump, advanced)
      count += a
      stat.append(b)
    print("Die Wahl wurde ", n, " mal simuliert: \nHarris hat", round(100 * (1 - count/n), 2), "% der Simulationen gewonnen. \nTrump hat ", round(100*count/n, 2), "% der Simulationen gewonnen.")

  def allStates(self, n, error, advanced, sort):
    if (sort == False):
      print("{:<20} {:<10} {:<10} {:<10} {:<10} {:<10} {:<10}".format(
          "Name", "EV", "TrumpChance", "HarrisChance", "TrumpPoll", "HarrisPoll", "Difference"))
      for state in self.states:
        p = state.forecast.calcChance(n, error, Trump, advanced)
        q = state.forecast.result[0]

        # Bestimmen Sie die Farbe für den letzten Eintrag
        last_entry = 200 * (q - 0.5)
        if last_entry > 0:
          last_entry_str = f"{RED}{last_entry:.2f}{RESET}"
        elif (last_entry < 0):
          last_entry_str = f"{LIGHT_BLUE}{-last_entry:.2f}{RESET}"

        else:
          last_entry_str = f"{YELLOW}{last_entry:.2f}{RESET}"

        print("{:<20} {:<10} {:<10.2f} {:<10.2f} {:<10.2f} {:<10.2f} {}".format(
            state.name,
            state.elVotes,
            100 * p,
            100 * (1 - p),
            100 * q,
            100 * (1 - q),
            last_entry_str
        ))
    else:
      polls = []
      for state in self.states:
        polls.append(state.forecast.result[0])
      sorted = []
      differences = [abs(poll - 0.5) for poll in polls]
      for i in range(len(self.states)):
        i = differences.index(min(differences))
        sorted.append(i)
        differences[i] = 10
      print("{:<20} {:<10} {:<10} {:<10} {:<10} {:<10} {:<10}".format(
          "Name", "EV", "TrumpChance", "HarrisChance", "TrumpPoll", "HarrisPoll", "Difference"))
      for i in range(len(self.states)):
        state = self.states[sorted[i]]
        p = state.forecast.calcChance(n, error, Trump, advanced)
        q = state.forecast.result[0]

        # Bestimmen Sie die Farbe für den letzten Eintrag
        last_entry = 200 * (q - 0.5)
        if last_entry > 0:
          last_entry_str = f"{RED}{last_entry:.2f}{RESET}"
        elif (last_entry < 0):
          last_entry_str = f"{LIGHT_BLUE}{-last_entry:.2f}{RESET}"

        else:
          last_entry_str = f"{YELLOW}{last_entry:.2f}{RESET}"

        print("{:<20} {:<10} {:<10.2f} {:<10.2f} {:<10.2f} {:<10.2f} {}".format(
            state.name,
            state.elVotes,
            100 * p,
            100 * (1 - p),
            100 * q,
            100 * (1 - q),
            last_entry_str
        ))


  

class UI:
    def __init__(self, model):
        self.model = model

    def main(self):
        while True:
            try:
                info = input("Enter your order:")
                
                if info.startswith("addPoll"):
                    new = info.strip().split()
                    if len(new) != 5:
                        print("Invalid input. Usage: addPoll <name> <trump> <harris> <days>")
                        continue
                    name = new[1]
                    trump = float(new[2])
                    harris = float(new[3])
                    days = int(new[4])
                    self.model.addPollByName(Poll([trump, harris], cand, 1000, days), name)

                elif info.startswith("Fast"):
                    new = info.strip().split()
                    if len(new) != 2:
                        print("Invalid input. Usage: Fast <n>")
                        continue
                    n = int(new[1])
                    self.model.TrumpVsHarris(n, STDError, False)

                elif info.startswith("State"):
                    new = info.strip().split()
                    if len(new) != 2:
                        print("Invalid input. Usage: State <name>")
                        continue
                    name = new[1]
                    ind = self.model.getStateIndex(name)
                    self.model.states[ind].forecast.printInfo(Trump)

                elif info.startswith("AllStates"):
                  new = info.strip().split()
                  if len(new) != 2:
                    self.model.allStates(100000, STDError, True, False)
                    continue
                  sort = new[1].lower() == "sort"
                  self.model.allStates(100000, STDError, True, sort)

                elif info.startswith("Exit"):
                    print("Exiting program.")
                    break

                else:
                    print("Unknown command. Please try again.")

            except ValueError as e:
                print(f"Invalid input: {e}")
            except IndexError as e:
                print(f"Error: {e}")
            except Exception as e:
                print(f"An unexpected error occurred: {e}")

# Beispiel für die Verwendung der neuen Exit-Funktion
Rep = Party("Republican")
Dem = Party("Democratic")

Trump = Candidate("Donald Trump", Rep)
Harris = Candidate("Kamala Harris", Dem)
cand = [Trump, Harris]

Poll1 = Poll([0.53, 0.47], cand, 1000, 30)
Poll2 = Poll([0.51, 0.49], cand, 750, 28)
Poll3 = Poll([0.47, 0.53], cand, 100, 12)


""" PollAL = Poll([0.58, 0.38], cand, 1000, 26)
PollAK = Poll([0.52, 0.42], cand, 1000, 26)
PollAZ = Poll([0.48, 0.48], cand, 1000, 26)
PollAR = Poll([0.60, 0.36], cand, 1000, 26)
PollCA = Poll([0.36, 0.60], cand, 1000, 26)
PollCO = Poll([0.41, 0.54], cand, 1000, 26)
PollCT = Poll([0.35, 0.61], cand, 1000, 26)
PollDC = Poll([0.07, 0.93], cand, 1000, 26)
PollDE = Poll([0.38, 0.58], cand, 1000, 26)
PollFL = Poll([0.50, 0.46], cand, 1000, 26)
PollGA = Poll([0.48, 0.48], cand, 1000, 26)
PollHI = Poll([0.30, 0.66], cand, 1000, 26)
PollID = Poll([0.64, 0.32], cand, 1000, 26)
PollIL = Poll([0.39, 0.58], cand, 1000, 26)
PollIN = Poll([0.58, 0.38], cand, 1000, 26)
PollIA = Poll([0.53, 0.43], cand, 1000, 26)
PollKS = Poll([0.56, 0.40], cand, 1000, 26)
PollKY = Poll([0.60, 0.36], cand, 1000, 26)
PollLA = Poll([0.59, 0.37], cand, 1000, 26)
PollME = Poll([0.46, 0.51], cand, 1000, 26)
PollMD = Poll([0.33, 0.64], cand, 1000, 26)
PollMA = Poll([0.32, 0.65], cand, 1000, 26)
PollMI = Poll([0.47, 0.49], cand, 1000, 26)
PollMN = Poll([0.45, 0.52], cand, 1000, 26)
PollMS = Poll([0.58, 0.39], cand, 1000, 26)
PollMO = Poll([0.55, 0.42], cand, 1000, 26)
PollMT = Poll([0.55, 0.42], cand, 1000, 26)
PollNE = Poll([0.61, 0.36], cand, 1000, 26)
PollNV = Poll([0.48, 0.48], cand, 1000, 26)
PollNH = Poll([0.45, 0.51], cand, 1000, 26)
PollNJ = Poll([0.39, 0.58], cand, 1000, 26)
PollNM = Poll([0.44, 0.53], cand, 1000, 26)
PollNY = Poll([0.34, 0.63], cand, 1000, 26)
PollNC = Poll([0.49, 0.48], cand, 1000, 26)
PollND = Poll([0.61, 0.35], cand, 1000, 26)
PollOH = Poll([0.51, 0.46], cand, 1000, 26)
PollOK = Poll([0.64, 0.33], cand, 1000, 26)
PollOR = Poll([0.42, 0.55], cand, 1000, 26)
PollPA = Poll([0.48, 0.49], cand, 1000, 26)
PollRI = Poll([0.37, 0.60], cand, 1000, 26)
PollSC = Poll([0.55, 0.42], cand, 1000, 26)
PollSD = Poll([0.62, 0.34], cand, 1000, 26)
PollTN = Poll([0.60, 0.36], cand, 1000, 26)
PollTX = Poll([0.52, 0.45], cand, 1000, 26)
PollUT = Poll([0.55, 0.41], cand, 1000, 26)
PollVT = Poll([0.28, 0.68], cand, 1000, 26)
PollVA = Poll([0.45, 0.51], cand, 1000, 26)
PollWA = Poll([0.38, 0.59], cand, 1000, 26)
PollWV = Poll([0.65, 0.31], cand, 1000, 26)
PollWI = Poll([0.48, 0.48], cand, 1000, 26)
PollWY = Poll([0.67, 0.29], cand, 1000, 26) """

PollAL = Poll([0.58, 0.38], cand, 1000, 26)
PollAK = Poll([0.52, 0.42], cand, 1000, 26)
PollAZ = Poll([0.48, 0.48], cand, 1000, 26)
PollAR = Poll([0.60, 0.36], cand, 1000, 26)
PollCA = Poll([0.36, 0.60], cand, 1000, 26)
PollCO = Poll([0.41, 0.54], cand, 1000, 26)
PollCT = Poll([0.35, 0.61], cand, 1000, 26)
PollDC = Poll([0.07, 0.93], cand, 1000, 26)
PollDE = Poll([0.38, 0.58], cand, 1000, 26)
PollFL = Poll([0.50, 0.46], cand, 1000, 26)
PollGA = Poll([0.48, 0.48], cand, 1000, 26)
PollHI = Poll([0.30, 0.66], cand, 1000, 26)
PollID = Poll([0.64, 0.32], cand, 1000, 26)
PollIL = Poll([0.39, 0.58], cand, 1000, 26)
PollIN = Poll([0.58, 0.38], cand, 1000, 26)
PollIA = Poll([0.53, 0.43], cand, 1000, 26)
PollKS = Poll([0.56, 0.40], cand, 1000, 26)
PollKY = Poll([0.60, 0.36], cand, 1000, 26)
PollLA = Poll([0.59, 0.37], cand, 1000, 26)
PollME = Poll([0.46, 0.51], cand, 1000, 26)
PollMD = Poll([0.33, 0.64], cand, 1000, 26)
PollMA = Poll([0.32, 0.65], cand, 1000, 26)
PollMI = Poll([0.47, 0.49], cand, 1000, 26)
PollMN = Poll([0.45, 0.52], cand, 1000, 26)
PollMS = Poll([0.58, 0.39], cand, 1000, 26)
PollMO = Poll([0.55, 0.42], cand, 1000, 26)
PollMT = Poll([0.55, 0.42], cand, 1000, 26)
PollNE = Poll([0.61, 0.36], cand, 1000, 26)
PollNV = Poll([0.48, 0.48], cand, 1000, 26)
PollNH = Poll([0.45, 0.51], cand, 1000, 26)
PollNJ = Poll([0.39, 0.58], cand, 1000, 26)
PollNM = Poll([0.44, 0.53], cand, 1000, 26)
PollNY = Poll([0.34, 0.63], cand, 1000, 26)
PollNC = Poll([0.49, 0.48], cand, 1000, 26)
PollND = Poll([0.61, 0.35], cand, 1000, 26)
PollOH = Poll([0.51, 0.46], cand, 1000, 26)
PollOK = Poll([0.64, 0.33], cand, 1000, 26)
PollOR = Poll([0.42, 0.55], cand, 1000, 26)
PollPA = Poll([0.48, 0.49], cand, 1000, 26)
PollRI = Poll([0.37, 0.60], cand, 1000, 26)
PollSC = Poll([0.55, 0.42], cand, 1000, 26)
PollSD = Poll([0.62, 0.34], cand, 1000, 26)
PollTN = Poll([0.60, 0.36], cand, 1000, 26)
PollTX = Poll([0.52, 0.45], cand, 1000, 26)
PollUT = Poll([0.55, 0.41], cand, 1000, 26)
PollVT = Poll([0.28, 0.68], cand, 1000, 26)
PollVA = Poll([0.45, 0.51], cand, 1000, 26)
PollWA = Poll([0.38, 0.59], cand, 1000, 26)
PollWV = Poll([0.65, 0.31], cand, 1000, 26)
PollWI = Poll([0.48, 0.48], cand, 1000, 26)
PollWY = Poll([0.67, 0.29], cand, 1000, 26)


ForecastAL = Forecast([PollAL], cand)
ForecastAK = Forecast([PollAK], cand)
ForecastAZ = Forecast([PollAZ], cand)
ForecastAR = Forecast([PollAR], cand)
ForecastCA = Forecast([PollCA], cand)
ForecastCO = Forecast([PollCO], cand)
ForecastCT = Forecast([PollCT], cand)
ForecastDC = Forecast([PollDC], cand)
ForecastDE = Forecast([PollDE], cand)
ForecastFL = Forecast([PollFL], cand)
ForecastGA = Forecast([PollGA], cand)
ForecastHI = Forecast([PollHI], cand)
ForecastID = Forecast([PollID], cand)
ForecastIL = Forecast([PollIL], cand)
ForecastIN = Forecast([PollIN], cand)
ForecastIA = Forecast([PollIA], cand)
ForecastKS = Forecast([PollKS], cand)
ForecastKY = Forecast([PollKY], cand)
ForecastLA = Forecast([PollLA], cand)
ForecastME = Forecast([PollME], cand)
ForecastMD = Forecast([PollMD], cand)
ForecastMA = Forecast([PollMA], cand)
ForecastMI = Forecast([PollMI], cand)
ForecastMN = Forecast([PollMN], cand)
ForecastMS = Forecast([PollMS], cand)
ForecastMO = Forecast([PollMO], cand)
ForecastMT = Forecast([PollMT], cand)
ForecastNE = Forecast([PollNE], cand)
ForecastNV = Forecast([PollNV], cand)
ForecastNH = Forecast([PollNH], cand)
ForecastNJ = Forecast([PollNJ], cand)
ForecastNM = Forecast([PollNM], cand)
ForecastNY = Forecast([PollNY], cand)
ForecastNC = Forecast([PollNC], cand)
ForecastND = Forecast([PollND], cand)
ForecastOH = Forecast([PollOH], cand)
ForecastOK = Forecast([PollOK], cand)
ForecastOR = Forecast([PollOR], cand)
ForecastPA = Forecast([PollPA], cand)
ForecastRI = Forecast([PollRI], cand)
ForecastSC = Forecast([PollSC], cand)
ForecastSD = Forecast([PollSD], cand)
ForecastTN = Forecast([PollTN], cand)
ForecastTX = Forecast([PollTX], cand)
ForecastUT = Forecast([PollUT], cand)
ForecastVT = Forecast([PollVT], cand)
ForecastVA = Forecast([PollVA], cand)
ForecastWA = Forecast([PollWA], cand)
ForecastWV = Forecast([PollWV], cand)
ForecastWI = Forecast([PollWI], cand)
ForecastWY = Forecast([PollWY], cand)



AL = State("Alabama", 9, ForecastAL, cand)
AK = State("Alaska", 3, ForecastAK, cand)
AZ = State("Arizona", 11, ForecastAZ, cand)
AR = State("Arkansas", 6, ForecastAR, cand)
CA = State("California", 54, ForecastCA, cand)
CO = State("Colorado", 10, ForecastCO, cand)
CT = State("Connecticut", 7, ForecastCT, cand)
DC = State("District of Columbia", 3, ForecastDC, cand)
DE = State("Delaware", 3, ForecastDE, cand)
FL = State("Florida", 30, ForecastFL, cand)
GA = State("Georgia", 16, ForecastGA, cand)
HI = State("Hawaii", 4, ForecastHI, cand)
ID = State("Idaho", 4, ForecastID, cand)
IL = State("Illinois", 19, ForecastIL, cand)
IN = State("Indiana", 11, ForecastIN, cand)
IA = State("Iowa", 6, ForecastIA, cand)
KS = State("Kansas", 6, ForecastKS, cand)
KY = State("Kentucky", 8, ForecastKY, cand)
LA = State("Louisiana", 8, ForecastLA, cand)
ME = State("Maine", 4, ForecastME, cand)
MD = State("Maryland", 10, ForecastMD, cand)
MA = State("Massachusetts", 11, ForecastMA, cand)
MI = State("Michigan", 15, ForecastMI, cand)
MN = State("Minnesota", 10, ForecastMN, cand)
MS = State("Mississippi", 6, ForecastMS, cand)
MO = State("Missouri", 10, ForecastMO, cand)
MT = State("Montana", 4, ForecastMT, cand)
NE = State("Nebraska", 5, ForecastNE, cand)
NV = State("Nevada", 6, ForecastNV, cand)
NH = State("New Hampshire", 4, ForecastNH, cand)
NJ = State("New Jersey", 14, ForecastNJ, cand)
NM = State("New Mexico", 5, ForecastNM, cand)
NY = State("New York", 28, ForecastNY, cand)
NC = State("North Carolina", 16, ForecastNC, cand)
ND = State("North Dakota", 3, ForecastND, cand)
OH = State("Ohio", 17, ForecastOH, cand)
OK = State("Oklahoma", 7, ForecastOK, cand)
OR = State("Oregon", 8, ForecastOR, cand)
PA = State("Pennsylvania", 19, ForecastPA, cand)
RI = State("Rhode Island", 4, ForecastRI, cand)
SC = State("South Carolina", 9, ForecastSC, cand)
SD = State("South Dakota", 3, ForecastSD, cand)
TN = State("Tennessee", 11, ForecastTN, cand)
TX = State("Texas", 40, ForecastTX, cand)
UT = State("Utah", 6, ForecastUT, cand)
VT = State("Vermont", 3, ForecastVT, cand)
VA = State("Virginia", 13, ForecastVA, cand)
WA = State("Washington", 12, ForecastWA, cand)
WV = State("West Virginia", 4, ForecastWV, cand)
WI = State("Wisconsin", 10, ForecastWI, cand)
WY = State("Wyoming", 3, ForecastWY, cand)

STATES = [AL, AK, AZ, AR, CA, CO, CT, DE, DC, FL, GA, HI, ID, IL, IN, IA, KS, KY, LA, ME, MD, MA, MI, MN, MS, MO, MT, NE, NV, NH, NJ, NM, NY, NC, ND, OH, OK, OR, PA, RI, SC, SD, TN, TX, UT, VT, VA, WA, WV, WI, WY]

#Forecast1 = Forecast([Poll2, Poll1], cand)

#PEN = State("Pennsylvania", 19, Forecast1, cand)


#STATES = [PEN]

M = Model(STATES, cand)

#Forecast1.printInfo(Trump)
#print("Trump has a Chance of ", round(100*PEN.getChance(Trump), 2),  "% to win the election.")
#Forecast1.printInfo(Harris)
#Forecast1.calcAvg()

#M.addPollByName(Poll3, "Pennsylvania")
#print("Trump has a Chance of ", round(100*PEN.getChance(Trump), 2),  "% to win the election.")
#Forecast1.printInfo(Harris)
#Forecast1.calcAvg()

#print()

#M.monteCarlo(NUM, STDError, Trump, False)

#print()

#M.monteCarlo(NUM, STDError, Trump, True)

#print()

#M.monteCarlo(NUM, STDError, Harris, False)

#print()

#M.monteCarlo(NUM, STDError, Harris, True)

#M.TrumpVsHarris(1000000, STDError, False)

U = UI(M)

U.main()
