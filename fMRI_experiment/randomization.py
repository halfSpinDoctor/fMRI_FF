import numpy as np
import trial_parameters as tp
import random
import pickle
import datetime
import matplotlib.pyplot as mp

number_of_trials = tp.blocks[0]*tp.blocks[1]

for f in range(6):

    #balanced variables:    Modus order, EV_gap
    blocks = []
    EV_gap = []
    #random variables:      inversions(stim order, option marker possition, decision marker possition, higher EV possition),
    #                       timing, Actual EV(left, right)
    timing = np.zeros((number_of_trials,9))
    inversions = np.zeros((number_of_trials,4))
    

    #balance Modus order
    j = random.randint(1,np.shape(tp.trial_modi)[0])
    for i in range(tp.blocks[0]):
        blocks.append(tp.trial_modi[(i+j)%np.shape(tp.trial_modi)[0]])
    random.shuffle(blocks) 


    #balance EV_gaps

    for i in range(tp.blocks[0]):
        gap_tmp = []
        i1 = i*tp.blocks[1]
        i2 = (i+1)*tp.blocks[1]
        for j in range(tp.blocks[1]):
                if j<tp.blocks[1]/2:
                    gap_tmp.append('large')
                elif j>=tp.blocks[1]/2:
                    gap_tmp.append('small')
        random.shuffle(gap_tmp)
        EV_gap = np.append(EV_gap,gap_tmp)
            
    #randimize inversions

    for k in range(tp.blocks[0]):
        i1 = k*tp.blocks[1]
        i2 = (k+1)*tp.blocks[1]
        too_many_repetitions = True
        while too_many_repetitions == True:
            inversions[i1:i2,0:4] = [0,0,0,0]
            for i in range(i1,i2):
                inversions[i,0] = random.choice([-1,1])
                inversions[i,1] = random.choice([-1,1])
                inversions[i,2] = random.choice([-1,1])
                inversions[i,3] = random.choice([-1,1])

            #check if the maximum number of repetitions satisfies max_rep
            too_many_repetitions = False
            for i in range(i1,i2 - tp.max_rep):
                same_1 = True
                same_2 = True
                same_3 = True
                same_4 = True
                for j in range(i,i+tp.max_rep):
                    if inversions[j,0] != inversions[i,0]:
                        same_1 = False
                    if inversions[j,1] != inversions[i,1]:
                        same_2 = False
                    if inversions[j,2] != inversions[i,2]:
                        same_3 = False
                    if inversions[j,3] != inversions[i,3]:
                        same_4 = False
                if same_1 == True or same_2 == True or same_3 == True or same_4 == True:
                        too_many_repetitions = True
                        break
    #randomize timings

    if tp.geometric_parameter == 'mean':
        delay_1_prob = 1./tp.mean_delay_1_trs
        delay_2_prob = 1./tp.mean_delay_2_trs
        baseline_prob = 1./tp.mean_baseline_trs
    if tp.geometric_parameter == 'meadian':
        print 'median probabilities not yet implemented'

    for i in range(tp.blocks[0]):
        kind = blocks[i]
        i1 = i*tp.blocks[1]
        i2 = (i+1)*tp.blocks[1]
        no_long_trials = True
        too_long_trials = True
        while (no_long_trials or too_long_trials) == True :
            if kind == 'math':
                timing[i1:i2,0] = tp.time_math_stim_1
                timing[i1:i2,1] = tp.time_break_1
                timing[i1:i2,2] = tp.time_math_stim_2
                timing[i1:i2,3] = tp.time_break_2
            if kind == 'dot':
                timing[i1:i2:,0] = tp.time_dot_stim_1
                timing[i1:i2:,1] = tp.time_break_1
                timing[i1:i2:,2] = tp.time_dot_stim_2
                timing[i1:i2:,3] = tp.time_break_2
            if kind == 'audio':
                timing[i1:i2,0] = tp.time_audio_stim_1
                timing[i1:i2,1] = tp.time_break_1
                timing[i1:i2,2] = tp.time_audio_stim_2
                timing[i1:i2,3] = tp.time_break_2
            for j in range(i1,i2):
                tmp = tp.max_delay_ts
                while tmp>=tp.max_delay_ts:
                    tmp = np.random.geometric(delay_1_prob)
                timing[j,4] = tmp

            timing[i1:i2,5] = tp.time_options

            for j in range(i1,i2):
                tmp = tp.max_delay_ts
                while tmp>=tp.max_delay_ts:
                    tmp = np.random.geometric(delay_2_prob)
                timing[j,6] = tmp

            timing[i1:i2,7] = tp.time_response

            for j in range(i1,i2):
                tmp = tp.max_delay_ts
                while tmp>=tp.max_delay_ts:
                    tmp = np.random.geometric(baseline_prob)
                timing[j,8] = tmp

            no_long_trials = True
            c1,c2,c3 = False,False,False
            if (timing[i1:i2,4]>=tp.long_trial_ts).sum()>=tp.long_trial_number:
                c1 = True
            if (timing[i1:i2,6]>=tp.long_trial_ts).sum()>=tp.long_trial_number:
                c2 = True
            if (timing[i1:i2,8]>=tp.long_trial_ts).sum()>=tp.long_trial_number:
                c3 = True
            if c1 == True and c2 == True and c3 == True:
                no_long_trials = False

            too_long_trials = True
            if ((timing[i1:i2,4]>tp.max_delay_ts).sum() + (timing[i1:i2,6]>tp.max_delay_ts).sum() + (timing[i1:i2,8]>tp.max_delay_ts).sum()) == 0:
                too_long_trials = False


    #fig3 = mp.figure()
    #ax3 = fig3.add_subplot(111)
    #ax3.plot(rewards[:,0], rewards[:,1], 'o')
    #ax3.set_xlabel('right reward')
    #ax3.set_ylabel('left reward')
    #mp.savefig('run_parameters/run_'+`f+1`+'reward_scatterplot.pdf')
    #fig4 = mp.figure()
    #ax4 = fig4.add_subplot(111)
    #ax4.hist(rewards[:,0]-rewards[:,1])
    #mp.savefig('run_parameters/run_'+`f+1`+'reward_distance_histogram.pdf')

    fig5 = mp.figure()
    ax5=fig5.add_subplot(111)
    ax5.hist([timing[:,4],timing[:,6],timing[:,8]], label=['delay 1', 'delay 2', 'baseline'])
    ax5.legend(loc='upper right')
    ax5.set_xlabel('timing in tr')
    mp.savefig('run_parameters/run_'+`f+1`+'timing_histogramm.pdf')

    fig6 = mp.figure()
    ax6 = fig6.add_subplot(111)
    tmp = (EV_gap=='large')
    ax6.hist(tmp, bins=2, rwidth=0.8)
    ax6.set_xticks([0.25,0.75])
    labels = [item.get_text() for item in ax6.get_xticklabels()]
    labels[0] = 'small EV gap'
    labels[1] = 'large EV gap'
    ax6.set_xticklabels(labels)
    ax6.set_title('EV gap distribution over trials between small and large')
    mp.savefig('run_parameters/run_'+`f+1`+'_EV_gap_distribution_histogram.pdf')

    print 'mean delay 1 time is ', sum(timing[:,4])/number_of_trials, 'ts'
    print 'mean delay 2 time is ', sum(timing[:,6])/number_of_trials, 'ts'
    print 'mean baseline time is ', sum(timing[:,8])/number_of_trials, 'ts'
    print 'number of long delay1 time is', (timing[:,4]>=tp.long_trial_ts).sum()
    print 'number of long delay2 time is', (timing[:,6]>=tp.long_trial_ts).sum()
    print 'number of long baseline time is', (timing[:,8]>=tp.long_trial_ts).sum()


    print 'average times that difficult task is first is', (inversions[:,0]==1).sum()/float(number_of_trials)
    print 'averate times that high reward is left is', (inversions[:,1]==1).sum()/float(number_of_trials)
    print 'averate times that marker_1 is left on options slide is', (inversions[:,2]==1).sum()/float(number_of_trials)
    print 'average times that marker_1 is left on decision slide is', (inversions[:,3]==1).sum()/float(number_of_trials)
    print 'average times that EV gap is large is', (EV_gap == 'large').sum()/float(number_of_trials)
    print sum(sum(timing))

    print 'the total duration of the run is', str(datetime.timedelta(seconds=int(sum(sum(timing[:,:]))*tp.fmri_time)))

    trial_parameters = {}
    trial_parameters['blocks'] = blocks
    trial_parameters['EV_gap'] = EV_gap
    trial_parameters['timing'] = timing
    trial_parameters['inversions'] = inversions
    trial_parameters['trial_number'] = range(1,number_of_trials)

    with open('run_parameters/run_'+`f+1`+'_parameters_.p', 'wb') as fb:
                pickle.dump(trial_parameters, fb)

