# Expy – Save and reproduce your experiments

Expy is a tool for saving the results of your classification experiments in a database, along with additional experiment information such as configuration settings, timestamp of run, commit ID of your experiment's code base, et cetera. The purpose of this is to help you organize your work into projects where each experiment is reproducible in five years just as easily as today.

## How to use

Create a project by existing one by instantiating the Project class:

    > test_data = {'a test instance': 'balloon', 'another test': 'fox'}
    
    > project = expy.Project(project_name="My Project", 
                           test_data=my_test_data,
                           assert_clean_repo=True)

`project_name` is the name of your project. If a project already exists, it will load the project rather than creating a new one with the same name.

`test_data` is a dictionary of test instances as keys and expected output as value. All experiments in a project has to use the same test data. 

If `assert_clean_repo` is set to True, it will make sure your source code is checked into a git repo. If you have uncommitted changes, it will refuse to run the experiments. This is good to make sure that your code base is up to date with the saved commit id for later retaining your code as it were when you first ran your experiments.

Save results of your experiment:
    
    > test_results = {'a test instance': 'balloon', 'another test': 'dog'}
    > configuration = {'parameter1': 'value1', 'parameter2': 'value2'}
    > project.new_experiment(predicted=test_results,
                             configuration=configuration,
                             description='This is just for fun.',
                             tags=['test', 'another tag'])

`predicted` is dictionary of {'test instance': 'predicted'} values. `configuration` is a dictionary containing all configuration parameters you might want to save. `tags` adds another layer of categorization.

List your experiments in a project:

    > project.experiments
    [<Experiment 1 of project RILangID. Timestamp: 2015-02-05 23:29:13>,
    <Experiment 2 of project RILangID. Timestamp: 2015-02-05 23:56:57>,
    <Experiment 3 of project RILangID. Timestamp: 2015-02-06 00:50:05>,
    <Experiment 4 of project RILangID. Timestamp: 2015-02-06 02:33:00>,
    <Experiment 5 of project RILangID. Timestamp: 2015-02-06 05:14:51>]

Produce an experiment report based on your experiment result:

    > experiment = project.experiments[0]
    > experiment.experiment_report()
    
    Precision: 0.9758328247167309
    Recall: 0.9730322088812655
    F-score: 0.9743059436317486


## Requirements

Needs a MySQL database for storing. For now you add your database user credentials in config.py. I should learn how you are supposed to setup this properly.

## Install
Make sure you have everything installed correctly under requirements. Thereafter:
    
    python setup.py install
