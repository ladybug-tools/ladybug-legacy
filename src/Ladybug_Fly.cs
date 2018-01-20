using Rhino;
using Rhino.Geometry;
using Rhino.DocObjects;
using Rhino.Collections;

using GH_IO;
using GH_IO.Serialization;
using Grasshopper;
using Grasshopper.Kernel;
using Grasshopper.Kernel.Data;
using Grasshopper.Kernel.Types;

using System;
using System.IO;
using System.Xml;
using System.Xml.Linq;
using System.Linq;
using System.Data;
using System.Drawing;
using System.Reflection;
using System.Collections;
using System.Windows.Forms;
using System.Collections.Generic;
using System.Runtime.InteropServices;



/// <summary>
/// This class will be instantiated on demand by the Script component.
/// </summary>
public class Script_Instance : GH_ScriptInstance
{
#region Utility functions
  /// <summary>Print a String to the [Out] Parameter of the Script component.</summary>
  /// <param name="text">String to print.</param>
  private void Print(string text) { /* Implementation hidden. */ }
  /// <summary>Print a formatted String to the [Out] Parameter of the Script component.</summary>
  /// <param name="format">String format.</param>
  /// <param name="args">Formatting parameters.</param>
  private void Print(string format, params object[] args) { /* Implementation hidden. */ }
  /// <summary>Print useful information about an object instance to the [Out] Parameter of the Script component. </summary>
  /// <param name="obj">Object instance to parse.</param>
  private void Reflect(object obj) { /* Implementation hidden. */ }
  /// <summary>Print the signatures of all the overloads of a specific method to the [Out] Parameter of the Script component. </summary>
  /// <param name="obj">Object instance to parse.</param>
  private void Reflect(object obj, string method_name) { /* Implementation hidden. */ }
#endregion

#region Members
  /// <summary>Gets the current Rhino document.</summary>
  private readonly RhinoDoc RhinoDocument;
  /// <summary>Gets the Grasshopper document that owns this script.</summary>
  private readonly GH_Document GrasshopperDocument;
  /// <summary>Gets the Grasshopper script component that owns this script.</summary>
  private readonly IGH_Component Component;
  /// <summary>
  /// Gets the current iteration count. The first call to RunScript() is associated with Iteration==0.
  /// Any subsequent call within the same solution will increment the Iteration count.
  /// </summary>
  private readonly int Iteration;
#endregion

  /// <summary>
  /// This procedure contains the user code. Input parameters are provided as regular arguments,
  /// Output parameters as ref arguments. You don't have to assign output parameters,
  /// they will have a default value.
  /// </summary>
  private void RunScript(List<System.Object> _inputSliders, bool _fly, ref object Vviiiiiiiiiizzz)
  {

    /*
    // Open epwmap
    //
    // Ladybug: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
    //
    // This file is part of Ladybug.
    //
    // Copyright (c) 2013-2016, James Ramsedn and Mostapha Sadeghipour Roudsari <Sadeghipour@gmail.com>
    // Ladybug is free software; you can redistribute it and/or modify
    // it under the terms of the GNU General Public License as published
    // by the Free Software Foundation; either version 3 of the License,
    // or (at your option) any later version.
    //
    // Ladybug is distributed in the hope that it will be useful,
    // but WITHOUT ANY WARRANTY; without even the implied warranty of
    // MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
    // GNU General Public License for more details.
    //
    // You should have received a copy of the GNU General Public License
    // along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
    //
    // @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

    */

    Component.Description =
      @"Use Fly to cycle through all connected sliders. If no slider is connects it will cycle through all the sliders in the document!
      Fly is originally posted as a code snippet by David Rutten. The code has been modified by James Ramsedn and Mostapha Sadeghipour Roudsari.

      -
      Provided by Ladybug 0.0.62
      ";

    Component.Params.Input[0].Description = "Connect input sliders. Component will execute all the possible combinations";
    Component.Params.Input[1].Description = "Set to True to let the fly fly!";
    Component.Params.Output[0].Description = "This output has no use for now. Just for making some noise!";
    Component.Name = "Ladybug_fly";
    Component.NickName = "FLY!";
    Component.Category = "Ladybug";
    Component.SubCategory = "5 | Extra";
    Component.Message = "VER 0.0.66\nJAN_20_2018";

    //add a toggle if we need one
    // I comment out this based on some user feedback. It's cool but can be pretty confusing

    /*
    if(Component.Params.Input[1].SourceCount == 0 && Component.Params.Input[0].SourceCount > 0)
    {
    AddToggle();
    }
    */

    if (!_fly)
      return;

    if (_running)
      return;

    _run = true;
    _sliders = _inputSliders;

    GrasshopperDocument.SolutionEnd += OnSolutionEnd;

    // Print(_rtnmessage);
  }

  // <Custom additional code> 

  // icon from this address > http://www.fancyicons.com/free-icon/116/hooligans-icon-set/free-fly-icon-png/

  private bool _run = false;
  private bool _running = false;
  private List<System.Object> _sliders;

  Grasshopper.Kernel.Special.GH_Group grp = new Grasshopper.Kernel.Special.GH_Group();


  private void OnSolutionEnd(object sender, GH_SolutionEventArgs e)
  {
    // Unregister the event, we don't want to get called again.
    e.Document.SolutionEnd -= OnSolutionEnd;

    // If we're not supposed to run, abort now.
    if (!_run)
      return;

    // If we're already running, abort now.
    if (_running)
      return;

    // Reset run and running states.
    _run = false;
    _running = true;

    try
    {
      // Find the Guid for connected slides
      List<System.Guid> guids = new List<System.Guid>(); //empty list for guids
      Grasshopper.Kernel.IGH_Param selSlidersInput = Component.Params.Input[0]; //ref for input where sliders are connected to this component
      IList<Grasshopper.Kernel.IGH_Param> sources = selSlidersInput.Sources; //list of things connected on this input
      bool isAnythingConnected = sources.Any(); //is there actually anything connected?


      // Find connected
      Grasshopper.Kernel.IGH_Param trigger = Component.Params.Input[1].Sources[0]; //ref for input where a boolean or a button is connected
      Grasshopper.Kernel.Special.GH_BooleanToggle boolTrigger = trigger as Grasshopper.Kernel.Special.GH_BooleanToggle;

      if (isAnythingConnected) { //if something's connected,
        foreach (var source in sources) //for each of these connected things:
        {
          IGH_DocumentObject component = source.Attributes.GetTopLevel.DocObject; //for this connected thing, bring it into the code in a way where we can access its properties
          Grasshopper.Kernel.Special.GH_NumberSlider mySlider = component as Grasshopper.Kernel.Special.GH_NumberSlider; //...then cast (?) it as a slider
          if (mySlider == null) //of course, if the thing isn't a slider, the cast doesn't work, so we get null. let's filter out the nulls
            continue;
          guids.Add(mySlider.InstanceGuid); //things left over are sliders and are connected to our input. save this guid.
          //we now have a list of guids of sliders connected to our input, saved in list var 'mySlider'
        }
      }

      // Find all sliders.
      List<Grasshopper.Kernel.Special.GH_NumberSlider> sliders = new List<Grasshopper.Kernel.Special.GH_NumberSlider>();
      foreach (IGH_DocumentObject docObject in GrasshopperDocument.Objects)
      {
        Grasshopper.Kernel.Special.GH_NumberSlider slider = docObject as Grasshopper.Kernel.Special.GH_NumberSlider;
        if (slider != null)
        {
          // check if the slider is in the selected list
          if (isAnythingConnected)
          {
            if (guids.Contains(slider.InstanceGuid)) sliders.Add(slider);
          }
          else sliders.Add(slider);
        }
      }
      if (sliders.Count == 0)
      {
        System.Windows.Forms.MessageBox.Show("No sliders could be found", "<harsh buzzing sound>", MessageBoxButtons.OK);
        return;
      }

      //we now have all sliders
      //ask the user to give a sanity check
      int counter = 0;
      int totalLoops = 1;
      string popupMessage = "";

      // create progress bar by dots and |
      string pb = ".................................................."; //50 of "." - There should be a better way to create this in C# > 50 * "." does it in Python!
      char[] pbChars = pb.ToCharArray();

      foreach(Grasshopper.Kernel.Special.GH_NumberSlider slider in sliders)
      {
        totalLoops *= (slider.TickCount + 1);
        popupMessage += slider.ImpliedNickName;
        popupMessage += "\n";
      }
      if (System.Windows.Forms.MessageBox.Show(sliders.Count + " slider(s) connected:\n" + popupMessage +
        "\n" + totalLoops.ToString() + " iterations will be done. Continue?"+ "\n\n (Press ESC to pause during progressing!)", "Start?", MessageBoxButtons.YesNo) == DialogResult.No)
      {
        SetBooleanToFalse(boolTrigger);
        Component.Message = "Release the fly!";
        return;
      }

      // Set all sliders back to first tick
      foreach (Grasshopper.Kernel.Special.GH_NumberSlider slider in sliders)
        slider.TickValue = 0;

      //start a stopwatch
      System.Diagnostics.Stopwatch sw = System.Diagnostics.Stopwatch.StartNew();

      // Start a giant loop in which we'll permutate our way across all slider layouts.
      while (true)
      {
        int idx = 0;

        // let the user cancel the process
        if (GH_Document.IsEscapeKeyDown())
        {
          if (System.Windows.Forms.MessageBox.Show("Do you want to stop the process?\nSo far " + counter.ToString() +
            " out of " + totalLoops.ToString() + " iterations are done!", "Stop?", MessageBoxButtons.YesNo) == DialogResult.Yes)
          {
            // cancel the process by user input!
            SetBooleanToFalse(boolTrigger);
            Component.Message += "\nCanceled by user! :|";
            return;
          }
        }

        if (!MoveToNextPermutation(ref idx, sliders))
        {
          // study is over!
          SetBooleanToFalse(boolTrigger);
          sw.Stop(); //stop start watch
          UpdateProgressBar(counter, totalLoops, sw, pbChars);
          Component.Message += "\nFinished at " + DateTime.Now.ToShortTimeString();
          break;
        }

        // We've just got a new valid permutation. Solve the new solution.
        counter++;
        e.Document.NewSolution(false);
        Rhino.RhinoDoc.ActiveDoc.Views.Redraw();
        UpdateProgressBar(counter, totalLoops, sw, pbChars);
      }
    }
    catch {
      // "something went wrong!";
    }
    finally {
      // Always make sure that _running is switched off.
      _running = false;
    }
  }

  private bool MoveToNextPermutation(ref int index, List<Grasshopper.Kernel.Special.GH_NumberSlider> sliders)
  {
    if (index >= sliders.Count)
      return false;

    Grasshopper.Kernel.Special.GH_NumberSlider slider = sliders[index];
    if (slider.TickValue < slider.TickCount)
    {
      // Increment the slider.
      slider.TickValue++;
      return true;
    }
    else
    {
      // The current slider is already at the maximum value. Reset it back to zero.
      slider.TickValue = 0;

      // Move on to the next slider.
      index++;

      // If we've run out of sliders to modify, we're done permutatin'
      if (index >= sliders.Count)
        return false;

      return MoveToNextPermutation(ref index, sliders);
    }
  }

  private void SetBooleanToFalse(Grasshopper.Kernel.Special.GH_BooleanToggle boolTrigger)
  {
    if (boolTrigger == null)return;

    grp.Colour = System.Drawing.Color.IndianRed;
    boolTrigger.Value = false; //set trigger value to false
    boolTrigger.ExpireSolution(true);
  }

  private void UpdateProgressBar(int counter, int totalLoops, System.Diagnostics.Stopwatch sw, char[] pbChars)
  {
    // calculate percentage and update progress bar!
    double pecentageComplete = Math.Round((double) 100 * (counter + 1) / totalLoops, 2);

    int lnCount = (int) pecentageComplete / (100 / pbChars.Length); //count how many lines to be changed!

    for (int i = 0; i < lnCount; i++) pbChars[i] = '|';

    string pbString = new string(pbChars);

    // format and display the TimeSpan value
    System.TimeSpan ts = sw.Elapsed;

    string elapsedTime = String.Format("{0:00}:{1:00}:{2:00}.{3:00}",
      ts.Hours, ts.Minutes, ts.Seconds,
      ts.Milliseconds / 10);

    // calculate average run time
    double avergeTime = Math.Round(ts.TotalSeconds / (counter + 1), 2); // average time for each iteration

    double expectedTime = Math.Round((ts.TotalMinutes / (counter + 1)) * totalLoops, 2); // estimation for total runs

    Component.Message = elapsedTime + "\n" + pbString + "\n" + pecentageComplete.ToString() + "%\n"
      + "Average Time: " + avergeTime + " Sec.\n"
      + "Est. Total Time: " + expectedTime + " Min.\n";
  }

  private void AddToggle()
  {
    var toggle = new Grasshopper.Kernel.Special.GH_BooleanToggle();
    toggle.CreateAttributes();
    toggle.Value = false;
    toggle.NickName = "Release the fly...";
    toggle.Attributes.Pivot = new PointF((float) (Component.Attributes.Bounds.Left - 200), (float) (Component.Attributes.Bounds.Top + 30));
    GrasshopperDocument.AddObject(toggle, false);
    Component.Params.Input[1].AddSource(toggle);
    toggle.ExpireSolution(true);

    grp = new Grasshopper.Kernel.Special.GH_Group();
    grp.CreateAttributes();
    grp.Border = Grasshopper.Kernel.Special.GH_GroupBorder.Blob;
    grp.AddObject(toggle.InstanceGuid);
    grp.Colour = System.Drawing.Color.IndianRed;
    grp.NickName = "";
    GrasshopperDocument.AddObject(grp, false);
  }


  // </Custom additional code> 
}