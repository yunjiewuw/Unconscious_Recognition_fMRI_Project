from psychopy import visual, event, gui, data, core
from glob import glob
import time
import os 
import random
import pandas as pd
import numpy as np
import datetime
import pickle
from screeninfo import get_monitors

#screen setting
Psychopy_Monitor_Name = "Goggle" # for fMRI
Monitors = get_monitors()
width = Monitors [0].width
height = Monitors[0].height

##Path setting
CFS_path='CFS' 
image_path= 'images'
result_path='results'
log_path=os.path.join(result_path,'log')
position=[(-400,0),(400,0)] #parameter varies according to screensize and screen extension
pickle_path=os.path.join(result_path, 'MRI', 'subject_data.pickle')

##experimental date
date=datetime.datetime.today().strftime('%Y-%m-%d')#-%H:-%M:-%S
de='initial'

# Save or create a pickle file for this subject (change name/ delete for each new subject)
if not os.path.exists(pickle_path):
    print("please run the log creation for this subject first")
    
else:
    # The pickle file already exists, load its content
    with open(pickle_path, "rb") as pickle_file:
        subject_data = pickle.load(pickle_file)
        dlg = gui.DlgFromDict(subject_data, title='2. POS ADJUSTING', fixed=['Date'], order=['sub_ID','Dominant_eye','Date'])
        
        if dlg.OK:
            subid = int(dlg.data[0])
            de = dlg.data[1]
            
            # Save the dictionary to the pickle file
            with open(pickle_path, "wb") as pickle_file:
                pickle.dump(subject_data, pickle_file)
            print('pickle saved. Experiment starts!')
        else:
            print('user cancelled')

## binocular stimulus control 
if de=='Left':
    dominant_position=position[0] #left square
    nondominant_position=position[1] #right square
else:
    dominant_position=position[1] #right square
    nondominant_position=position[0] #left square
    
## make a text file to save data
fileName = 'sub'+str(subject_data['sub_ID']) + '_'+str(subject_data['Date'])

# Create a window
#win=visual.Window(size=[1440, 900],units="pix",fullscr=True, color=[0, 0, 0]) #w
win = visual.Window(size=[2*width, height], fullscr=False, screen=0,
    pos = [0,0], winType='pyglet', allowGUI=False, allowStencil=False,
    monitor=Psychopy_Monitor_Name, colorSpace='rgb',
    blendMode='avg', useFBO=True, units='deg', color=[0,0,0])
win.setMouseVisible(False)

# Create two boxes
example_image_path=os.path.join(image_path,'example.jpg')

img1 = visual.ImageStim(win=win, units="pix", size=(100,100)) #stimulus (always) #left=non-dominant eye
img2 = visual.ImageStim(win=win, units="pix", size=(100,100)) #stimulus #right=dominant eye
img1.setImage(example_image_path)
img2.setImage(example_image_path)
                              
fixation1 = visual.Circle(win, size = 5, units="pix", lineColor = 'red', fillColor = 'red')
fixation2 = visual.Circle(win, size = 5, units="pix", lineColor = 'red', fillColor = 'red')

box_outline_1=visual.rect.Rect(win, width=128, height=128, units="pix", lineWidth=5, lineColor='white', fillColor=None, fillColorSpace=None)
box_outline_2=visual.rect.Rect(win, width=128, height=128, units="pix", lineWidth=5, lineColor='white', fillColor=None, fillColorSpace=None)

msg1= visual.TextStim(win, text= 'when fusing, press LEFT to quit!', units="pix")
msg2= visual.TextStim(win, text= 'when fusing, press LEFT to quit!', units="pix")

# Set the amount of movement per key press
movement_amount = 5

# Start the fusion adjustment loop


keys=[]
distance=0
# Getting response from CurrentDesign response box
while True:
    getkey=event.getKeys(keyList=['1','2','6'])
    keys +=getkey 
    # Check for key press

    if len(keys) == 0:
        box_outline_1.pos= dominant_position
        img1.pos= dominant_position
        fixation1.pos= dominant_position
        msg1.pos= (dominant_position[0],230)
        
        box_outline_2.pos= nondominant_position
        img2.pos= nondominant_position
        fixation2.pos= nondominant_position
        msg2.pos= (nondominant_position[0],230)
        
        box_outline_1.draw()
        img1.draw()
        fixation1.draw()
        msg1.draw()
    
        box_outline_2.draw()
        img2.draw()
        fixation2.draw()
        msg2.draw()
        win.flip()
        
    else:
        # Adjust nondominant eye's box positions based on arrow Current Design Key Input
        # While dominant eye's box position remain fixed
        if '1' in getkey:
            distance-= movement_amount
            box_outline_2.pos= (nondominant_position[0]+distance, nondominant_position[1])
            img2.pos= (nondominant_position[0]+distance, nondominant_position[1])
            fixation2.pos= (nondominant_position[0]+distance, nondominant_position[1])
            msg2.pos=(nondominant_position[0]+distance, 230)
            
            box_outline_1.draw()
            img1.draw()
            fixation1.draw()
            msg1.draw()
    
            box_outline_2.draw()
            img2.draw()
            fixation2.draw()
            msg2.draw()
            win.flip()
    
        elif '2' in getkey:
            distance+= movement_amount
            box_outline_2.pos= (nondominant_position[0]+distance, nondominant_position[1])
            img2.pos= (nondominant_position[0]+distance, nondominant_position[1])
            fixation2.pos= (nondominant_position[0]+distance, nondominant_position[1])
            msg2.pos=(nondominant_position[0]+distance, 230)
            
            box_outline_1.draw()
            img1.draw()
            fixation1.draw()
            msg1.draw()
    
            box_outline_2.draw()
            img2.draw()
            fixation2.draw()
            msg2.draw()
            win.flip()
        
    if '6' in keys:
        print("quitting")
        break  # Exit the loop if space key is pressed
            

# Report the final fusing location of the boxes
print("img2 position:", img2.pos)
print("box_outline2 position:", box_outline_2.pos)
print("fixation2 position:", fixation2.pos)

with open(pickle_path, "rb") as pickle_file:
    subject_data = pickle.load(pickle_file)
    subject_data['r_y_pos']=img2.pos[0]

    # Save the dictionary to the pickle file
    with open(pickle_path, "wb") as pickle_file:
        pickle.dump(subject_data, pickle_file)
        print('pickle saved and r_y_pos updated')

# Close the window
win.close()
core.quit()
