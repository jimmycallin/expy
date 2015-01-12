import time
import measures
import dataset
import os
import sys
import git
from datetime import datetime

_db = dataset.connect('mysql+pymysql://root@localhost/results')

class Project(object):
    """
    Defines and creates a project and its configuration.
    If Project ID is set, just return an existing project.
    """

    def __init__(self, name=None, test_data=None, base_configuration=None, description=None, project_id=None, store=True):
        assert isinstance(test_data, dict)
        assert isinstance(base_configuration, dict)
        self.name = name
        self.test_data = test_data
        self.base_configuration = base_configuration
        self.description = description
        self.project_path = sys.argv[0]
        self.store = store
        self.experiments = []

        if project_id:
            proj = _db['Project'].find(id=project_id)
            if proj:
                self.project_id = project_id
            else:
                raise KeyError("Project {} not found in database".format(project_id))
        elif store:
            with _db as db:
                project = db['Project']
                config = db['Configuration']
                data = db['Data']
                self.project_id = project.insert({'name': self.name, 
                                                  'description': self.description,
                                                  'project_path': self.project_path})
                
                config.insert_many([{'parameter': cparameter, 'value': cvalue, 'project_id': self.project_id}
                                    for cparameter, cvalue in self.base_configuration.items()])
                
                data.insert_many([{'instance': instance, 'answer': answer, 'project_id': self.project_id} 
                                  for instance, answer in self.test_data.items()])
                      


    def new_experiment(self, predicted, configuration, description=None):        
        try:
            repo = git.Repo(sys.path[0])
            commit = repo.head.log()[0].newhexsha
        except git.InvalidGitRepositoryError as e:
            commit = None

        timestamp = datetime.now()

        self.experiments.append({'predicted': predicted,
                                 'configuration': configuration, 
                                 'description': description,
                                 'commit': commit,
                                 'timestamp': timestamp})

        with _db as db:
            experiment = db['Experiment']
            experiment_results = db['ExperimentResults']
            configuration = db['Configuration']
            data = db['Data']
            experiment_id = experiment.insert({x: y for x, y in self.experiments[-1].items() if x != 'predicted'}) 
            exp_instances = []

            for instance, pred in predicted.items():
                instance_id = data.find_one(instance=instance, id=self.project_id)
                if not instance_id:
                    raise KeyError("Predicted instance {} is not available in the project's test data".format(instance))
                exp_instances.append({'predicted': pred, 'instance_id': instance_id, 'experiment_id': experiment_id})

            experiment_results.insert_many(exp_instances)
            configuration.insert_many([{'parameter': cparam, 'value': cvalue, 'experiment_id': experiment_id}
                                              for cparam, cvalue in configuration.items()])
        return Experiment(experiment_id)

    @classmethod
    def get_project(cls, name=None, project_id=None, project_path=None):
        if name:
            return Project(project_id=_db['Project'].find_one(name=name)['id'])
        if project_id:
            proj = _db['Project'].find(id=project_id)
            if proj:
                return Project(project_id=project_id)
            else:
                raise KeyError("Project {} not found in database".format(project_id))
        if project_path:
            return Project(_db['Project'].find_one(project_path=project_path)['id'])



class Experiment(object):
    def __init__(self, experiment_id):
        self.experiment_id = experiment_id

    @property
    def actual(self):
        project_id = _db['Experiment'].findone(id=self.experiment_id)['project_id']
        return _db['Data'].find(project_id=project_id)

    @property
    def predicted(self):
        return _db['Data'].find(experiment_id=self.experiment_id)

    @property
    def precision(self):
        return measures.precision(self.actual, self.predicted)

    @property
    def recall(self):
        return measures.recall(self.actual, self.predicted)

    @property
    def f1_score(self):
        return measures.f1_score(self.actual, self.predicted)
