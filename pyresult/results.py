import time
from . import measures
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

    def __init__(self, name=None, test_data=None, base_configuration=None, description=None, project_id=None, assert_clean_repo=False):
        if assert_clean_repo:
            repo = git.Repo(sys.path[0])
            if repy.is_dirty():
                raise RuntimeError("Your repository is dirty, please commit changes to any modified files.")

        if test_data is not None:
            assert isinstance(test_data, dict)
        if base_configuration is not None:
            assert isinstance(base_configuration, dict)

        if project_id:
            proj = _db['Project'].find(id=project_id)
            if proj:
                self.project_id = project_id
            else:
                raise KeyError(
                    "Project {} not found in database".format(project_id))
        else:
            with _db as db:
                project = db['Project']
                config = db['Configuration']
                data = db['Data']
                self.project_id = project.insert({'name': name,
                                                  'description': description,
                                                  'project_path': sys.argv[0]})

                if base_configuration:
                    config.insert_many([{'parameter': cparameter, 'value': str(cvalue), 'project_id': self.project_id}
                                        for cparameter, cvalue in base_configuration.items()])

                data.insert_many([{'instance': instance, 'answer': answer, 'project_id': self.project_id}
                                  for instance, answer in test_data.items()])

    @property
    def name(self):
        if hasattr(self,'_name'):
            return self._name
        else:
            with _db as db:
                self._name = db['Project'].find_one(id=self.project_id)['name']
                return self.name

    @name.setter
    def name(self, val):
        with _db as db:
            db['Project'].update({'id':self.project_id, 'name':val}, ['id'])

        self._name = val
    
    @property
    def description(self):
        if hasattr(self,'_description'):
            return self._description
        else:
            with _db as db:
                self._description = db['Project'].find_one(
                    id=self.project_id)['description']
                return self._description

    @description.setter
    def description(self, value):
        with _db as db:
            db['Project'].update({'id':self.project_id, 'description':value}, ['id'])
            self._description = value

    @property
    def test_data(self):
        if hasattr(self,'_test_data'):
            return self._test_data
        else:
            with _db as db:
                self._test_data = {x['instance']: x['answer']
                                   for x in db['Data'].find(project_id=self.project_id)}
                return self.test_data


    @property
    def experiments(self):
        if not hasattr(self,'_experiments'):
            with _db as db:
                self._experiment = [
                    Experiment(x['id']) for x in db['Experiment'].find(project_id=self.project_id)]
        return self._experiment

    @property
    def base_configuration(self):
        if not hasattr(self,'_base_config'):
            with _db as db:
                self._base_config = {c['parameter']: c['value'] for c in db['Configuration'].find(project_id=self.project_id)}
        return self._base_config

    def new_experiment(self, predicted, configuration, description=None, tags=None):
        try:
            repo = git.Repo(sys.path[0])
            commit = repo.head.log()[0].newhexsha
            if repo.is_dirty():
                print("Warning: The git repository has uncommited changes,"
                      "the registered commit is likely to not represent the current code.")
        except git.InvalidGitRepositoryError as e:
            commit = None

        timestamp = datetime.now()

        exp = {'description': description,
               'commit': commit,
               'timestamp': timestamp,
               'project_id': self.project_id}

        with _db as db:
            experiment = db['Experiment']
            experiment_results = db['ExperimentResults']
            data = db['Data']

            experiment_id = experiment.insert(exp)
            exp_instances = []

            for instance, pred in predicted.items():
                instance_id = data.find_one(
                    instance=instance, project_id=self.project_id)['id']
                if not instance_id:
                    raise KeyError(
                        "Predicted instance {} is not available in the project's test data".format(instance))
                exp_instances.append(
                    {'predicted': pred, 'instance_id': instance_id, 'experiment_id': experiment_id})

            experiment_results.insert_many(exp_instances)
            db['Configuration'].insert_many([{'parameter': cparam, 'value': str(cvalue), 'experiment_id': experiment_id}
                                             for cparam, cvalue in configuration.items()])
            
            if tags:
                db['Tags'].insert_many([{'experiment_id': experiment_id, 'tag': str(tag)} for tag in tags])

        return Experiment(experiment_id)

    @classmethod
    def get_project(cls, name=None, test_data=None, project_id=None, project_path=None, assert_clean_repo=False):
        if name:
            proj = _db['Project'].find_one(name=name)
            if proj:
                project_id = proj['id']
        
        if project_id:
            proj = _db['Project'].find(id=project_id)
            if not proj:
                project_id = None
        
        if project_path:
            project_id = _db['Project'].find_one(project_path=project_path)['id']

        if project_id:
            return Project(project_id=project_id, assert_clean_repo=assert_clean_repo)
        else:
            raise KeyError("Project not found.")


    @classmethod
    def get_projects(cls):
        return [Project(project_id=proj['id']) for proj in _db['Project']]

    def delete_project(self):
        with _db as db:
            db['Project'].delete(id=self.project_id)
            db['Configuration'].delete(project_id=self.project_id)
            db['Data'].delete(project_id=self.project_id)
            experiments = db['Experiment'].find(project_id=self.project_id)
            for exp in experiments:
                expid = exp['id']
                db['ExperimentResults'].delete(experiment_id=expid)
                db['Configuration'].delete(experiment_id=expid)

            db['Experiment'].delete(project_id=self.project_id)

    def __repr__(self):
        return "<Project {}: {}>".format(self.project_id, self.name)


class Experiment(object):

    def __init__(self, experiment_id):
        self.experiment_id = experiment_id

    @property
    def project_name(self):
        with _db as db:
            project_id = db['Experiment'].find_one(
                id=self.experiment_id)['project_id']
            return db['Project'].find_one(id=project_id)['name']

    @property
    def project_id(self):
        with _db as db:
            project_id = db['Experiment'].find_one(
                id=self.experiment_id)['project_id']
            return project_id



    @property
    def test_data(self):
        if not hasattr(self,'_test_data'):
            project_id = _db['Experiment'].find_one(
                id=self.experiment_id)['project_id']
            self._test_data = [x['instance']
                               for x in _db['Data'].find(project_id=project_id)]
        return self._test_data

    @property
    def actual(self):
        if not hasattr(self,'_actual'):
            project_id = _db['Experiment'].find_one(
                id=self.experiment_id)['project_id']
            self._actual = [
                x['answer'] for x in _db['Data'].find(project_id=project_id, order_by='id')]
        return self._actual

    @property
    def predicted(self):
        if not hasattr(self,'_predicted'):
            with _db as db:
                query = 'select ExperimentResults.predicted from ExperimentResults  \
                        join Data on ExperimentResults.instance_id = Data.id \
                        where ExperimentResults.experiment_id = {}  \
                        order by Data.id'.format(self.experiment_id)
                self._predicted = [x['predicted'] for x in db.query(query)]
        return self._predicted

    @property
    def timestamp(self):
        return _db['Experiment'].find_one(id=self.experiment_id)['timestamp']

    @property
    def description(self):
        return _db['Experiment'].find_one(id=self.experiment_id)['description']

    @property
    def configuration(self):
        return {conf['parameter']: conf['value'] for conf in _db['Configuration'].find(experiment_id=self.experiment_id)}

    @description.setter
    def description(self, value):
        with _db as db:
            db['Experiment'].update({'id':self.experiment_id, 'description':value}, ['id'])

    @property
    def labels(self):
        if not hasattr(self,'_labels'):
            self._labels = list(
                {label for label in self.actual + self.predicted})
        return self._labels

    @property
    def precision(self):
        act = [self.labels.index(x) for x in self.actual]
        pred = [self.labels.index(x) for x in self.predicted]
        return measures.precision(act, pred)

    @property
    def recall(self):
        act = [self.labels.index(x) for x in self.actual]
        pred = [self.labels.index(x) for x in self.predicted]
        return measures.recall(act, pred)

    @property
    def f1_score(self):
        act = [self.labels.index(x) for x in self.actual]
        pred = [self.labels.index(x) for x in self.predicted]
        return measures.f1_score(act, pred)

    @property
    def num_correct(self):
        return len([x for x, y in zip(self.actual, self.predicted) if x == y])

    @property
    def accuracy(self):
        return self.num_correct / len(self.actual)

    def experiment_report(self, accuracy=False, precision=True, recall=True, f1_score=True,):
        # They are split up to keep all warnings to before the printout
        if accuracy:
            acc = self.accuracy
        if precision:
            prec = self.precision
        if recall:
            rec = self.recall
        if f1_score:
            f1 = self.f1_score

        if accuracy:
            print("Accuracy: {}".format(acc))
        if precision:
            print("Precision: {}".format(prec))
        if recall:
            print("Recall: {}".format(rec))
        if f1_score:
            print("F-score: {}".format(f1))

    def __repr__(self):
        timest = self.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        return "<Experiment {} of project {}. Timestamp: {}>".format(self.experiment_id, self.project_name, timest)

    def __str__(self):
        timest = self.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        return "Experiment: {} of project {}. Timestamp: {}".format(self.experiment_id, self.project_name, timest)
