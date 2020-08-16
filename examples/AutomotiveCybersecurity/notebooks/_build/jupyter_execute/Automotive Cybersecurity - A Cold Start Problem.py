# 1. Automotive Cybersecurity - A Cold Start Problem

As automotive vehicles are increasingly connected, they face higher risk of being compromised. Especially, their in-vehicle networks are prone to attacks due to original designs with no security concerns in mind and one of the most common attacks is injecting messages to a vehicle’s CAN Bus.

In fact, this received [widespread media attention in 2015](https://www.wired.com/2015/07/hackers-remotely-kill-jeep-highway/) that a Senate bill was proposed in 2015 and [recently reintroduced in 2019](https://www.markey.senate.gov/news/press-releases/senators-markey-and-blumenthal-reintroduce-legislation-to-protect-cybersecurity-on-aircrafts-and-in-cars) to "ensure cybersecurity in increasingly computerized vehicles".

Similar threats exist for aircrafts, smart factories, smart buildings, and of course, the increasing number of IoT appliances. But let’s focus on automotive cybersecurity in this tutorial.

<img src="http://docs.arimo.com/H1ST_AI_Tutorial/img/cyberattacks.png" alt="Cyberattaks" />

Two of the proposed requirement in the SPY Car act are:
  * All  entry  points  to  the  electronic  systems  of  each  motor  vehicle  manufactured  for  sale  in  the  United  States  shall  be  equipped  with  reasonable  measures  to  protect  against hacking attacks
  * Any  motor  vehicle  manufactured  for  sale  in  the  United  States  that  presents  an  entry  point  shall  be  equipped  with  capabilities  to  immediately  detect,  report,  and  stop  attempts  to  intercept  driving data or control the vehicle

It is not obvious that such intrusion detection system (IDS) could work, but it turns out that with careful system design, we can construct it with Human1st.AI. The nature of CAN bus data and vehicle operations is that the normal traffic is highly regular (unlike an open node on the internet) and we can leverage this to build an IDS.

Let's dive in!

### 1a. CAN data basics

Let's familiarize ourselves with vehicle data.

Controller Area Network (CAN Bus) is a common in-vehicle network architecture. It was designed to avoid massive physical wires between Engine Control Units (ECUs) in a vehicle. A CAN packet (also called message)’s payload contains data from one or more ECUs which we refer to as sensors such as Car Speed, Steering Wheel’s Angle, Yaw Rate, Longitudinal Acceleration (Gx), Latitudinal Acceleration (Gy).

CAN Bus’ simple communication protocol makes it vulnerable to cyber-attacks due to security issues such as message broadcasting, no authentication, etc. Injection attacks are common to CAN Bus.

_**NOTE**: we're currently working to make available fully an equivalent dataset to the one used for this tutorial for download. For now the tutorial is read-only. Hold on tight!_

import pandas as pd
import numpy as np

DATA_LOCATION = "COMING-SOON"
df = pd.read_parquet('%s/train/attacks/20181113_Driver1_Trip1-0.parquet' % DATA_LOCATION)

df.head(20)

Note that the data has a particular rhythm to it: each non-NA CarSpeed or YawRate comes at a regular interval, and YawRate/Gx/Gy messages always come with each other. In technical parlance, these are 3 different CAN IDs with different message payloads.

### 1b. Simulating attacks

Now comes the hard & fun part, as we only have normal data. How can we develop an intrusion detection system?

The first natural step is to generate attack data. There are many ways to simulate such attacks but the cheapest method is simply to inject fake messages into the stored data stream.

A more realistic (and also more expensive) method to safely simulate attacks is to inject messages directly into the CAN bus while vehicle is stationary (engine on/transmission in park), or when vehicle is in motion in a controlled driving environment / test track [such as conducted by the NHTSA](https://rosap.ntl.bts.gov/view/dot/41006)

For convenience, we have provided the synthetic data. Let’s take a look at it!

yr = df[(df.Timestamp > 300) & (df.Timestamp < 330)].dropna(subset=["YawRate"])
import matplotlib.pyplot as plt
att = yr[yr["Label"] == "Attack"]
normal = yr[yr["Label"] == "Normal"]
plt.plot(normal.Timestamp, normal.YawRate, label="normal")
plt.plot(att.Timestamp, att.YawRate, label="attack")
plt.legend()

The key question is can ML/AD system detect the injected messages from the normal ones?