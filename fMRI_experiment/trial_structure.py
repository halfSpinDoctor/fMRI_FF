
#import dependencies
#-----------------------------------------------------------------------------
import numpy as np
from psychopy import core, visual, event, logging
from trial_classes import trial, init
import random
import trial_parameters as globvar
import pylink
logging.console.setLevel(logging.CRITICAL)
#-----------------------------------------------------------------------------

#initialize the eyetracker
#-----------------------------------------------------------------------------
print 'initialize eyetracker'

#connect to tracker, if needed
if globvar.tracker_connected == True:
    eye_tracker = pylink.EyeLink(globvar.tracker_ip)
elif globvar.tracker_connected == False:
    eye_tracker = pylink.EyeLink(None)

#open output file
pylink.getEYELINK().openDataFile(globvar.edf_filename)


#send screen size to tracker
pylink.getEYELINK().sendCommand("screen_pixel_coords =  0 0 %d %d" %(globvar.full_window_size[0], globvar.full_window_size[1]))
pylink.getEYELINK().sendMessage("screen_pixel_coords =  0 0 %d %d" %(globvar.full_window_size[0], globvar.full_window_size[1]))

#get tracker version and tracker software version
tracker_software_ver = 0
eyelink_ver = pylink.getEYELINK().getTrackerVersion()
if eyelink_ver == 3:
	tvstr = pylink.getEYELINK().getTrackerVersionString()
	vindex = tvstr.find("EYELINK CL")
	tracker_software_ver = int(float(tvstr[(vindex + len("EYELINK CL")):].strip()))
print 'tracker version', eyelink_ver
print 'tracker software v', tracker_software_ver

# set tracker output file contents 
pylink.getEYELINK().sendCommand("file_event_filter = LEFT,RIGHT,FIXATION,SACCADE,BLINK,MESSAGE,BUTTON")
if tracker_software_ver>=4:
	pylink.getEYELINK().sendCommand("file_sample_data  = LEFT,RIGHT,GAZE,AREA,GAZERES,STATUS,HTARGET")
else:
	pylink.getEYELINK().sendCommand("file_sample_data  = LEFT,RIGHT,GAZE,AREA,GAZERES,STATUS")
#do tracker setup
if eyelink_ver != 0:
    eye_tracker.doTrackerSetup()
eye_tracker.setOfflineMode()

#-----------------------------------------------------------------------------


#initialize the class for generation of trial parameters
#-----------------------------------------------------------------------------
print 'trial setup'
init_parameters = init()

#change participent specific parameters
init_parameters.participant_parameter_dialog()
    
#load balancing from file
init_parameters.load_trial_parameters()

#generate trial parameters for the upcomming trials
blocks, EV_gap, timing, inversions, EV_values, difficulties, stim_parameters, rewards = init_parameters.randomize_participant_specific_variables()
#-----------------------------------------------------------------------------

#preparation of trials: prepare output to file
#-----------------------------------------------------------------------------
win = visual.Window(size=globvar.full_window_size, fullscr=globvar.full_screen)
#write a short readme to the output file
output_user_interaction = open('choice_study_user_input.txt','w')
print>>output_user_interaction, '#output format is the following'
print>>output_user_interaction, '#trial_type, user_active?, user_input_key, accepted difficulty, accepted reward, accepted dif*reward, rejected difficulty, rejected reward, rejected dif*reward, inversions'
print>>output_user_interaction, '#difficulty refers to the exptected participant performance as set in trial_parameters'
print>>output_user_interaction, '#the four columns of inversions refer to the inversion of the default arrangement of the displayed elements. 1 means default arrangement, -1 means inverse of default arrangement.'
print>>output_user_interaction, '# The default setting is 1) easy fist, hard second, 2) high left, low right, 3) option markers: marker_1 left and marker_2 right 4) response markers: marker_1 left and marker_2 right'

output_trial_timing = open('choice_study_trial_timing.txt','w')
print>>output_trial_timing, '#this file contains the data for timing of each trial'
print>>output_trial_timing, '#output is given relative timing to trial start. output format is the following:'
print>>output_trial_timing, '#trial_type, time_tasks, time_delay_1, time_options, time_delay_2, time_decision, time_baseline time_trial_end, user_reaction_time'

globvar.output_run_timing = open('participant_'+`globvar.participant_id`+'_run_'+`globvar.run_number`+'_timestamped_output.txt','w')
#-----------------------------------------------------------------------------

#preparation of trials: short introduction and explanation slide
#-----------------------------------------------------------------------------
message1 = visual.TextStim(win=win, text='Wellcome to the experiment! \n \n \n To start the experiment press space. \n To quit the experiment press escape.', height=globvar.text_height*globvar.f_y)
message1.draw()
event.clearEvents()
win.flip()
#-----------------------------------------------------------------------------

#wait for human start signal
#-----------------------------------------------------------------------------
start_human = False
print 'waiting for human start signal'
while start_human == False:
    for key in event.getKeys():
        if key == globvar.human_start_signal:
            start_human = True
        if key == globvar.exit_key:
            win.close()
            core.quit()
#-----------------------------------------------------------------------------

#wait for machine start signal
#-----------------------------------------------------------------------------
event.clearEvents()
start_machine = False
print 'waiting for machine start signal'
while start_machine == False:
    for key in event.getKeys():
        if key == globvar.fMRI_start_signal:
            start_machine = True
#-----------------------------------------------------------------------------

#initialize run timer
globvar.experiment_timer.append(core.MonotonicClock())
globvar.sequential_timer.append(0)

#iterate over requested number of blocks and set parameters
#-----------------------------------------------------------------------------
for block, kind in enumerate(blocks):
    i1 = block*globvar.blocks[1]
    i2 = (block+1)*globvar.blocks[1]

    print>>globvar.output_run_timing, globvar.sequential_timer[-1], 'started_block', block, 'of ', globvar.blocks[1], kind, 'trials'
    #write a short note to the output file, if a new block starts
    print>>output_user_interaction, 'start ', kind, ' block ' + `block`
    print>>output_trial_timing, 'start ', kind, ' block ' + `block`

#-----------------------------------------------------------------------------

#run the actual trials and record user input
#-----------------------------------------------------------------------------
    for i in range(i1,i2):
        if eyelink_ver != 0:
            if eye_tracker.isConnected()==False:
                print 'SCANNER CONNECTION LOST'
            pylink.getEYELINK().startRecording(1, 1, 0, 0)
        #set trial parameters
        current_trial = trial(kind,win,i) 
        #run trial
        print>>globvar.output_run_timing, globvar.sequential_timer[-1],\
                'start_'+kind+'_trial', i, 'EV_gap_is', globvar.run_parameters['EV_gap'][i]
        current_trial.run_trial()
        print>>globvar.output_run_timing, globvar.sequential_timer[-1],\
                'end_'+kind+'_trial', i
        #data from trial.getData() is kind, user_active[y,n], input_key, difficulty_chosen, reward_chosen, dif*rew, 
        #                                                                difficulty_rejected, reward_rejected, dif*rew
        #save data from each trial, timing of slides, user input and inversions of stimuli
        print>>output_user_interaction, str(current_trial.getData()).strip('()'), str(inversions[i,:]).strip('[]')
        print>>output_trial_timing, str(current_trial.getTiming()).strip('()')
        del current_trial
        if eyelink_ver !=0:
            pylink.getEYELINK().stopRecording()
win.close()
output_user_interaction.close()
output_trial_timing.close()
#-----------------------------------------------------------------------------


#-----------------------------------------------------------------------------
#present actual tasks to participant
#-----------------------------------------------------------------------------


#-----------------------------------------------------------------------------
#evaluate user input and save relevant data
#-----------------------------------------------------------------------------

if pylink.getEYELINK() != None:
   # File transfer and cleanup!
    pylink.getEYELINK().setOfflineMode();                          
    pylink.msecDelay(500);                 

    #Close the file and transfer it to Display PC
    pylink.getEYELINK().closeDataFile()
    pylink.getEYELINK().receiveDataFile(globvar.edf_filename, globvar.edf_filename)
    pylink.getEYELINK().close();
