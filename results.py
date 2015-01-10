import time
import dataset
from datetime import datetime

_db = dataset.connect('mysql+pymysql://root@localhost/results')

class Project(object):
    """
    Defines and creates a project and its configuration.
    """

    def __init__(self, name, test_data, base_configuration, description=None):
        assert isinstance(test_data, dict)
        assert isinstance(base_configuration, dict)
        with _db as db:
            project = db['Project']
            config = db['Configuration']
            data = db['Data']
            self.project_id = project.insert({'name': name, 'description': description})
            
            config.insert_many([{'parameter': cparameter, 'value': cvalue, 'project_id': self.project_id}
                                for cparameter, cvalue in base_configuration.items()])
            
            data.insert_many([{'instance': instance, 'answer': answer, 'project_id': self.project_id} 
                              for instance, answer in test_data.items()])                


    def new_experiment(self, predicted, configuration, description=None):
        with _db as db:
            experiment = db['Experiment']
            experiment_results = db['ExperimentResults']
            experiment_id = experiment.insert({'project_id': self.project_id, 'description': description})
            for instance, pred in predicted.items():
                instance_id = db['Data'].find_one(instance=instance, id=self.project_id)
                print(instance_id)
                if not instance_id:
                    raise KeyError("Predicted instance {} is not available in the project's test data".format(instance))
                experiment_results.insert({'predicted': pred, 'instance_id': instance_id, 'timestamp': datetime.now()})

