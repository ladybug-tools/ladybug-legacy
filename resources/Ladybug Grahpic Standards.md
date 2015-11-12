#LADYBUG GRAPHIC STANDARDS

Below are a list of component characteristics and standards that have been drafted to help ensure that the components have a consistent means of communicating with users.
This communication is important for helping users understand how to use the components and how to solve issues when something has gone wrong.
These standards also help developers communicate with one another in a consistent manner and adherence to these standards will ultimately save all of us time.
Ladybug + Honeybee developers should adhere to the Hard and Fast Rules unless given permission otherwise and should generally strive to follow the Guidelines.


#HARD AND FAST RULES

1) All components should include the ladybug header at the top of the code.  This includes information on the GPL license, descriptions for the inputs/outputs, as well as name/date/and version of the component.  A template for this header can be found [here](https://github.com/mostaphaRoudsari/ladybug/blob/master/resources/Ladybug_Header_Template.py).

2) All components should follow a format for their body that includes a check of the current Ladybug and/or Honeybee version as well as separate functions for input-checking and for running the main function of the component.  A template for this body can be found [here](https://github.com/mostaphaRoudsari/ladybug/blob/master/resources/Ladybug_Body_Template.py).

3) Descriptions of component inputs should include the following information:

* What data type users should input (ie. number, point, brep).
* What the input represents for the component.
* If the input is meant to take the output of another Ladybug component, this other component should be referenced in the description.
* If the input has a default value when nothing is connected, this must be included in the description.

4) All inputs of components will use the following convention of '_' placement for communicating the importance of the input to the user:

* _input : An input that the user is required to provide in order to run the component.  Generally, the number of these inputs should be minimized if there are possible good defaults. (Example of this type of input: _location on the sunpath)
* _ input _ : An input that is important/required for the primary function of the component but for which the component includes a good default value. (Example of this type of input: _ hour _ on the sunpath)
* input_ : A completely optional input or an input that is mostly there to help users customize the output. (Example of this type of input: legendPar_ on the sunpath)

5) Any time that a component relies on a change made in Ladybug_Ladybug or Honeybee_Honeybee, the "#compatibleLBVersion" and/or the "#compatibleHBVersion" in the header must be updated to this version of Ladybug_Ladybug or Honeybee_Honeybee.

6) Components will remain grey when dropped on the canvas but, once any input is connected, the component should use Grasshopper's "Warning" capability (orange component) any time that there is a missing required input or incorrect type of input.  Ideally, all of these warnings are given either before or within the input-checking function of the component (so all warnings are given before getting to the main function).

7) If a component gets to its main function but fails to run to completion, Grasshopper's "Error" capability should be used (ie. an energy simulation was started but failed because of incorrect inputs).  If the component is running to completion and you you only want to give the user information about how the process has run, please use the "readMe!" output (by printing the message) and not any warnings, errors, or remarks.  Grasshopper's "Remark" capability should never be used because it over-rides the color of the component in the case of warnings or errors.

8) Components that produce a graphic output in the Rhino scene will have their preview turned on by default while those that do not produce a graphic output will have their preview turned off.

9) All components will be placed first in WIP and beta tested by the community before being moved to the other tabs.  This will communicate to users that the components are still being vetted and they should use them at their own risk.

10) No one understands best what a specific component should be telling its user better than the developer and those trying to apply it.  Therefore, these standards should be seen as a minimum of what is required and any additional warnings, errors, or information that you realize should be given to the user is desirable and encouraged as long as you are not violating the general structure outlined in this document.




#GUIDELINES

1) Please be mindful of the color schemes and fonts that other developers have implemented on the existing component icons.  Deviating too much from these colors/fonts can compromise the graphic identity of the project.

2) If a given input to a component is one that merits some expert knowledge (like a certain coefficient), it is usually a good idea to include some examples of this in the input description.

3) You should aim to limit the size of your component and the number of outputs.  Remember that users can probably derive similar/redundant outputs with a few native GH components and so you often only need to include one.  Also, if you have similar inputs, it may be useful to add an integer input for "calculation type" that switches between different modes of running the component.  The number of inputs/outputs should always aim to be less than 15.  However, if you have so much that the component does and good reasons for needing more outputs, the largest component in the whole suite currently has 22 outputs. If you are exceeding 15, be prepared with these reasons.

4) If you have one operation that applies to a number of components, you should write this operation into Ladybug_Ladybug or Honeybee_Honeybee.  You should never be copy/pasting a function from another component unless you are going to be modifying that function substantially to be specific for that component's needs.
