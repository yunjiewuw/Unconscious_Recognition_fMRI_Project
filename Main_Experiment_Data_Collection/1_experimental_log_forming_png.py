#import
from psychopy import visual, data, event, gui, core, monitors
from glob import glob
import time
import os 
import random
import pandas as pd
import numpy as np
import datetime
import pickle


#Path setting
CFS_path='CFS' 
image_path= 'images'
result_path='results'
log_path=os.path.join(result_path,'log')
MRI_path=os.path.join(result_path, 'MRI')
pickle_path= os.path.join(MRI_path, 'subject_data.pickle')

##experimental date
date=datetime.datetime.today().strftime('%Y-%m-%d')#%H-%M:-%S

# Save or create a pickle file for this subject (change name/ delete for each new subject)
if not os.path.exists(pickle_path):
    # Create a dialog to collect values
    initialDlg = gui.Dlg(title="Enter Values")
    initialDlg.addField("sub_ID:")
    initialDlg.addField("Dominant Eye:", choices=["Left", "Right"])
    if initialDlg.show():
            subid = int(initialDlg.data[0])
            de = initialDlg.data[1]
            datestr= date

            # Create a dictionary to store the values
            subject_data = {"sub_ID": subid, "Dominant_eye": de, "Date": date}

            # Save the dictionary to the pickle file
            with open(pickle_path, "wb") as pickle_file:
                pickle.dump(subject_data, pickle_file)
else:
    # The pickle file already exists, load its content
    with open(pickle_path, "rb") as pickle_file:
        subject_data = pickle.load(pickle_file)
        dlg = gui.DlgFromDict(subject_data, title='1. LOG FORMING', fixed=['Date'], order=['sub_ID','Dominant_eye','Date'])
        
        if dlg.OK:
            subid = int(dlg.data[0])
            de = dlg.data[1]
            # update the dictionary to store the values
            subject_data = {"sub_ID": subid, "Dominant_eye": de, "Date": date}

            # Save the dictionary to the pickle file
            with open(pickle_path, "wb") as pickle_file:
                pickle.dump(subject_data, pickle_file)
            print('pickle saved. Experiment starts!')
        else:
            print('user cancelled')

# Experiment Log file

## shuffle images 
complete_list=glob(os.path.join(image_path,'mooney','*.png'))
#fixed for first and last trial (incomplete image data)
incomplete_list=[os.path.join(image_path, 'mooney','020.png'),
                 os.path.join(image_path, 'mooney','040.png'),
                 os.path.join(image_path, 'mooney','042.png'),
                 os.path.join(image_path, 'mooney','068.png')] 
                

for img in incomplete_list:
    complete_list.remove(img)
random.shuffle(complete_list)
image_list= incomplete_list[:2]+ complete_list + incomplete_list[2:]

##get filenames
experiment_image_order=[]
for img in image_list:
    experiment_image_order.append(img.split('\\')[-1]) 

## Trial setting
runs_set=[] 
img_set=[]
disambiguation_num= 2 #meaning 2 images are disambiguated for each trial
for i in range(0, len(experiment_image_order), disambiguation_num): #no disambiguation/post-disambiguation for the last run
    img_set=[experiment_image_order[i], experiment_image_order[i+1]] #12 images in total
    runs_set.append(img_set)

###image queue preparation
trial=0
image_name=[]
image_type=[]
condition_list=[]
repetition=[]
flip_record=[]

#### trial setting
for r in range(int((len(runs_set)-1))): #all runs -1
    run_number=1+r #0-13
    disambiguation=runs_set[r] #disambiguation== grayscale
    predisambiguation=runs_set[r+1]
    trial= disambiguation+predisambiguation 
            
    # 3 times repetition 
    for i in range(3): 
         
         #grayscale
         #pre+post- mooney
        for c in range(2):
            random.shuffle(disambiguation)
            for g in range(2):
                flip_record.append(os.path.join(image_path,'grey', disambiguation[g]))
                image_name.append(disambiguation[g])
                image_type.append('grayscale')
                if c==0: 
                    condition_list.append('unconscious')  #unconscious
                elif c==1:
                    condition_list.append('conscious')
                repetition.append(i+1)
        
        for c in range(2):
            random.shuffle(trial)
            for m in range(4):
                flip_record.append(os.path.join(image_path,'mooney',trial[m]))
                image_name.append(trial[m])
                image_type.append('mooney')
                if c==0:
                    condition_list.append('unconscious')  #unconscious
                elif c==1:
                    condition_list.append('conscious')
                repetition.append(i+1)
                

####setting for run
run_number=int(len(repetition)/36) #7runs 
runs=[]
for i in range(run_number):
    for j in range(36):
        runs.append(i+1)                                                                                          

#### check if this subject has already had a log file
sub_log_path = os.path.join(log_path, f'sub{subid}_{date}_log.csv' )
isExist = os.path.exists(sub_log_path)
if isExist:
    print(f'log file already exists, you should either remove it before proceed')
    core.quit()


#### saving experimental log to record path
log_file=pd.DataFrame({'sub_ID': subid, 'Dominant_eye': de, 'Run': runs, 'image_name' : image_name, 'path':flip_record, 'image_type' : image_type,
                            'condition' : condition_list, 'repetition': repetition}, 
                            columns=['sub_ID', 'Dominant_eye','Run','image_name','path','image_type','condition', 'repetition'])
log_file.to_csv(os.path.join(sub_log_path))


####create batch folder for subject
path = os.path.join(result_path, 'MRI', f'sub{subid}' )
isExist = os.path.exists(path)
if not isExist:
    os.makedirs(path)
    print(f"Folder {path} is created!")    
else:
    print(f"[warning]***Folder {path} already EXISTS!***")
    
log_file.to_csv(os.path.join(result_path, 'MRI', f'sub{subid}', f'sub{subid}_{date}_experimental_log.csv' ))
print("experimental_log.csv created!")