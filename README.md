# NonlinearDynamicsLab  
  
This is code written by myself for the Nonlinear Dynamics Lab that I am assisting with in the Fall 2022 semester.  
  
FindInconsistencies.py:  
  This python file uses two time-spatial datasets about Sargassum density on the coast. One dataset is from satellite data, and the other is from citizen science eye-witness reports. The purpose of the python file is to find places in which there are inconsistent readings between the citizen science and satellite reports which are close to each other in time and space. Once these places and times are identified, we can graph the time-series to better see the relationship.  
  Addition 1: added an option menu to make searches more modular, and also added plotting a time series as an option using a few parameters  
  
VelocityTracker.py:  
  This program can take a still video and track the velocity of something across it when provided with the measuring length, camera fps, and starting frame. To use, one must first highlight the area containing the measuring length, then highlight the object to be tracked. Will return a velocity over time graph and an average velocity for the object.  
