#----------------------------------------------------------------------------
#this class can be used to structure one trial.
#input is:
#kind   :   the kind of stimulus presented
#win    :   the window the stimulus will be presented in
#timing :   time each slide shall be presented
#spacing:   spacing array containing the positions of the different objects in the trail
#           [stim1, stim2, marker1, marker2, fixation_cross]
#difficulties : difficulties for the different stimuli

#----------------------------------------------------------------------------
#trial is activated by calling the self.run_trail() method.

from psychopy import core, visual, sound, event, gui
import numpy as np
import matplotlib.pyplot as mp
import random
import wave
import trial_parameters as globvar
from struct import pack
import pylink
import operator
import pickle

def prod(iterable):
        return reduce(operator.mul, iterable, 1)

class trial:
    'class to outline trial structure'
    trialCount = 0
    ts = globvar.fmri_time


#initialization of the trial parameters

    def __init__(self, kind, win, trial_number):
        self.name           = kind
        self.window         = win
        self.flip           = globvar.run_parameters['inversions'][trial_number,:]
        self.pos_stim_1     = globvar.spacing[0]    #position of right stimulus
        self.pos_stim_2     = globvar.spacing[1]    #position of left stimulus
        self.pos_marker_1   = globvar.spacing[2]    #position of motor marker 1
        self.pos_marker_2   = globvar.spacing[3]    #position of motor marker 2
        self.pos_reward_1   = globvar.spacing[4]    #position of the prize for task 1
        self.pos_reward_2   = globvar.spacing[5]    #position of the prize for task 2
        self.pos_fixcross   = globvar.spacing[6]    #position of fixation cross
        self.dif_stim_1     = globvar.run_parameters['difficulties'][trial_number,0]       #difficulty for fist stimulus
        self.dif_stim_2     = globvar.run_parameters['difficulties'][trial_number,1]       #difficulty for second stimulus
        self.par_stim_1     = globvar.run_parameters['stim_parameters'][trial_number,0]
        self.par_stim_2     = globvar.run_parameters['stim_parameters'][trial_number,1]
        self.reward_1       = globvar.run_parameters['rewards'][trial_number,0]
        self.reward_2       = globvar.run_parameters['rewards'][trial_number,1]
        self.time_stim_1    = globvar.run_parameters['timing'][trial_number,0]*trial.ts  #display time for stimulus
        self.time_break_1   = globvar.run_parameters['timing'][trial_number,1]*trial.ts  #display time for first delay
        self.time_stim_2    = globvar.run_parameters['timing'][trial_number,2]*trial.ts  #display time for stimulus
        self.time_break_2   = globvar.run_parameters['timing'][trial_number,3]*trial.ts  #display time for first delay
        self.time_delay_1   = globvar.run_parameters['timing'][trial_number,4]*trial.ts  #display time for first delay
        self.time_options   = globvar.run_parameters['timing'][trial_number,5]*trial.ts  #display time for decision screen
        self.time_delay_2   = globvar.run_parameters['timing'][trial_number,6]*trial.ts  #display time for first delay
        self.time_decision  = globvar.run_parameters['timing'][trial_number,7]*trial.ts  #display time for decision screen
        self.time_baseline  = globvar.run_parameters['timing'][trial_number,8]*trial.ts  #display time for baseline
        trial.trialCount    += 1

#routine to return user input data from the trial
    def getData(self):
        return  self.name, \
                self.user_input[0], \
                self.user_input[1], \
                self.user_input[2], \
                self.user_input[3], \
                round(self.user_input[4],4), \
                self.user_input[5], \
                self.user_input[6], \
                round(self.user_input[7],4)

#routine to return timing date from the trial
    def getTiming(self):
        return  self.name, \
                self.t_stimuli, \
                self.t_delay_1, \
                self.t_options, \
                self.t_delay_2, \
                self.t_response, \
                self.t_baseline, \
                self.t_end, self.tR

#routine to present stimuli
    def present_stimuli(self):
        #define fixation cross
        cross   = visual.TextStim(  self.window, color=-1, colorSpace='rgb', 
                                    text='+', pos=self.pos_fixcross, 
                                    height=globvar.text_height*globvar.f_y)
        
        #define stimuli here as stim_1 and stim_2 according to self.name 
        #with difficulties from randomization 'dot' is for random dot movement, 
        #'math' is for arithmetic task and 'noise' will be for noise task
        
        #Random dot motion stimulus
        if self.name=='dot':
            #randomly choose direction of rdm and according correct answer
            dot_direction_1, self.correct_answer_easy = random.choice(globvar.possible_rdm_directions)
            dot_direction_2, self.correct_answer_hard = random.choice(globvar.possible_rdm_directions)
            #setup rdm coherences from difficulty levels
            dot_coherence_1, dot_coherence_2 = self.par_stim_1, self.par_stim_2
            #put dot stimuli into a list
            stim = []
            stim.extend([visual.DotStim(
                    #constant parameters for dot motion
                    self.window, color=(1.0,1.0,1.0), nDots=500, fieldShape='circle',
                    dotLife=2, signalDots='same', noiseDots='direction', speed=0.01, 
                    #variable parameters for dot motion
                    fieldSize=4*globvar.size,
                    coherence=dot_coherence_1,
                    dir=dot_direction_1,
                    fieldPos=self.pos_stim_1
                    )])
            stim.extend([visual.DotStim(
                    #constant parameters for dot motion
                    self.window, color=(1.0,1.0,1.0), nDots=500, fieldShape='circle',
                    dotLife=2, signalDots='same', noiseDots='direction', speed=0.01, 
                    #variable parameters for dot motion
                    fieldSize=4*globvar.size,
                    coherence=dot_coherence_2,
                    dir=dot_direction_2,
                    fieldPos=self.pos_stim_2
                    )])
            #resize stimuli according to screen size
            for stimulus in stim:
                stimulus.fieldSize*=(globvar.f_x,globvar.f_y)
            #initiat countdown for total stimulu spresentation
            t1 = self.time_stim_1+self.time_stim_2+self.time_break_1+self.time_break_2
            dot_timer = core.CountdownTimer(t1)
            nout = 0
            #present stimuli and breaks according to timing and print entries to timestamp file
            #cycle to refresh dots
            while True :
                t = t1 - dot_timer.getTime()
                if (t>=t1):
                    break
                if (0<t and t<self.time_stim_1):
                    stim[0].draw()
                elif (  self.time_stim_1+self.time_break_1<t and 
                        t<self.time_stim_1 + self.time_break_1 + self.time_stim_2):
                    stim[1].draw()

                if(t>=0 and nout == 0):
                    nout += 1
                    print>>globvar.output_run_timing, globvar.run_timer[-1].getTime(), \
                            'start_visual_stim', 1, 'difficulty =', self.dif_stim_1
                if(t>=self.time_stim_1 and nout == 1):
                    nout += 1
                    print>>globvar.output_run_timing, globvar.run_timer[-1].getTime(), \
                            'start_break', 1
                if(t>self.time_stim_1+self.time_break_1 and nout == 2):
                    nout += 1
                    print>>globvar.output_run_timing, globvar.run_timer[-1].getTime(), \
                            'start_visual_stim', 2, 'difficulty =', self.dif_stim_2
                if(t>self.time_stim_1+self.time_break_1+self.time_stim_2 and nout == 3):
                    nout += 1
                    print>>globvar.output_run_timing, globvar.run_timer[-1].getTime(), \
                            'start_break', 2
               
                cross.draw()
                self.window.flip()
                core.wait(0.01)
        
        #Arithmetic task
        elif self.name=='math':
            #generate numbers for the actual arithmetic task
            self.numbers_to_sum = np.zeros((4))
            for i in range(4):
                self.numbers_to_sum[i] = np.random.randint(1,21)
            self.correct_answer = sum(self.numbers_to_sum)
            #build intervals around the correct answer
            easy_interval = '+/-'+`int(self.par_stim_1)`
            hard_interval = '+/-'+`int(self.par_stim_2)`

            #Ofset of numbers from absolute task position
            x_offset = globvar.size*globvar.f_x
            y_offset = globvar.size*globvar.f_y
            relative_number_possitions=[(-x_offset,-y_offset),
                                        ( x_offset,-y_offset),
                                        ( x_offset, y_offset),
                                        (-x_offset, y_offset)]
            numbers = np.zeros((2,4))
            #Generation of numbers to sum over by the participant
            for i in range(4):
                numbers[0,i] = np.random.randint(1,21)
                numbers[1,i] = np.random.randint(1,21)
            #generate stimuli and put them in a list
            stim_1 = []
            stim_2 = []
            for i in range(4):
                #calculate the positions of the numbers relative to the absolute task position
                p1 = tuple(x+y for x,y in zip(self.pos_stim_1, relative_number_possitions[i]))
                p2 = tuple(x+y for x,y in zip(self.pos_stim_2, relative_number_possitions[i]))
                #add all numbers belonging to one task to one list.
                stim_1.extend([ visual.TextStim(self.window, text=`int(numbers[0,i])`, pos=p1,
                                height=globvar.text_height*globvar.f_y)])
                stim_2.extend([ visual.TextStim(self.window, text=`int(numbers[1,i])`, pos=p2,
                                height=globvar.text_height*globvar.f_y)])
            #append confidence intervals to stimuli list
            stim_1.extend([visual.TextStim(self.window, text=easy_interval, color='red', 
                colorSpace='rgb', pos = (0,1.7*y_offset), height=globvar.text_height*globvar.f_y)])
            stim_2.extend([visual.TextStim(self.window, text=hard_interval, color='red', 
                colorSpace='rgb', pos = (0,1.7*y_offset), height=globvar.text_height*globvar.f_y)])
            #initiata countdown timer for total stimulus presentation time
            t1 = self.time_stim_1+self.time_stim_2+self.time_break_1+self.time_break_2
            dot_timer = core.CountdownTimer(t1)
            nout = 0
            #present stimuli and write entries to timestamp file accordingly
            while True :
                t = t1 - dot_timer.getTime()
                if (t>=t1):
                    break
                if (0<t and t<self.time_stim_1):
                    [stim.draw() for stim in stim_1]
                elif (  self.time_stim_1+self.time_break_1<t and
                        t<self.time_stim_1 + self.time_break_1 + self.time_stim_2):
                    [stim.draw() for stim in stim_2]

                if(t>=0 and nout == 0):
                    nout += 1
                    print self.dif_stim_1, self.par_stim_1
                    print>>globvar.output_run_timing, globvar.run_timer[-1].getTime(), \
                            'start_arithmetic_stim', 1, 'difficulty =', self.dif_stim_1
                if(t>=self.time_stim_1 and nout == 1):
                    nout += 1
                    print>>globvar.output_run_timing, globvar.run_timer[-1].getTime(), \
                            'start_break', 1
                if(t>self.time_stim_1+self.time_break_1 and nout == 2):
                    print self.dif_stim_2, self.par_stim_2
                    nout += 1
                    print>>globvar.output_run_timing, globvar.run_timer[-1].getTime(), \
                            'start_arithmetic_stim', 2, 'difficulty =', self.dif_stim_2
                if(t>self.time_stim_1+self.time_break_1+self.time_stim_2 and nout == 3):
                    nout += 1
                    print>>globvar.output_run_timing, globvar.run_timer[-1].getTime(), \
                            'start_break', 2
               
                cross.draw()
                self.window.flip()
                core.wait(0.01)


        #Auditory trial:
        elif self.name=='audio':
            stim_files=globvar.audio_files
            #we weather ru|lu or ba|da sould be right resp. left
            sounds = [['ru','lu'],['ba','da']]
            rd = range(3)
            for i in range(3):
                rd[i] = np.random.randint(0,2)
            i_1 = rd[0]
            i_2 = (rd[0]+1)%2
            #and chose then, which of ru|lu and ba|da will be played
            sound_1 = sounds[i_1][rd[1]]
            sound_2 = sounds[i_2][rd[2]]
            #then we open the according wav files
            file_1 = wave.open(sound_1 + '.wav','r')
            file_2 = wave.open(sound_2 + '.wav','r')
            #and get their file details
            #Returns a tuple (nchannels, sampwidth, framerate, nframes, comptype, compname)
            file_1_parameters = file_1.getparams()
            file_2_parameters = file_2.getparams()
            #since the sound tracks will be combined, they must have the same length
            sound_frames = min(file_1_parameters[3], file_2_parameters[3])
            #read raw wav data from files
            file_1_raw = file_1.readframes(sound_frames)
            file_2_raw = file_2.readframes(sound_frames)
            #unpack wav data to be able to work with it
            file_1_data = np.frombuffer(file_1_raw, dtype='<i2')
            file_2_data = np.frombuffer(file_2_raw, dtype='<i2')
            #extract maximum amplitude from wav data
            max_amp_file_1 = max(abs(file_1_data))
            max_amp_file_2 = max(abs(file_2_data))
            #create white noise
            noise = np.random.randn(sound_frames)
            #set noise levels
            noise_level_1 = self.par_stim_1
            noise_level_2 = self.par_stim_2
            #ad noise to signals
            stim_1_data = np.zeros((sound_frames))
            stim_2_data = np.zeros((sound_frames))
            for i in range(sound_frames):
                stim_1_data[i] = (  file_1_data[i]*(1-noise_level_1) 
                                    + noise[i]*noise_level_1*file_1_data[i]*globvar.noise_factor)
                stim_2_data[i] = (  file_2_data[i]*(1-noise_level_2) 
                                    + noise[i]*noise_level_2*file_2_data[i]*globvar.noise_factor)
                #cut sound tracks if their combined amplitude exceeds the max_amplitude of the source file
                if abs(stim_1_data[i]) > max_amp_file_1:
                    sign_1 = file_1_data[i]/abs(file_1_data[i])
                    stim_1_data[i] = max_amp_file_1*sign_1
                if abs(stim_2_data[i]) > max_amp_file_2:
                    sign_2 = file_2_data[i]/abs(file_2_data[i])
                    stim_2_data[i] = max_amp_file_2*sign_2
            #normalize audio streams to fixed amplitude
            amp1 = max(abs(stim_1_data))
            amp2 = max(abs(stim_2_data))
            max_amp = globvar.max_amp
            stim_2_data = stim_2_data/amp2*max_amp
            stim_1_data = stim_1_data/amp1*max_amp
            #open output files
            stim_file_1 = wave.open(stim_files[0], 'w')
            stim_file_2 = wave.open(stim_files[1], 'w')
            #set output file parameters
            stim_file_1.setparams((2,2,file_1_parameters[2],0,'NONE', 'not compressed'))
            stim_file_2.setparams((2,2,file_1_parameters[2],0,'NONE', 'not compressed'))
            #merge sound tracks for output and pack them to an appropriate data format
            stim_sound_data_1 = ''
            stim_sound_data_2 = ''
            for i in range(sound_frames):
                stim_sound_data_1 += pack('h', stim_1_data[i]) #track for file_1
                stim_sound_data_1 += pack('h', stim_1_data[i]) #track for file_1
                stim_sound_data_2 += pack('h', stim_2_data[i]) #track for file_2
                stim_sound_data_2 += pack('h', stim_2_data[i]) #track for file_2
            #write data to file
            stim_file_1.writeframes(stim_sound_data_1)
            stim_file_2.writeframes(stim_sound_data_2)
            stim_file_1.close()
            stim_file_2.close()
            file_1.close()
            file_2.close()
            #generate sound stimulus. open sound files in row
            audit_stim_1 = sound.Sound(value=stim_files[0], sampleRate = file_1_parameters[3])
            audit_stim_2 = sound.Sound(value=stim_files[1], sampleRate = file_1_parameters[3])
            speaker_symbol = visual.ImageStim(  self.window, 
                                                image=globvar.speaker_symbol, 
                                                pos=(0,globvar.size), 
                                                size = globvar.speaker_size*globvar.f_y)
            #draw other objects
            cross.draw()
            #flip window and play sound
            self.window.flip()
            #initiate countdown timer for stim time
            t1 = self.time_stim_1+self.time_stim_2+self.time_break_1+self.time_break_2
            dot_timer = core.CountdownTimer(t1)
            start1, stop1 = False, False
            start2, stop2 = False, False
            nout = 0
            #play sounds and pause for breaks
            while True :
                t = t1 - dot_timer.getTime()
                if (t>=t1):
                    break
                if (0<t and start1 == False):
                    audit_stim_1.play(loops = 0)
                    start1 = True
                    print '1 started'
                if (0<t and t<self.time_stim_1):
                    cross.draw()
                    speaker_symbol.draw()
                elif (self.time_stim_1<t and stop1 == False):
                    audit_stim_1.stop()
                    stop1 = True
                    print '1 stopped'
                elif (  self.time_stim_1+self.time_break_1<t 
                        and start2 == False):
                    audit_stim_2.play(loops = 0)
                    start2 = True
                    print '2 started'
                elif (  self.time_stim_1+self.time_break_1<t 
                        and t<self.time_stim_1 + self.time_break_1 + self.time_stim_2):
                    cross.draw()
                    speaker_symbol.draw()
                elif (  self.time_stim_1 + self.time_break_1 + self.time_stim_2<t 
                        and stop2 == False):
                    audit_stim_2.stop()
                    stop2 = True
                    print '2 stopped'

                #write timestamps according to stimuli
                if(t>=0 and nout == 0):
                    nout += 1
                    print self.dif_stim_1, self.par_stim_1
                    print>>globvar.output_run_timing, globvar.run_timer[-1].getTime(), \
                            'start_auditory_stim', 1, 'difficulty =', self.dif_stim_1
                if(t>=self.time_stim_1 and nout == 1):
                    nout += 1
                    print>>globvar.output_run_timing, globvar.run_timer[-1].getTime(), \
                            'start_break', 1
                if(t>self.time_stim_1+self.time_break_1 and nout == 2):
                    print self.dif_stim_2, self.par_stim_2
                    nout += 1
                    print>>globvar.output_run_timing, globvar.run_timer[-1].getTime(), \
                            'start_auditory_stim', 2, 'difficulty =', self.dif_stim_2
                if(t>self.time_stim_1+self.time_break_1+self.time_stim_2 and nout == 3):
                    nout += 1
                    print>>globvar.output_run_timing, globvar.run_timer[-1].getTime(), \
                            'start_break', 2
               
                self.window.flip()

#Option slide with markers and rewards
    def present_options(self):
        #reverse position of markers if flip[0] == -1
        if self.flip[2] == 1:
            mpos1 = self.pos_marker_1
            mpos2 = self.pos_marker_2
        elif self.flip[2] == -1:
            mpos1 = self.pos_marker_2
            mpos2 = self.pos_marker_1
        #define marker stimuli with files defined in globvar.py
        print globvar.file_marker_1, mpos1
        marker_1= visual.ImageStim( self.window, 
                                    image=globvar.file_marker_1,
                                    pos=mpos1,
                                    size = globvar.marker_size)
        marker_2= visual.ImageStim( self.window, 
                                    image=globvar.file_marker_2,
                                    pos=mpos2,
                                    size = globvar.marker_size)
        #resize markers according to display size
        marker_1.size*=(globvar.f_x,globvar.f_y)
        marker_2.size*=(globvar.f_x,globvar.f_y)
        #define fixation cross
        cross   = visual.TextStim(  self.window, 
                                    color=-1, 
                                    colorSpace='rgb', 
                                    text='+',
                                    pos=self.pos_fixcross, 
                                    height=globvar.text_height*globvar.f_y)
        #define reward stimuli according to the possitions of the easy and hard_l task
        eur = u"\u20AC"
        reward_1 = visual.TextStim( self.window, 
                                    text= `round(self.reward_1,2)` + eur,
                                    pos=self.pos_reward_1, 
                                    height=globvar.text_height*globvar.f_y)
        reward_2 = visual.TextStim( self.window, 
                                    text= `round(self.reward_2,2)` + eur,
                                    pos=self.pos_reward_2, 
                                    height=globvar.text_height*globvar.f_y)

        #write markers and rewards to screen
        event.clearEvents()
        marker_1.draw()
        marker_2.draw()
        reward_1.draw()
        reward_2.draw()
        cross.draw()
        print>>globvar.output_run_timing, globvar.run_timer[-1].getTime(), \
                'start_option_presentation'
        timer = core.CountdownTimer(self.time_options)
        self.window.flip()

        #check for premature input
        while timer.getTime() > 0:
            for key in event.getKeys():
                print>>globvar.output_run_timing, globvar.run_timer[-1].getTime(), \
                        'PREMATURE INPUT', key

#Delay slide 1 without interactivity

    def present_delay_1(self):
        timer = core.CountdownTimer(self.time_delay_1)
        print 'define slide B'
        self.window.clearBuffer()
        #define fixation cross
        cross = visual.TextStim(self.window, 
                                color=-1, 
                                colorSpace='rgb', 
                                text='+',
                                pos=self.pos_fixcross, 
                                height=globvar.text_height*globvar.f_y)

        #draw fixation cross to screen
        cross.draw()
        event.clearEvents()
        self.premature_input = []
        active = False
        #write timestamp to file
        print>>globvar.output_run_timing, globvar.run_timer[-1].getTime(), \
                'start_delay', 1
        self.window.flip()

        #check for premature user input
        while timer.getTime() > 0:
            for key in event.getKeys():
                self.premature_input = ['premature input',key]
                print>>globvar.output_run_timing, globvar.run_timer[-1].getTime(), \
                        'PREMATURE INPUT', key
                active = True
        if active == False:
            self.premature_input = ['no input during delay','']


#Delay slide 2 without interactivity

    def present_delay_2(self):
        timer = core.CountdownTimer(self.time_delay_2)
        print 'define slide B'
        self.window.clearBuffer()
        #define fixation cross
        cross = visual.TextStim(self.window, 
                                color=-1, 
                                colorSpace='rgb', 
                                text='+',
                                pos=self.pos_fixcross, 
                                height=globvar.text_height*globvar.f_y)

        #draw cross to screen
        cross.draw()
        event.clearEvents()
        self.premature_input = []
        active = False
        #write timestamp to file
        print>>globvar.output_run_timing, globvar.run_timer[-1].getTime(), \
                'start_delay', 2
        self.window.flip()

        #check for premature user input
        while timer.getTime() > 0:
            for key in event.getKeys():
                self.premature_input = ['premature input',key]
                print>>globvar.output_run_timing, globvar.run_timer[-1].getTime(), \
                        'PREMATURE INPUT', key
                active = True
        if active == False:
            self.premature_input = ['no input during delay','']


#Decision slide presented during recording of user input

    def present_response(self):
        print 'present slide C'
        
        #revert marker possitions according to flip
        self.window.clearBuffer()
        if self.flip[3] == 1:
            mpos1 = self.pos_marker_1
            mpos2 = self.pos_marker_2
        elif self.flip[3] == -1:
            mpos1 = self.pos_marker_2
            mpos2 = self.pos_marker_1
        #define markers
        marker_1= visual.ImageStim( self.window, 
                                    image=globvar.file_marker_1,
                                    pos=mpos1,
                                    size =globvar.marker_size)
        marker_2= visual.ImageStim( self.window, 
                                    image=globvar.file_marker_2,
                                    pos=mpos2, 
                                    size = globvar.marker_size)
        #resize markers according to display size
        marker_1.size*=(globvar.f_x,globvar.f_y)
        marker_2.size*=(globvar.f_x,globvar.f_y)
        #define fixation cross
        cross   = visual.TextStim(self.window, 
                                    color='red', 
                                    colorSpace='rgb', 
                                    text='+',
                                    pos=self.pos_fixcross, 
                                    height=globvar.text_height*globvar.f_y)
        #draw markers and fixation cross to buffer
        marker_1.draw()
        marker_2.draw()
        cross.draw()
        #clear events: empty user input list before response is recorded
        event.clearEvents()
        #initiate countown for response time
        timer = core.CountdownTimer(self.time_decision)
        #present response slide and write timestamp to file
        print>>globvar.output_run_timing, globvar.run_timer[-1].getTime(), \
                'start_option_presentation'
        self.window.flip()
        #wait for time_decision seconds for user input
        #record keystroke here as [input==True, key, rt]
        self.user_input = []
        user_active = False
        input_correct = False
        nout = 0
        while timer.getTime()>=0:
            #get user input
            for key in event.getKeys(keyList=['left','right', 'p', 'escape']):
                #if user made input, write timestamp to file
                print>>globvar.output_run_timing, globvar.run_timer[-1].getTime(), \
                        'user_input', key
                #check wheather user input is one of left, right 
                #and set his choice parameter accordingly
                if key in ['left', 'right']:
                    self.tR = self.time.getTime()-self.t_response
                    if key == 'left':
                        choice = 1
                    elif key == 'right':
                        choice = -1
                    marker_flips = [2,3]
                    EV_flips = [1,2,3]
                    #figure out which reward/difficulty level the user 
                    #accepted/rejected by cross checking his choice
                    #with the position of the elements in the trial. 
                    #by default easy trial is first, low reward is left and
                    #marker_1 is always left each deviation of this setup 
                    #is given by a flip = -1.
                    if prod(self.flip[marker_flips])*choice == 1:
                        accepted_choice_reward = self.reward_1
                        rejected_choice_reward = self.reward_2
                        accepted_choice_dif = self.dif_stim_1
                        rejected_choice_dif = self.dif_stim_2
                    elif prod(self.flip[marker_flips])*choice == -1:
                        accepted_choice_reward = self.reward_2
                        rejected_choice_reward = self.reward_1
                        accepted_choice_dif = self.dif_stim_2
                        rejected_choice_dif = self.dif_stim_1
                    if prod(self.flip[EV_flips])*choice == 1:
                        accepted_EV = 'high'
                    elif prod(self.flip[EV_flips])*choice == -1:
                        accepted_EV = 'low'
                     
                    print>>globvar.output_run_timing, globvar.run_timer[-1].getTime(), \
                            'choice_difficulty', accepted_choice_dif, 'choice_EV', \
                            accepted_choice_reward*accepted_choice_dif, '('+accepted_EV+')'
                    user_active = True
                    input_correc = True
                    self.user_input = [ 1,
                                        key,
                                        accepted_choice_dif, 
                                        accepted_choice_reward, 
                                        accepted_choice_dif*accepted_choice_reward, 
                                        rejected_choice_dif, 
                                        rejected_choice_reward, 
                                        rejected_choice_dif*rejected_choice_reward]
                    break
                #check wheaterh user wants to exit experiment
                elif key in ['escape']:
                    print 'aborting'
                    message = visual.TextStim(  win=self.window, 
                                                text='you pressed escape. \n The experiment will now end.', 
                                                height=globvar.text_height*globvar.f_y)
                    message.draw()
                    self.window.flip()
                    core.wait(3)
                    self.window.close()
                    core.quit()
                #pause experiment if user presses 'p'
                elif key in ['p']:
                    self.tR = -78
                    pause = True
                    message = visual.TextStim(  win=self.window, 
                                                text='the experiment is paused \n press p again to continue', 
                                                height=globvar.text_height*globvar.f_y)
                    message.draw()
                    self.window.flip()
                    while pause == True:
                        for key in event.getKeys(keyList=['p']):
                            if key == 'p':
                                pause = False
            if user_active == False:
                self.tR = -78
                self.user_input = [0,'none',0,0,0,0,0,0]

    #Baseline slide
    def present_baseline(self):
        timer = core.CountdownTimer(self.time_baseline)
        print 'define slide D'
        event.clearEvents()
        self.window.clearBuffer()
        cross = visual.TextStim(self.window, 
                                color=-1, 
                                colorSpace='rgb', 
                                text='+', 
                                pos=self.pos_fixcross, 
                                height=globvar.text_height*globvar.f_y)
        cross.draw()
        print>>globvar.output_run_timing, globvar.run_timer[-1].getTime(),\
                'start_baseline'
        self.window.flip()
        while timer.getTime() > 0:
            for key in event.getKeys():
                print>>globvar.output_run_timing, globvar.run_timer[-1].getTime(), \
                        'LATE INPUT', key


#Method to run trial i.e. define slides, show for certain time, record user input. Store data.

    def run_trial(self):
        #start time counter for the trial
        self.time = core.MonotonicClock()
#------------------------------------
        #get time of presentation of task slide from time counter
        self.t_stimuli = self.time.getTime()
        #present stimulus slide for time self.time_stimulus
        self.present_stimuli()
#------------------------------------
        #get time for presentation of delay slide
        self.t_delay_1 = self.time.getTime()
        #first delay slide
        self.present_delay_1()
#------------------------------------
        #show choice options and rewards
        self.t_options = self.time.getTime()
        self.present_options()
#------------------------------------
        #second delay slide
        self.t_delay_2 = self.time.getTime()
        self.present_delay_2()
#------------------------------------
        #response slide shows motor markers and records user input.
        #get start time
        self.t_response = self.time.getTime()
        #present slide
        self.present_response()
#------------------------------------
        #slide for baseline time
        #get time of baseline slide
        self.t_baseline = self.time.getTime()
        #present baseline slide
        self.present_baseline()
        #get time of end of trial
        self.t_end = self.time.getTime()


#----------------------------------------------------------------------------
#this class can be used to generate the parameters for the trials on an experiment.
#input is:
#modus              :the modus for the next trials (math, dot or audio)
#number_of_trials   :the number of the next trials of type modus
#max_rep            :the maximum number of repetitions in the parameter series allowed
#dif_easy, dif_hard :the difficulty levels for the next trials
#mean_delay_average :mean time of delay slide in units of fmri 
#mean_baseline_average:mean time of baseline slide in units of fmri
#output is timing, difficulties and inversions for the next series of trials

#----------------------------------------------------------------------------
class init:
    'class to randomize trial parameters'

    def __init__(self):
        self.number_of_trials = globvar.blocks[0]*globvar.blocks[1]
        
    def load_trial_parameters(self):
        
        with open('run_parameters/run_'+`globvar.run_number`+'_parameters_.p', 'rb') as fp:
                    globvar.run_parameters = pickle.load(fp)

    def participant_parameter_dialog(self):
       # first, we ask for the subject id etc
       myDlg = gui.Dlg(title="Flavia's fMRI Study")
       myDlg.addText('Subject info')
       myDlg.addField('ID:', globvar.participant_id)
       myDlg.addText('RDM coherence')
       myDlg.addField('easy:', globvar.dot_motion_trial_coherence[0])
       myDlg.addField('hard:', globvar.dot_motion_trial_coherence[1])
       myDlg.addText('Auditory noise')
       myDlg.addField('easy:', globvar.audio_trial_stn_ratio[0])
       myDlg.addField('hard:', globvar.audio_trial_stn_ratio[1])
       myDlg.addText('Arithmetic range')
       myDlg.addField('easy:', globvar.math_trial_interval[0])
       myDlg.addField('hard:', globvar.math_trial_interval[1])
       myDlg.addText('Expected accuracy')
       myDlg.addField('easy:', globvar.anticipated_participant_performance[0])
       myDlg.addField('hard:', globvar.anticipated_participant_performance[1])
       myDlg.addText('Run number')
       myDlg.addField('Nr.', globvar.run_number)
       myDlg.show()  # show dialog and wait for OK or Cancel
       if myDlg.OK:  # then the user pressed OK
           subjinfo = myDlg.data
           globvar.participant_id = subjinfo[0]
           globvar.dot_motion_trial_coherence[0] = subjinfo[1]
           globvar.dot_motion_trial_coherence[1] = subjinfo[2]
           globvar.audio_trial_stn_ratio[0] = subjinfo[3]
           globvar.audio_trial_stn_ratio[1] = subjinfo[4]
           globvar.math_trial_interval[0] = subjinfo[5]
           globvar.math_trial_interval[1] = subjinfo[6]
           globvar.anticipated_participant_performance[0] = subjinfo[7]
           globvar.anticipated_participant_performance[1] = subjinfo[8]
           globvar.run_number = subjinfo[9]
    def randomize_participant_specific_variables(self):
        blocks = globvar.run_parameters['blocks']
        EV_gap = globvar.run_parameters['EV_gap']
        EV_values = globvar.run_parameters['EV_values']
        timing = globvar.run_parameters['timing']
        inversions = globvar.run_parameters['inversions']


        #deduced variables:     first/second participant performance aka. 
        #                       difficulties, fist/second stim_parameter
        difficulties = np.zeros((self.number_of_trials,2))
        stim_parameters = np.zeros((self.number_of_trials,2))

        #calculated variables:  Rewards(left, right)
        rewards = np.zeros((self.number_of_trials,2))

        #fig1 = mp.figure()
        #mp.hist(EV_value[:,0] - EV_value[:,1], bins = 2)
        #fig2 = mp.figure()
        #mp.hist(abs(EV_value[:,0] - EV_value[:,1]), bins = 2)
        #mp.show()

        #set first/second expected participant performance and stimulus parameter

        for i in range(globvar.blocks[0]):
            kind = blocks[i]
            i1 = i*globvar.blocks[1]
            i2 = (i+1)*globvar.blocks[1]
            for j in range(i1,i2):
                difficulty = globvar.anticipated_participant_performance 
                if kind == 'math':
                    stim_parameter = globvar.math_trial_interval
                elif kind == 'dot':
                    stim_parameter = globvar.dot_motion_trial_coherence
                elif kind == 'audio':
                    stim_parameter = globvar.audio_trial_stn_ratio
                if inversions[j,0] == 1:
                    difficulties[j,:] = difficulty
                    stim_parameters[j,:] = stim_parameter
                elif inversions[j,0] == -1:
                    difficulties[j,:] = [difficulty[1],difficulty[0]]
                    stim_parameters[j,:] = [stim_parameter[1], stim_parameter[0]]

        #calculate left/right rewards from participant performance and EV

        for i in range(self.number_of_trials):
            for j in range(2):
                rewards[i,j] = round(float(EV_values[i,j])/difficulties[i,j],globvar.digits)
                EV_values[i,j] = rewards[i,j]*difficulties[i,j]

        globvar.run_parameters['EV_values'] = EV_values
        globvar.run_parameters['difficulties'] = difficulties
        globvar.run_parameters['stim_parameters'] = stim_parameters
        globvar.run_parameters['rewards'] = rewards

        with open('full_run_parameters_participant'+`globvar.participant_id`+'run'+`globvar.run_number`+'.p', 'wb') as fb:
                    pickle.dump(globvar.run_parameters, fb)

        return blocks, EV_gap, timing, inversions, EV_values, difficulties, stim_parameters, rewards

