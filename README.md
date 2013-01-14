What is Ladybug?
Ladybug is a free and open source environmental plugin for Grasshopper to help designers create an environmentally-conscious architectural design.  The initial step in the design process should be the weather data analysis; a thorough understanding of the weather data will, more likely, lead designers to high-performance design decisions.
Ladybug imports standard EnergyPlus Weather files (.EPW) in Grasshopper and provides a variety of 2D and 3D designer-friendly interactive graphics to support the decision-making process during the initial stages of design. The tool also provides further support for designers to test their initial design options for implications from radiation and sunlight-hours analyses results. Integration with Grasshopper allows for an almost instantaneous feedback on design modifications, and as it runs within the design environment, the information and analysis is interactive.
So much information but… What does it do, put simply?
Ladybug allows you to: import and analyze standard weather data in Grasshopper; draw diagrams like Sun-path, wind-rose, radiation-rose, etc; customize the diagrams in several ways; run radiation analysis, shadow studies, and view analysis for your design inside Grasshopper!
Here is Ladybug in a less than 5-minute video!

Ok! I like it. How do I start?
1.  Download Ladybug:
You can download the components from one of the links below. There are two key points that you should be aware of before you download the ‘bug.
a) Due to the current limitations of Python in Grasshopper there is no simple way to make GHA files from Python scripts so for now I decided to distribute it as UserObjects. For the majority of the time it doesn’t make a big difference for you, as a user. The only problem that you might face, in case you are not a frequent user of Grasshopper, is to have the Python Editor window open, in case you double click on the component. I made a locked version for non-frequent users. However, I suggest that everyone download the unlocked version. The locked version components don’t change color for warnings and errors. You should always have a panel connected to the report output.
b) Ladybug only works on Rhino 5.0. Unfortunately, there is no version for Rhino 4. You can download an evaluation version of Rhino 5 for free. You also need to have GHPython 5.0. 1.0 and Grasshopper 0.9.0014 or higher installed on your system.

Download the unlocked version here!
Download the locked version here! The password is: “whatever” (without quotation marks)

2.	Installation:  There is no installation! After you download the files just drag and drop the files into Grasshopper canvas. You should then see the Ladybug tab in Grasshopper.
Note: If you have an older version of Ladybug already installed you should first manually delete the old files, else the components will be duplicated. You can find the old file in one of the folders below:
C:\Users\%username%\AppData\Roaming\Grasshopper\UserObjects
C:\Documents and Settings\%username%\Application Data\Grasshopper\UserObjects

3.	Check the sample file and watch the videos: If you haven’t watched it yet, watch the video on top of this page.  It shows what Ladybug does; more videos are available on my channel. I will, periodically, capture and upload more videos. There is also a sample file that you can download from here.
Ladybug is great! How can I support it?
1.	Send your feedback: You can comment on the grasshopper group page, create discussions, or email me at thisisladybug [at] gmail [dot] com. Sending comments to the group can get others involved, which is a big plus, but I will always be happy to read your feedbacks via email as well.
2.	Spread the word: Let more people know about Ladybug. Like it on Facebook or follow it on Twitter.
3.	Donate the project:  DONATE!
I know Python. Does it make any difference?
Yes! It does. You can be part of Ladybug development and make a big difference! Simply fork Ladybug repository in GitHub (make a copy of the source code for yourself), or use the unlocked components, develop your own components or modify the available components and share it back to the community. 
How is Ladybug licensed?
  
Ladybug started by Mostapha Sadeghipour Roudsari is licensed under a Creative Commons Attribution-ShareAlike 3.0 Unported License. Based on a work at https://github.com/mostaphaRoudsari/ladybug.
It means you can copy, distribute and transmit the work or remix it to adapt the work. You can also use it to make commercial use of the work, BUT you must attribute that the work is based on Ladybug, and if you alter, transform, or build upon Ladybug, you may distribute the resulting work only under the same or similar license. This process will ensure that Ladybug and its future versions will stay free and accessible for everyone. 
 

Acknowledgments:
I want to thank my friends at Adrian Smith + Gordon Gill Architecture, who helped me so much during the process with their support and comments. Special thanks to Michelle Pak for proofreading much of the text.
I also want to thank Darren Robinson and Christoph Reinhart for their generosity in sharing the latest version of GenCumulativeSky with Ladybug users.
Last, but definitely not least, I want to thank all the amazing Grasshopper community that produced and shared the amazing body of knowledge at Grasshopper3D.com. I learned so much from you guys! Thanks and have fun with the ‘bug! :)
Best, Mostapha
