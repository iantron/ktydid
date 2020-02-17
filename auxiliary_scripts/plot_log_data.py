#!/usr/bin/env python3

import matplotlib.pyplot as plt
import pandas as pd

df = pd.read_csv('test.csv', sep=' ', quotechar='|')
df.loc[:,'ut']=pd.to_datetime(df.loc[:,'ut'], unit='s')
df = df.set_index('ut')

fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(16,10), sharex=True)

df1 = df.loc[:,['thrust']]
df1.plot(ax=axes[0,0])

df2 = df.loc[:,['mean_altitude']]
df2.plot(ax=axes[0,1])

df3 = df.loc[:,['angle_of_attack', 'pitch']]
df3.plot(ax=axes[1,0])

df4 = df.loc[:,['apoapsis_altitude', 'periapsis_altitude']]
df4.plot(ax=axes[1,1])

plt.tight_layout()
fig.savefig('test.png')