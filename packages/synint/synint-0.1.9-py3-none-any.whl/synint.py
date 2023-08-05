import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from math import *
from decimal import Decimal

def SynInt(Y,s):
  C = []
  SI = []
  Ix = []
  gradient = []
  lY = len(Y)
  sVal = s
  for i in list(range(0,lY-s)):
    A = Y[i:(i+(s))].mean()
    B = Y[(i+s):(i+2*s)].mean()
    DY = (B-A)
    Indx = i+s
    Ix.append(Indx)
    C.append(DY)
    SI.append(np.sum(C))
  bVal = Y[int(np.floor(.5*s)):int(np.ceil(1.5*s))].mean()
  mVal = 1/s
  trIter = 10000
  j = 0
  Dm_hold = 1
  delta_M = 1
  reduction = 100
  for i in range(trIter): 
    SIm = SI[0:lY]
    SIm = np.multiply(SIm,mVal)
    SIm = list(map(lambda x: x + bVal, SIm))
    e = np.subtract(Y[(s):(lY)],SIm[0:lY])
    e = np.power(e,2)
    sum_error = np.sum(e)
    Dm = (2/lY)*sum_error
    if np.abs(reduction) < .000001:
      break
    reduction = np.abs(Dm_hold) - np.abs(Dm)
    if reduction < 0:
      delta_M = -delta_M
      j = j+i      
    bVal1 = bVal - (bVal*(1/(2*j+2)))*delta_M
    Dm_hold = Dm
    bVal = bVal1
    gradient.append(Dm)
  SI = np.multiply(SI,mVal) + bVal
  SD = np.multiply(C,mVal)
  return(SI,SD,Ix,sVal,bVal)

def SIproject(SI,SD,Ixn,s):
  bookmark = len(Ixn)
  (SDa,SDDb,IDx,sVala,bValb) = SynInt(SD,s)
  DVmin = SDa.min()
  DVmax = SDa.max()
  reverse = 0
  tail = len(SDa)-2*s
  if tail < 0:
    tail = 0
  vDelta = SDa[tail:len(SDa)-2].mean()
  DV1 = SDa[len(SDa)-1]
  DvM = (DV1-vDelta)/s
  Ixlast = Ixn[len(Ixn)-1]
  SIproj = []
  SDproj = []
  prpoints = []
  sdpoints = []
  for p in list(range(0,ceil(s+1))):
    IxAppend = Ixlast+p+1
    if p == 0:
      proj = SI[len(SI)-1]
      sdm = DV1
      proj = proj + sdm
    elif (lastSD <= DVmax and lastSD >= DVmin) and reverse == 0:   
      sdm = p*DvM + DV1
      proj = proj+sdm
    elif reverse == 1:
      sdm = -1 * np.abs(DvM) + lastSD
      proj = proj+sdm
    elif reverse == -1:
      sdm = np.abs(DvM) + lastSD
      proj = proj+sdm   
    SIproj.append(proj)
    SDproj.append(sdm)
    Ixn.append(IxAppend)
    prpoints.append(proj)
    sdpoints.append(sdm)
    lastSD = SDproj[len(SDproj)-1]
    if lastSD > DVmax:
        reverse = 1
    if lastSD < DVmin:
        reverse = -1
        
  SI = np.concatenate((SI, SIproj), axis=0)
  SD = np.concatenate((SD,SDproj), axis = 0)
  IxO = Ixn[0:bookmark]
  return (SI,SD,Ixn,IxO)

def SIforecast(Y_series,FClen,tail_length,spec_index = "auto"):
  Y = np.array(Y_series).reshape(len(Y_series))
  projDatanp = np.empty((0,3), int)
  integrals = list(range(3,(FClen+3),1))
  iter = len(integrals)
  for itr in list(range(0,iter)):
    SIlast = []
    castnum = []
    indexP = []
    s = integrals[itr]
    (SI,SD,Ix,sVal,bVal) = SynInt(Y,s)
    maxLength = len(SI)-1
    for step in list(range((spec_index),(maxLength+1),1)):
      stepIndex = step
      if spec_index == 0:
        tail_length = 0      
      (SIa,SDa,Ixna,IxOa) = SIproject(SI[(stepIndex-tail_length):stepIndex],SD[(stepIndex-tail_length):stepIndex],Ix[(stepIndex-tail_length):stepIndex],s)
      SIlast.append(SIa[len(SIa)-1])
      endpoint = np.array(SIlast)
      indexP.append(Ixna[len(Ixna)-1].astype(int))
      castnum.append(s)
      projDataStep = np.array((indexP, endpoint,castnum)).transpose()
    projDatanp = np.concatenate((projDatanp, projDataStep), axis=0)
  projData = pd.DataFrame(projDatanp)
  return(projData)

def aggProcess(projData,tdata,FClen):
  pcl = projData
  indices = projData.loc[:,'index'].unique()
  dimension = list(range(0,len(indices)))

  index_f = []
  p_count = []
  pvals = []
  forecast = []
  upperbound = []
  lowerbound = []
  mprojection = []
  xincr = 1

  for i in dimension:
    pcl_s = pcl.loc[pcl['index'] == indices[i]]
    maxstep = np.max(pcl_s['SI_val'])
    minstep = np.min(pcl_s['SI_val'])
    avgstep = np.mean(pcl_s['SI_val'])
    ix_ct = len(pcl_s['SI_val'])
    try:
      tsval = tdata['y_col'].loc[tdata['index_a'] == indices[i]].values[0]
      pval = len(pcl_s['SI_val'].loc[pcl_s['SI_val'] < tsval].values)/ix_ct
    except:
      xincr = xincr + 1/(10*FClen)
      pval = .5 - (.5 - pval)/(xincr)
    fcast = pcl_s['SI_val'].quantile(pval)

    index_f.append(indices[i])
    p_count.append(ix_ct)
    pvals.append(pval)
    forecast.append(fcast)
    upperbound.append(maxstep)
    lowerbound.append(minstep)
    mprojection.append(avgstep)

  DataStep = np.array((index_f,p_count,pvals,forecast,upperbound,lowerbound,mprojection)).transpose()

  aggdata = pd.DataFrame(DataStep)
  aggdata = aggdata.rename(columns={0: "index_f", 1: "p_count", 2: "pval",3:"forecast",4:"upperbound",5:"lowerbound",6:"mprojection"})
  return aggdata

def gt_forecast(tdata,FClen,cat_id):
  tdata.loc[:,'index_a'] = np.arange(tdata.shape[0]) + 1
  Y_series = tdata['y_col']
  tail = (2*FClen)
  start = len(Y_series)-tail - 10
  projData = SIforecast(Y_series,FClen,tail,start)
  projData.columns = ["index","SI_val","stepnum"]
  gt_model = aggProcess(projData,tdata,FClen)

  gt_model['cat_id'] = cat_id
  last_index = np.max(tdata["index_a"])
  last_time = np.max(tdata["date"])
  tperiod = "d"

  date_series = pd.Series(pd.period_range(last_time, freq=tperiod, periods=FClen + 1).to_timestamp())[1:]
  index_a_series = pd.Series(list(range(last_index + 1,last_index + FClen +1)))

  frame = { 'index_a': index_a_series.reset_index(drop=True), 'date': date_series.reset_index(drop=True) } 

  append_df = pd.DataFrame(frame) 
  actuals_df = tdata.append([append_df])
  actuals_df['cat_id'] = cat_id

  gt_model["pbiKey"] = gt_model['index_f'].astype(str) + "$" + gt_model['cat_id']
  actuals_df["pbiKey"] = actuals_df['index_a'].astype(str) + "$" + actuals_df['cat_id']

  return (actuals_df,gt_model)

def simple_si_forecast(tdata,FClen,cat_id):
  tdata.loc[:,'index_a'] = np.arange(tdata.shape[0]) + 1
  Y = tdata.loc[:,'y_col']
  (SI,SD,Ix,sVal,bVal) = SynInt(Y,FClen)
  (SIp,SDp,Ixp,Ix) = SIproject(SI,SD,Ix,FClen)
  si_model =  pd.DataFrame({'Ix':Ixp,'SI': SIp, 'SD': SDp})
  si_model.loc[:,"sVal"] = sVal
  si_model.loc[:,"cat_id"] = cat_id
  last_index = np.max(tdata["index_a"])
  last_time = np.max(tdata["date"])
  tperiod = "d"
  date_series = pd.Series(pd.period_range(last_time, freq=tperiod, periods=FClen + 1).to_timestamp())[1:]
  index_a_series = pd.Series(list(range(last_index + 1,last_index + FClen +1)))
  frame = { 'index_a': index_a_series.reset_index(drop=True), 'date': date_series.reset_index(drop=True) } 
  append_df = pd.DataFrame(frame) 
  actuals_df = tdata.append([append_df])
  actuals_df.loc[:,'cat_id'] = cat_id
  si_model["pbiKey"] = si_model['Ix'].astype(str) + "$" + si_model['cat_id']
  actuals_df["pbiKey"] = actuals_df['index_a'].astype(str) + "$" + actuals_df['cat_id'] 
  return(si_model,actuals_df)