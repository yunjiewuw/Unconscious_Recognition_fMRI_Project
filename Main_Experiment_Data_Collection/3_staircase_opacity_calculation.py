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

clock=core.Clock()

#screen setting
Psychopy_Monitor_Name = "Goggle" # for fMRI
Monitors = get_monitors()
width = Monitors [0].width
height = Monitors[0].height

# exp parameter 
frequency=10 
initial_contrast=50
de='initial'

#Path setting
CFS_path='CFS' 
image_path= 'images'
result_path='results'
log_path=os.path.join(result_path,'log')
pickle_path=os.path.join(result_path, 'MRI', 'subject_data.pickle')

##experimental date
date=datetime.datetime.today().strftime('%Y-%m-%d') #-%H:-%M:-%S
time=datetime.datetime.today().strftime('%H%M')

# Save or create a pickle file for this subject (change name/ delete for each new subject)
if not os.path.exists(pickle_path):
    print("please run the log creation and location adjustment for the subject first")
    
else:
    # The pickle file already exists, load its content
    with open(pickle_path, "rb") as pickle_file:
        subject_data = pickle.load(pickle_file)
        dlg = gui.DlgFromDict(subject_data, title='3. OPACITY STAIRCASE', fixed=['Date'], order=['sub_ID','Dominant_eye','r_y_pos','Date'])
        
        if dlg.OK:
            subid = int(dlg.data[0])
            de = dlg.data[1]
            
            # Save the dictionary to the pickle file
            with open(pickle_path, "wb") as pickle_file:
                pickle.dump(subject_data, pickle_file)
            print('pickle saved. Experiment starts!')
        else:
            print('user cancelled')

if de=='Left':
    position=[(-400,0),(float(dlg.data[2]),0)] 
    dominant_position=position[0] #left square
    nondominant_position=position[1] #right square
else:
    position=[(float(dlg.data[2]),0), (400,0)] 
    dominant_position=position[1] #right square
    nondominant_position=position[0] #left square
        
# make a text file to save data
fileName = 'sub'+str(subject_data['sub_ID']) + '_'+str(subject_data['Date'])
dataFile = open(os.path.join(result_path, 'MRI', f'sub{subid}', f'staircase_{fileName}.csv'), 'w')  # a simple text file with 'comma-separated-values'
dataFile.write('mask_opacity, image_clarity, thisIncrement, response_key\n')

# create window and stimuli
example_image_path=example_image_path=os.path.join(image_path,'example.jpg')
win = visual.Window(size=[2*width, height], fullscr=False, screen=0,
    pos = [0,0], winType='pyglet', allowGUI=False, allowStencil=False,
    monitor=Psychopy_Monitor_Name, colorSpace='rgb',
    blendMode='avg', useFBO=True, units='deg', color=[0,0,0])
win.setMouseVisible(False)

img1 = visual.ImageStim(win=win, units="pix", pos= dominant_position, size=(100,100)) #stimulus (always) #left=non-dominant eye
img2 = visual.ImageStim(win=win, units="pix", pos= nondominant_position, size=(100,100)) #stimulus #right=dominant eye
# mondrian preloading
mon1 = visual.ImageStim(win=win, units="pix", pos= dominant_position, size=(128,128)) #CFS #right=dominant eye
mon1.setImage(os.path.join(CFS_path, 'mondrian1.jpg'))
mon2 = visual.ImageStim(win=win, units="pix", pos= dominant_position, size=(150,150))
mon2.setImage(os.path.join(CFS_path, 'mondrian2.jpg'))
mon3 = visual.ImageStim(win=win, units="pix", pos= dominant_position, size=(135,135))
mon3.setImage(os.path.join(CFS_path, 'mondrian3.jpg'))
mon4 = visual.ImageStim(win=win, units="pix", pos= dominant_position, size=(128,128))
mon4.setImage(os.path.join(CFS_path, 'mondrian4.jpg'))
mon5 = visual.ImageStim(win=win, units="pix", pos= dominant_position, size=(128,128))
mon5.setImage(os.path.join(CFS_path, 'mondrian5.jpg'))
mon6 = visual.ImageStim(win=win, units="pix", pos= dominant_position, size=(130,130))
mon6.setImage(os.path.join(CFS_path, 'mondrian6.jpg'))
mon7 = visual.ImageStim(win=win, units="pix", pos= dominant_position, size=(150,150))
mon7.setImage(os.path.join(CFS_path, 'mondrian7.jpg'))
mon8 = visual.ImageStim(win=win, units="pix", pos= dominant_position, size=(128,128))
mon8.setImage(os.path.join(CFS_path, 'mondrian8.jpg'))
mon9 = visual.ImageStim(win=win, units="pix", pos= dominant_position, size=(128,128))
mon9.setImage(os.path.join(CFS_path, 'mondrian9.jpg'))
mon10 = visual.ImageStim(win=win, units="pix", pos= dominant_position, size=(256,256))
mon10.setImage(os.path.join(CFS_path, 'mondrian10.jpg'))
mon_list=[mon1,mon2,mon3,mon4,mon5,mon6,mon7,mon8,mon9,mon10]

img1.setImage(example_image_path)
img2.setImage(example_image_path)
                              
fixation1 = visual.Circle(win, size = 5, units="pix", lineColor = 'red', fillColor = 'red', pos= dominant_position)
fixation2 = visual.Circle(win, size = 5, units="pix", lineColor = 'red', fillColor = 'red', pos= nondominant_position)

box_outline_1=visual.rect.Rect(win, width=128, height=128, units="pix", lineWidth=5, lineColor='white', fillColor=None, fillColorSpace=None, pos= dominant_position)
box_outline_2=visual.rect.Rect(win, width=128, height=128, units="pix", lineWidth=5, lineColor='white', fillColor=None, fillColorSpace=None, pos= nondominant_position)

recognition_check_1= visual.TextStim(win, text= 'Did it break? \n <y/n>', pos= dominant_position, units="pix")
recognition_check_2= visual.TextStim(win, text= 'Did it break? \n <y/n>', pos= nondominant_position, units="pix")

fading_square1=visual.rect.Rect(win, width=100, height=100, fillColor= [0,0,0], pos= dominant_position, units="pix")
fading_square2=visual.rect.Rect(win, width=100, height=100, fillColor= [0,0,0], pos= nondominant_position, units="pix")

ending_text_1= visual.TextStim(win, units="pix", pos=dominant_position)
ending_text_2= visual.TextStim(win, units="pix", pos= nondominant_position) 

# dCFS_flash
dCFS_flash_list=[[1,2,3,4],[5,6,7,8],[9,10,1,2],[3,4,5,6],[7,8,9,10]]
opacity_list=[5/6, 2/3, 1/2, 1/3, 1/6, 0]

# initial value
ceiling_check=0
mask_opacity=0
image_clarity=0
response_key=0
Resp_rec=0

# mean of the opacity for the two sessions
sq_opacity_list=[]

# create the staircase handler
    #response==n-> increase image clarity (decrease box opacity)  
    #response==y-> decrease image clarity (increase box opacity)

for initial_value in [50,70]:
    if initial_value==50:
        staircase = data.StairHandler(startVal = 0,
                                      stepType = 'lin', stepSizes=[10, 10, 5,5, 2.5, 2.5], 
                                      nUp= 1,#increase increment #2 times cannot recognized twice #sq_opacity and increment + #clarity-
                                      nDown=1,  #decrease increment #1 time to decrease the intensity of the fading_square #recognized once-> decrease
                                      # will home in on the 80% threshold
                                      nTrials=0, minVal= -50, maxVal= 50)
    elif initial_value==70:
        staircase = data.StairHandler(startVal = 0,
                                      stepType = 'lin', stepSizes=[10, 10, 5,5, 2.5, 2.5], 
                                      nUp= 1,#increase increment #2 times cannot recognized twice #sq_opacity and increment + #clarity-
                                      nDown=1,  #decrease increment #1 time to decrease the intensity of the fading_square #recognized once-> decrease
                                      # will home in on the 80% threshold
                                      nTrials=0, minVal= -70, maxVal= 30)
                              
    # display instructions and wait
    mask_opacity= initial_value
    initial_contrast= initial_value
    
    all_opacity=[]
    all_response=[]
    scenario= 'Normal' 
    #Normal-'[default] normal staircase condition'; Ceiling- 'reaching a ceilling'
    
    for thisIncrement in staircase: # will continue the staircase until it terminates!
        response_key=0
        Resp_rec=0
        
        #blank and fixation
        fixation1.draw()
        fixation2.draw()
        box_outline_1.draw()
        box_outline_2.draw()
        win.flip()
        core.wait(1.0)
        
        onset_time= clock.getTime()
        for f, flash in enumerate(dCFS_flash_list):
                    ###fade in
                    #record unconsious stimulus onset
                    if f==0:
                        image_onset_time=clock.getTime()
                        for t, m_num in enumerate(flash):
                            start_flash_time= clock.getTime()
                            mon_list[m_num-1].draw()
                            box_outline_1.draw()
                            box_outline_2.draw()
                            img2.draw()
                            fading_square2.opacity= (initial_contrast+ thisIncrement)/100
                            fading_square2.draw()
                            fixation2.draw()
                            win.flip()
                            core.wait(0.1)
                        #print(f'done fade in...{clock.getTime()}')
                    ### solid presentation
                    else:
                        #record unconscious stimulus offtime
                        for t, m_num in enumerate(flash):
                            start_flash_time= clock.getTime()
                            mon_list[m_num-1].draw()
                            fading_square2.opacity= (initial_contrast+ thisIncrement)/100
                            box_outline_1.draw()
                            box_outline_2.draw()
                            img2.draw()
                            fading_square2.draw()
                            fixation2.draw()
                            win.flip()
                            core.wait(0.1)
                        
                    #flash off
                    box_outline_1.draw()
                    box_outline_2.draw()
                    fixation1.draw()
                    fixation2.draw()
                    win.flip()
                    core.wait(0.4)
                    #print(f'flash off by orders...{clock.getTime()}')
        offset_time= clock.getTime()
        print(f'image_presentation duration is {offset_time-onset_time}')
        
        #recognition check
        event.clearEvents()
        resp=[]
        response_key='0'
        
        #Recognition 3s
        response_start= clock.getTime()
        present_moment=clock.getTime()
        while (present_moment-response_start) <=3:
            present_moment=clock.getTime()
            recognition_check_1.draw()
            recognition_check_2.draw()
            box_outline_1.draw()
            box_outline_2.draw()
            fixation1.draw()
            fixation2.draw()
            win.flip()
            resp= event.getKeys(keyList=['1','2','escape'], timeStamped= True)
            if len(resp)==0:
                continue
            else:
                if resp[0][0]=='1':
                    response_key= 'y'
                    Resp_rec=0
                    ceiling_check=0
                    break
                
                elif resp[0][0]== '2':
                    response_key= 'n'
                    Resp_rec=1
                    if initial_value==0:
                        ceiling_check+=1
                    break
            
                elif resp[0][0]=='escape':
                    dataFile.close()
                    staircase.saveAsPickle(fileName) 
                    core.quit()
                    print('quitted')
                    
                else:
                    #invalid response
                    response_key= 'not pressed any'
                    Resp_rec=1
                    continue
                    
        mask_opacity=  (initial_value+ thisIncrement)/100
        image_clarity= 1- mask_opacity 
        
        print(f'response: {response_key} ; thisIncrement: {thisIncrement}; opacity: {mask_opacity}; clarity: {image_clarity}') 
        
        all_opacity.append((initial_contrast+ thisIncrement)/100)
        all_response.append(Resp_rec)
        
        # add the data to the staircase so it can calculate the next level
        staircase.addResponse(Resp_rec)
        dataFile.write('%.2f,%.2f,%.2f,%s\n' %(mask_opacity, image_clarity, thisIncrement, response_key))
        #dataFile.write('%.2f,%s\n' %(thisIncrement, response_key))
        
        # consistantly reaching a ceiling in the second part 
        
        if ceiling_check>=6:
            if image_clarity==1.0:
                scenario='Ceiling'
                break
            #break
        else:
            scenario='Normal'
    # staircase has ended
    
    
    final_opacity=1000 #default
    # give some output to user in the command line in the output window
    if scenario=='Normal':
        print('reversals:')
        print(staircase.reversalIntensities)
        approxThreshold = np.average(staircase.reversalIntensities[-4:])
        final_opacity= initial_value +approxThreshold
        print('mean of final 4 reversals = %.2f' % (approxThreshold))
        print('opacity threshold = %.2f' % (final_opacity))
        
        # give some on-screen feedback
        feedback1 = visual.TextStim(
                win, pos=(dominant_position[0],50), units="pix",
                text='opacity = %.2f' % (final_opacity), height= 15)
        feedback2 = visual.TextStim(
                win, pos=(nondominant_position[0],50), units="pix",
                text='opacity = %.2f' % (final_opacity), height= 15)

    if scenario=='Ceiling':
        final_opacity=(initial_value+ thisIncrement)/100
        print(f'stop changing at the opacity increment of {(initial_contrast+ thisIncrement)/100} ')
        feedback1 = visual.TextStim(
                win, pos=(dominant_position[0],50), units="pix",
                text='ceilling opcacity at = %.2f' % (final_opacity), height= 15)
        feedback2 = visual.TextStim(
                win, pos=(nondominant_position[0],50), units="pix",
                text='ceilling opacity at = %.2f' % (final_opacity), height= 15)
    
    sq_opacity_list.append(final_opacity)

    if initial_value==50:
        ending_text_1.setText('Part I done! \n Press LEFT to continue')
        ending_text_2.setText('Part I done! \n Press LEFT to continue')
    elif initial_value==0:
        ending_text_1.setText('Thank you! \n press LEFT to quit!')
        ending_text_2.setText('Thank you! \n press LEFT to quit!')
        
    box_outline_1.draw()
    box_outline_2.draw()
    ending_text_1.draw()
    ending_text_2.draw()
    feedback1.draw()
    feedback2.draw()
    fixation1.draw()
    fixation2.draw()
    win.flip()
    event.waitKeys(keyList=['6'])  # wait for participant to respond
    
    if initial_value==50:
        pass
    elif initial_value==0:
        break

sq_opacity_value=np.mean(sq_opacity_list)
print(f'The 2 Sessions End! with mean of mean as {sq_opacity_value}')
dataFile.close()

with open(pickle_path, "rb") as pickle_file:
    subject_data = pickle.load(pickle_file)
    subject_data['SQ_opacity']=sq_opacity_value

    # Save the dictionary to the pickle file
    with open(pickle_path, "wb") as pickle_file:
        pickle.dump(subject_data, pickle_file)
        print('pickle saved. Experiment starts!')

win.close()
core.quit()