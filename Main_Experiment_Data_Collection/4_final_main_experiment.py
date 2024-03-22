#import
from psychopy import visual, event, gui, data, core
from glob import glob
import time
import os 
import random
import pandas as pd
import numpy as np
import datetime
import pickle
import zipfile 
import shutil
import json
from screeninfo import get_monitors

# Experimental parameter default value setting
#experimental date
date=datetime.datetime.today().strftime('%Y-%m-%d') #-%H:-%M:-%S
current_time=datetime.datetime.today().strftime('%H%M') #time

subid=0
de='initial'
sq_opacity=0.0

#screen setting
Psychopy_Monitor_Name = "Goggle" # for fMRI
Monitors = get_monitors()
width = Monitors [0].width
height = Monitors[0].height

#Path setting
CFS_path='CFS' 
image_path= 'images'
result_path='results'
log_path=os.path.join(result_path,'log')
MRI_path=os.path.join(result_path, 'MRI')
pickle_path=os.path.join(result_path, 'MRI', 'subject_data.pickle')


#function library
def zip_folder(source_folder, destination_path):
    # Create a temporary duplicate of the source folder
    temp_folder = source_folder + "_temp"
    shutil.copytree(source_folder, temp_folder)

    # Zip the temporary folder into the destination path
    with zipfile.ZipFile(destination_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(temp_folder):
            for file in files:
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, temp_folder)
                zipf.write(file_path, relative_path)
    # Remove the temporary duplicate folder
    shutil.rmtree(temp_folder)

def backup_by_trial(trial_data):
    with open(os.path.join(result_path, 'MRI', f'sub{subid}', f'sub{subid}_{date}_response_backup.json'), 'w') as backup_file:
        json.dump(trial_data, backup_file)
        print('******backed-up*******')
    return
    

def save_backup_to_csv(trial_data):
    current_time=datetime.datetime.today().strftime('%H%M') #time
    print('saving...')
    response_result= pd.DataFrame(trial_data)
    response_result.reindex(columns=[
        'sub_ID', 'Dominant_eye','Run','image_name','path','image_type','condition',
        'repetition','onset_frame','offset_frame','onset_time','offset_time','onset_time_clock',
        'offset_time_clock','presentation_duration_clock','recognition','response_time','response_time_clock', 
        'break_response','break_time','break_time_clock'])
    response_result.to_csv(os.path.join(result_path, 'MRI', f'sub{subid}', f'sub{subid}_{date}_response_{current_time}.csv'), index=False) 
    print('Experimental response file saved')
    
    # the entire experiment ends 
    if run_number_next==8:
        print('--------------------')
        #move the pickle file to the subject folder
        pickle_destination_path = os.path.join(MRI_path, f'sub{subid}',f'sub{subid}_subject_data.pickle')
        shutil.move(pickle_path, pickle_destination_path)
        print('copying...')
        #duplicate the subject folder and save as zip 
        source_folder = os.path.join(result_path, 'MRI', f'sub{subid}')
        destination_path = os.path.join(result_path, 'MRI', f'sub{subid}_result.zip')
        zip_folder(source_folder, destination_path)
        print(f'sub{subid} file saved and zipped!')
    return

# Save or create a pickle file for this subject (change name/ delete for each new subject)
if not os.path.exists(pickle_path):
    print("please get the parameters for this subject first")    
else:
    # The pickle file already exists, load its content
    with open(pickle_path, "rb") as pickle_file:
        subject_data = pickle.load(pickle_file)
        subject_data['Run']= 1
        #subject_data['SQ_opacity']=0
        dlg = gui.DlgFromDict(subject_data, title='4. MAIN RECOGNITION EXPERIMENT', 
        fixed=['Date'], 
        order=['sub_ID','Dominant_eye','r_y_pos', 'SQ_opacity', 'Date', 'Run'])
        
        if dlg.OK:
            #parameters
            subid = int(dlg.data[0])
            de = str(dlg.data[1])
            sq_opacity=float(dlg.data[3])
            start_run_number= int(dlg.data[5]) #run1-7
            print(f'This is RUN {start_run_number}, {type(start_run_number)}')
            
            # Save the dictionary to the pickle file
            with open(pickle_path, "wb") as pickle_file:
                pickle.dump(subject_data, pickle_file)
            print('pickle saved. Experiment starts!')
        else:
            print('user cancelled')

### location setting
position=[]
if dlg.data[1]=='Left':
    print('de is left')
    de='left'
    position=[(-400,0),(float(dlg.data[2]),0)] 
    dominant_position=position[0] #left square
    nondominant_position=position[1] #right square
else:
    dlg.data[1]='right'
    print(f'not left, {dlg.data[1]}')
    position=[(float(dlg.data[2]),0), (400,0)] 
    dominant_position=position[1] #right square
    nondominant_position=position[0] #left square
    
#set up conditions according to the log file
log= pd.read_csv(os.path.join(result_path, 'MRI', f'sub{subid}', f'sub{subid}_{date}_experimental_log.csv'), index_col=0)
flip_record=list(log.path)
name_list=list(log.image_name)
condition_list=list(log.condition)
run_list=list(log.Run)
image_type_list=list(log.image_type)
repetition_list=list(log.repetition)

# dCFS_flash
dCFS_flash_list=[[1,2,3,4],[5,6,7,8],[9,10,1,2],[3,4,5,6],[7,8,9,10]]

#Open a window for experiment
#win=visual.Window(size=[1440, 900],units="pix",fullscr=False, color=[0, 0, 0])
#win=visual.Window(size=[800, 600],units="pix",fullscr=True, color=[0, 0, 0])
win = visual.Window(size=[2*width, height], fullscr=False, screen=0,
    pos = [0,0], winType='pyglet', allowGUI=False, allowStencil=False,
    monitor=Psychopy_Monitor_Name, colorSpace='rgb',
    blendMode='avg', useFBO=True, units='deg', color=[0,0,0])
win.setMouseVisible(False)
    
###stimulus setting
#image preloading
img1 = visual.ImageStim(win=win, units="pix", pos= dominant_position, size=(100,100)) #stimulus (always) #left=non-dominant eye
img2 = visual.ImageStim(win=win, units="pix", pos= nondominant_position, size=(100,100)) #stimulus #right=dominant eye
image_paths = flip_record
stim1 = []
stim2 = []
for image_path in image_paths:
    image_stim1 = visual.ImageStim(win, image=image_path, units="pix", pos= dominant_position, size=(100,100))
    image_stim2=  visual.ImageStim(win, image=image_path, units="pix", pos= nondominant_position, size=(100,100))
    stim1.append(image_stim1)
    stim2.append(image_stim2)

# mondrian preloading
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

fixation1 = visual.Circle(win, size = 5, lineColor = 'red', fillColor = 'red', pos= dominant_position, units="pix")
fixation2 = visual.Circle(win, size = 5, lineColor = 'red', fillColor = 'red', pos= nondominant_position, units="pix")

box_outline_1= visual.rect.Rect(win, width=128, height=128, units="pix", lineWidth=5, lineColor='white', fillColor=None, fillColorSpace=None, pos= dominant_position)
box_outline_2= visual.rect.Rect(win, width=128, height=128, units="pix", lineWidth=5, lineColor='white', fillColor=None, fillColorSpace=None, pos= nondominant_position)

start_1= visual.TextStim(win, text= 'waiting for scanner', pos= dominant_position, units='pix', height= 15)
start_2= visual.TextStim(win, text= 'waiting for scanner', pos= nondominant_position, units='pix', height= 15)

recognition_check_1= visual.TextStim(win, text= 'Can you recognize? \n <y/n>', pos= dominant_position, units='pix', height= 15)
recognition_check_2= visual.TextStim(win, text= 'Can you recognize? \n <y/n>', pos= nondominant_position, units='pix', height= 15)

resting_text_1= visual.TextStim(win, text= 'Please rest for a bit !', pos= dominant_position, units='pix', height= 15)
resting_text_2= visual.TextStim(win, text= 'Please rest for a bit !', pos= nondominant_position, units='pix', height= 15)

ending_text_1= visual.TextStim(win, text= 'Experiment ends! \n Thank you!', pos= dominant_position, units='pix', height= 15)
ending_text_2= visual.TextStim(win, text= 'Experiment ends! \n Thank you!', pos= nondominant_position, units='pix', height= 15)

fading_square1= visual.rect.Rect(win, width=100, height=100, fillColor= [0,0,0], pos= dominant_position, units='pix')
fading_square2= visual.rect.Rect(win, width=100, height=100, fillColor= [0,0,0], pos= nondominant_position, units='pix')

text1= visual.TextStim(win, pos=dominant_position, units='pix', height= 15)
text2= visual.TextStim(win, pos=nondominant_position, units='pix', height= 15)

##record for one trial:
trial_data = []

## set timer 
time_frame=0
clock=core.Clock()
trial_clock=core.Clock()

##value by default
onset_time=0
offset_time=0
response_time=0
response_time_clock=0

#duration setting
fixation_duration = 2.0  # seconds
image_duration = 4.0  # seconds
text_duration = 3.0  # seconds
inter_trial_blank_duration = 1.0  # seconds
flash_duration = 0.1  # seconds (for 10 Hz)
cfs_duration = 0.4  # seconds
blank_duration = 0.4  # seconds
num_flashes = int(image_duration / flash_duration) #4/0.4
trial_duration=10.0

##waiting for trigger preparation
start_1.draw()
start_2.draw()
fixation1.draw()
fixation2.draw()
box_outline_1.draw()
box_outline_2.draw()
win.flip()
event.waitKeys(keyList=['5'])

print('experiment is about to start')


# default
break_response='0'
response_key='0'
reaction_time='time_out'
num_trigger = 0
trigger_list=[]
break_response='0'
break_times_clock=0
timestamp='0'
start_index = (start_run_number - 1) * 36

# Iterate over conditions
 
for i in range(start_index, len(condition_list)):
    event.clearEvents()
    trigger_list=[]
    num_trigger = 0
    break_response='0'
    break_times_clock=0
    timestamp='0'
    resp=[]
    response_key='0'
    reaction_time='time_out'
    
    condition=condition = condition_list[i]
    trial_start= trial_clock.getTime()
    run_number = run_list[i]
    try: 
        run_number_next = run_list[i+1]
    except IndexError:
        run_number_next= 8
        
    image_name=name_list[i]
    path=flip_record[i]
    image_type=image_type_list[i]
    repetition=repetition_list[i]
    image_number= i
    print(f'----------this is run {run_number}, trial {i}----------')
    trial_start = trial_clock.getTime()
    
    ## In order to sync with Scanner trigger, counting trigger in odd and even number trial
    # odd number trial, where recieving trigger during recognition
    if i % 2 == 0:
        print(f' trial {i+1} is odd number trial')
        while True:
            triggers = event.getKeys(keyList=['5','escape'])
            
            # fixation dot presentation- 2s 
            #fixation_start= clock.getTime()
            fixation1.draw()
            fixation2.draw()
            box_outline_1.draw()
            box_outline_2.draw()
            win.flip()
            core.wait(fixation_duration)
            #fixation_end= clock.getTime()
            #print(f'fixation start is {fixation_start}; fixation_end time is {fixation_end}')
            #print(f'fixation length is {fixation_end-fixation_start}')
                
            ###Image presentation-4 (flash, fade-in)
#            event.clearEvents()
            onset_time_clock=clock.getTime()
            #print(f'image onset time is {onset_time_clock}')
            
            #### conscious condition
            if condition=='conscious': 
            ####conscious condition
                for f, flash in enumerate(dCFS_flash_list):
                        #fade in
                        #record consious stimulus onset
                        if f==0:
                            for t in range(len(flash)): #4
                                flash_start_time=clock.getTime()
                                while clock.getTime()-flash_start_time<=0.1:
                                    box_outline_1.draw()
                                    box_outline_2.draw()
                                    stim1[image_number].draw()
                                    stim2[image_number].draw()
                                    fading_square1.opacity= (sq_opacity+(sq_opacity*((3-t)/4)))/100
                                    fading_square2.opacity= (sq_opacity+(sq_opacity*((3-t)/4)))/100
                                        #t=0,1,2,3 #3-t: 3,2,1,0
                                        #opacity sequence=baseline+decreasing quarter
                                    fading_square1.draw()
                                    fading_square2.draw()
                                    fixation1.draw()
                                    fixation2.draw()
                                    win.flip()
                                    time_frame=time_frame+1
                                    core.wait(flash_duration)
                                
                        ### solid presentation
                        else:
                            for t in range(len(flash)):
                                flash_start_time=clock.getTime()
                                while clock.getTime()-flash_start_time<=0.1:
                                    box_outline_1.draw()
                                    box_outline_2.draw()
                                    stim1[image_number].draw()
                                    stim2[image_number].draw()
                                    fading_square1.opacity=sq_opacity/100
                                    fading_square2.opacity=sq_opacity/100
                                    fading_square1.draw()
                                    fading_square2.draw()
                                    fixation1.draw()
                                    fixation2.draw()
                                    win.flip()
                                    time_frame=time_frame+1
                                    core.wait(flash_duration)
                            
                        #flash off
                        box_outline_1.draw()
                        box_outline_2.draw()
                        fixation1.draw()
                        fixation2.draw()
                        win.flip()
                        time_frame=time_frame+1
                        core.wait(blank_duration)
                        
            
            #### unconscious condition
            else: #condition==0: unconscious 
                ##presenting both mondrian and image stimulus
                #flash on
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
                            stim2[image_number].draw()
                            fading_square2.opacity=(sq_opacity+(sq_opacity*((3-t)/4)))/100
                            fading_square2.draw()
                            fixation2.draw()
                            win.flip()
                            time_frame=time_frame+1
                            core.wait(0.1)
                        #print(f'done fade in...{clock.getTime()}')
                    ### solid presentation
                    else:
                        #record unconscious stimulus offtime
                        for t, m_num in enumerate(flash):
                            start_flash_time= clock.getTime()
                            mon_list[m_num-1].draw()
                            fading_square2.opacity=sq_opacity/100
                            box_outline_1.draw()
                            box_outline_2.draw()
                            stim2[image_number].draw()
                            fading_square2.draw()
                            fixation2.draw()
                            win.flip()
                            time_frame=time_frame+1
                            core.wait(0.1)
                        
                    #flash off
                    box_outline_1.draw()
                    box_outline_2.draw()
                    fixation1.draw()
                    fixation2.draw()
                    win.flip()
                    time_frame=time_frame+1
                    core.wait(0.4)
                    #print(f'flash off by orders...{clock.getTime()}')
            offset_time_clock=clock.getTime()
    #            print(f'image_presentation duration is {offset_time_clock-onset_time_clock}')
                
            try:
                keys= event.getKeys(keyList=['6'], timeStamped=True)
                if keys: 
                    # Get the first key and its timestamp
                    key, timestamp = keys[0]
                    break_response='break'
                    break_times= timestamp
                    break_times_clock=clock.getTime()
                    print("Break, Key pressed:", key, "Timestamp:", timestamp)
                else:
                    print("Not breaking.")
                    break_response = '0'
                    break_times = 0
                    break_times_clock=0

            except ValueError:
                print('Error: No keys found.')
                break_response = '0'
                break_times = 0
                break_times_clock=0
                print('Error: No keys found.')

            ###recognition check
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
                resp= event.getKeys(keyList=['1','2'], timeStamped= True)
                if len(resp)==0:
                    continue
                else:
                    if resp[0][0]=='1':
                        response_key= 'y'
                        response_time=resp[0][1]
                        response_time_clock=clock.getTime()
                        response_time=response_time_clock-response_start
                    
                    elif resp[0][0]== '2':
                        response_key= 'n'
                        response_time=resp[0][1]
                        response_time_clock=clock.getTime()
                        response_time=response_time_clock-response_start
                    else:
                        #invalid response
                        response_time_clock=0
                        response_time=0
                        
                response_end= clock.getTime() 
                
                print('response: ', response_key, 'reaction_time:', response_time)
                print(f'response period is : {response_end-response_start}')
                
            # Create a dictionary to store trial data
            trial_dict = {
            'sub_ID':subid,
            'Dominant_eye':de, 
            'Run': run_number,
            'image_name':image_name,
            'path': path,
            'image_type': image_type,
            'condition': condition,
            'repetition': repetition,
            'onset_time_clock': onset_time_clock,
            'offset_time_clock': offset_time_clock,
            'presentation_duration_clock': offset_time_clock-onset_time_clock,
            'recognition': response_key,
            'response_time': response_time,
            'break_response': break_response,
            'break_time_clock': break_times_clock
            }
            
            trial_data.append(trial_dict)
            backup_by_trial(trial_data)
                
            triggers = event.getKeys(keyList=['5','escape'])    
            
            if 'escape' in triggers:
                save_backup_to_csv(trial_data)
                print('quitted and file saved')
                win.close()
                core.quit()
                    
            elif '5' in triggers:
                num_trigger += len(triggers)
                print(f'before blank receiving {triggers} as triggers..., num_trigger is {num_trigger}')
                #print(f'trigger is {trigger}, so trigger_list is {trigger_list}')
                    
            else:
                print(f' before blank, trigger is {triggers}')            
                
            # blank of max 1s 
            blank_start = clock.getTime()
            while num_trigger < 3:
                box_outline_1.draw()
                box_outline_2.draw()
                fixation1.draw()
                fixation2.draw()
                win.flip()
                blank_triggers = event.getKeys(keyList = ['5','escape'])
                if '5' in blank_triggers:
                    num_trigger += len(blank_triggers)
                    print(f'receiving {blank_triggers} as blank_triggers..., num_trigger is {num_trigger}')
                elif 'escape' in blank_triggers:
                    save_backup_to_csv(trial_data)
                    print('quitted and file saved')
                    win.close()
                    core.quit()
                #print(f'trigger is {trigger}, so trigger_list is {trigger_list}')
            
            print('while loop ends here')
            break
    
    #even number trial, where recieving 3 triggers
    else:
        print(f' trial {i+1} is even number trial')
        while True:
            triggers = event.getKeys(keyList=['5','escape'])
        
            # fixation dot presentation- 2s 
            #fixation_start= clock.getTime()
            fixation1.draw()
            fixation2.draw()
            box_outline_1.draw()
            box_outline_2.draw()
            win.flip()
            core.wait(fixation_duration)
            #fixation_end= clock.getTime()
            #print(f'fixation start is {fixation_start}; fixation_end time is {fixation_end}')
            #print(f'fixation length is {fixation_end-fixation_start}')
                
            ###Image presentation-4 (flash, fade-in)
#            event.clearEvents()
            onset_time_clock=clock.getTime()
            #print(f'image onset time is {onset_time_clock}')
            
            #### conscious condition
            if condition=='conscious': 
            ####conscious condition
                for f, flash in enumerate(dCFS_flash_list):
                        #fade in
                        #record consious stimulus onset
                        if f==0:
                            for t in range(len(flash)): #4
                                flash_start_time=clock.getTime()
                                while clock.getTime()-flash_start_time<=0.1:
                                    box_outline_1.draw()
                                    box_outline_2.draw()
                                    stim1[image_number].draw()
                                    stim2[image_number].draw()
                                    fading_square1.opacity= (sq_opacity+(sq_opacity*((3-t)/4)))/100
                                    fading_square2.opacity= (sq_opacity+(sq_opacity*((3-t)/4)))/100
                                        #t=0,1,2,3 #3-t: 3,2,1,0
                                        #opacity sequence=baseline+decreasing quarter
                                    fading_square1.draw()
                                    fading_square2.draw()
                                    fixation1.draw()
                                    fixation2.draw()
                                    win.flip()
                                    time_frame=time_frame+1
                                    core.wait(flash_duration)
                                
                        ### solid presentation
                        else:
                            for t in range(len(flash)):
                                flash_start_time=clock.getTime()
                                while clock.getTime()-flash_start_time<=0.1:
                                    box_outline_1.draw()
                                    box_outline_2.draw()
                                    stim1[image_number].draw()
                                    stim2[image_number].draw()
                                    fading_square1.opacity=sq_opacity/100
                                    fading_square2.opacity=sq_opacity/100
                                    fading_square1.draw()
                                    fading_square2.draw()
                                    fixation1.draw()
                                    fixation2.draw()
                                    win.flip()
                                    time_frame=time_frame+1
                                    core.wait(flash_duration)
                            
                        #flash off
                        box_outline_1.draw()
                        box_outline_2.draw()
                        fixation1.draw()
                        fixation2.draw()
                        win.flip()
                        time_frame=time_frame+1
                        core.wait(blank_duration)
                        
            
            #### unconscious condition
            else: #condition==0: unconscious 
                ##presenting both mondrian and image stimulus
                #flash on
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
                            stim2[image_number].draw()
                            fading_square2.opacity=(sq_opacity+(sq_opacity*((3-t)/4)))/100
                            fading_square2.draw()
                            fixation2.draw()
                            win.flip()
                            time_frame=time_frame+1
                            core.wait(0.1)
                        #print(f'done fade in...{clock.getTime()}')
                    ### solid presentation
                    else:
                        #record unconscious stimulus offtime
                        for t, m_num in enumerate(flash):
                            start_flash_time= clock.getTime()
                            mon_list[m_num-1].draw()
                            fading_square2.opacity=sq_opacity/100
                            box_outline_1.draw()
                            box_outline_2.draw()
                            stim2[image_number].draw()
                            fading_square2.draw()
                            fixation2.draw()
                            win.flip()
                            time_frame=time_frame+1
                            core.wait(0.1)
                        
                    #flash off
                    box_outline_1.draw()
                    box_outline_2.draw()
                    fixation1.draw()
                    fixation2.draw()
                    win.flip()
                    time_frame=time_frame+1
                    core.wait(0.4)
                    #print(f'flash off by orders...{clock.getTime()}')
            offset_time_clock=clock.getTime()
    #            print(f'image_presentation duration is {offset_time_clock-onset_time_clock}')
                
            try:
                keys= event.getKeys(keyList=['6'], timeStamped=True)
                if keys: 
                    # Get the first key and its timestamp
                    key, timestamp = keys[0]
                    break_response='break'
                    break_times= timestamp
                    break_times_clock=clock.getTime()
                    print("Break, Key pressed:", key, "Timestamp:", timestamp)
                else:
                    print("Not breaking.")
                    break_response = '0'
                    break_times = 0
                    break_times_clock=0

            except ValueError:
                print('Error: No keys found.')
                break_response = '0'
                break_times = 0
                break_times_clock=0
                print('Error: No keys found.')

            ###recognition check
#            event.clearEvents()
            second_trigger_arrival = 0 #default if no trigger is sent 
            
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
                resp= event.getKeys(keyList=['1','2','5','escape'], timeStamped= True)
                #print(resp)
                if len(resp)==0:
                    continue
                else:
                    if resp[0][0]=='1':
                        response_key= 'y'
                        response_time=resp[0][1]
                        response_time_clock=clock.getTime()
                        response_time=response_time_clock-response_start
                    
                    elif resp[0][0]== '2':
                        response_key= 'n'
                        response_time=resp[0][1]
                        response_time_clock=clock.getTime()
                        response_time=response_time_clock-response_start
                    
                    #trigger record
                    elif resp[0][0]== '5':
                        second_trigger_arrival= clock.getTime()
                        print(f'recieve second trigger at {second_trigger_arrival}')
                        event.clearEvents()
                    
                    elif resp[0][0] == 'escape':
                        core.quit()
                    else:
                        #invalid response
                        response_time_clock=0
                        response_time=0
            
            # response end
            response_end= clock.getTime() 
                
            print('response: ', response_key, 'reaction_time:', response_time)
            print(f'response peiod is : {response_end-response_start}')
                
            # Create a dictionary to store trial data
            trial_dict = {
            'sub_ID':subid,
            'Dominant_eye':de,
            'Run': run_number,
            'image_name':image_name,
            'path': path,
            'image_type': image_type,
            'condition': condition,
            'repetition': repetition,
            'onset_time_clock': onset_time_clock,
            'offset_time_clock': offset_time_clock,
            'presentation_duration_clock': offset_time_clock-onset_time_clock,
            'recognition': response_key,
            'response_time': response_time,
            'break_response': break_response,
            'break_time_clock': break_times_clock
            }
            trial_data.append(trial_dict)
            backup_by_trial(trial_data)
                
            # blank of max 1s 
            blank_start = clock.getTime()
            if second_trigger_arrival == 0:
                blank_duration_time = 0
                #if not receiving any trigger during recognition text stage
                while blank_duration_time < 0.8: 
                    blank_duration_time = clock.getTime() - blank_start
            else: 
                blank_duration_time = 0
                while blank_duration_time < 2:
                    blank_duration_time = clock.getTime() - second_trigger_arrival
                    box_outline_1.draw()
                    box_outline_2.draw()
                    fixation1.draw()
                    fixation2.draw()
                    win.flip()
            blank_end = clock.getTime()
            print(f'Blank length is : {blank_end-blank_start}')
            
            # end of a single trial
            break     
    
    
    trial_end= trial_clock.getTime() 
    print(f'***Trial length is : {trial_end- trial_start}***')
        
    # Within the same Run
    if run_number == run_number_next:
        print('proceed to the next trial')
    
    
    else:
        # The experiment ends
        if run_number_next == 8:
            print(f'Experiment ends')
            box_outline_1.draw()
            box_outline_2.draw()

            ending_text_1.draw() 
            ending_text_2.draw() 
            win.flip()
            event.waitKeys(keyList=['space'])

            save_backup_to_csv(trial_data)
            print('closing prog...')
            win.close()
            core.quit()
        
        # The Run Ends
        else: 
            print('-------this run STOP---------')
            # run one stop, the scan stop; 
            box_outline_1.draw()
            box_outline_2.draw()
            resting_text_1.draw() 
            resting_text_2.draw() 
            win.flip()
            
            #wait for trigger and reset time_frame
            response = event.waitKeys(keyList=['space'])
            if response[0]=='space':
                #after space is pressed, wait for trigger
                waitkey=event.waitKeys(keyList=['5'])
                if waitkey[0] == '5':
                    #reset time frame
                    time_frame=0
                    event.clearEvents()
                    clock.reset()
                    trial_clock.reset()
                    pass
