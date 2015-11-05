#LADYBUG GRAPHIC STANDARDS

Below are a list of component characterists that has been drafted to help ensure that the components have a consistent means of communicating with users.
This communication is important for helping users understand how to use the components and how to solve issues when something has gone wrong.
Ladybug + Honeybee developers should adhere to the Hard and Fast Rules unless given permission therwise and should generally strive to follow the Guidelines.


#HARD AND FAST RULES

1) All components should include the ladybug header at the top of the code.  This includes information on the GPL licence, descriptions for the inputs/outputs, as well as name/date/and version of the component.

2) Descriptions of component inputs should include the folling information:

* What data type users should input (ie. number, point, brep)
* What the input represents for the component
* If the input is meant to take the output of another Ladybug component, this other component should be referenced in the descrition.

3) All inputs of components will use the following convention of '_' placement for communicating with the user about their importantance:

* _ input: An input that the user is required to provide in order to run the component.  Generally, the number of these inputs should be minimized if there are possible good defaults. (example of this type of input: _location on the sunpath)
* _ input _: An input that is important/required for the primary function of the component but for which the component includes a good default value. (example of this type of input: _hour_ on the sunpath)
* input _: A completely optional input or an input that is mostly there to help users customize the output. (example of this type of input: legendPar_ on the sunpath)
	
4) All components should include a check of the current Ladybug and/or Honeybee version unless the component is so short in code length as to be entirely independent of Ladybug+Honyebee.

5) Any time that a component relies on a change made in Ladybug_Ladybug or Honeybee_Honeybee, the "#compatibleLBVersion" in the header must be updated to this version of Ladybug_Ladybug or Honeybee_Honeybee.

6) Components should only use Grasshopper's "Warning" capability (orange component) if the user has input something incorrect that would cause the component to crash or produce an incorrect result.  If you only want to tell the user to input a certain required input or give the user information about how the component is running, please use either the "readMe!" output (the GHPython "print" output) or use Grasshopper's "Remark" capability instead of the "Warning" capability.

7) Components should not purposefully use Grasshopper's "Error" capability.  This shall be reserved for either identifying bugs in our code or for telling the user that they have not put in the right data type to a certain input (ie. a point into a boolean input).

8) All components will use the "Always draw icon" feature of GHPython.  To ensure that this is implemented, right-click on the center of your component, go to the upper-right corner of the menu, and hit the icon there unitl you see a black hexagon.

9) Components that produce a graphic ouput in the Rhino scene will have their preview turned on by default while those that do not produce a graphic output will have their preview turned off.

10) All components will be placed first in WIP and beta tested by the community before being moved to the other tabs.  This will communicate to users that the components are still being vetted and they use them at their own risk.




#GUIDELINES

1) Please be mindful of the color schemes and fonts that other developers have implemented on the existing component icons.  Deviating too much from these colors/fonts can compromise the graphic identiy of the project.

2) If a given input to a component is one that merits some expert knowledge (like a certain coefficient), it is usually a good idea to incude some examples of this.