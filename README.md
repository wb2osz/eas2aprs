# eas2aprs


## EAS SAME to APRS Message Converter ##

The U.S. [National Weather Service](https://www.weather.gov/nwr/) (NWS) operates more than 1,000 VHF FM radio stations that continuously transmit weather information.  

These stations also transmit special warnings about severe weather, disasters (natural & manmade), and public safety.

Alerts are sent in a digital form known as Emergency Alert System (EAS) Specific Area Message Encoding (SAME).  You can [hear a sample here](https://en.wikipedia.org/wiki/Specific_Area_Message_Encoding).

It is possible to buy radios that decode these messages but what fun is that?  We are ham radio operators so we want to build our own from stuff that we already have sitting around.

It has been suggested that retransmitting these alerts over the APRS network could aid in local situational awareness.   

This is not difficult.  

There are already various open source packages to demodulate these sounds and decipher the resulting text.  We just need to gather some of those components and add a little software “glue” to hold them together.

Here is one possible approach.
