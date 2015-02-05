import unittest2 as unittest
import dataset
import expy
import expy.project
import pymysql

class ProjectTest(unittest.TestCase):

    def setUp(self):
        cursor = pymysql.connect(user='root').cursor()
        cursor.execute("create database if not exists testExpy")
        self.db = dataset.connect('mysql+pymysql://root@localhost/testExpy')
        expy.project._db = self.db
        self.name = "test instance"
        self.description = "just a test"
        self.test_data = {'here is a test instance': 'answers answer',
                          'here is another one': 'new answer'}

        self.project = expy.Project(name=self.name, description=self.description, test_data=self.test_data)

        self.ex_description = "a test experiment"
        self.ex_tags = ['a tag', 'another tag']
        self.ex_configuration = {'language': 'english', 'dimensionality': 2000}
        self.ex_predicted = {'here is a test instance': 'answers answer',
                     'here is another one': 'new answer'}
        experiment = self.project.new_experiment(description=self.ex_description,
                                                 configuration=self.ex_configuration,
                                                 predicted=self.ex_predicted,
                                                 tags=self.ex_tags)
        self.experiment = experiment

    def tearDown(self):
        if self.project:
            self.project.delete_project()

    def testProjectCreation(self):
        project = self.project
        self.assertEqual(self.db['Project'].find_one(id=project.project_id)['name'], project.name)
        self.assertEqual(self.db['Project'].find_one(id=project.project_id)['description'], project.description)
        dat = {x['instance']: x['answer'] for x in self.db['Data'].find(project_id=project.project_id)}
        self.assertEqual(dat, self.test_data)

    def testNewExperiment(self):
        pred = self.db.query("select instance, predicted from ExperimentResult join Data on Data.id = ExperimentResult.instance_id where ExperimentResult.experiment_id = {}".format(self.experiment.experiment_id))

        self.assertEqual(self.ex_predicted, {x['instance']: x['predicted'] for x in pred})
        
        t = [x['tag'] for x in self.db['Tag'].find(experiment_id=self.experiment.experiment_id)]
        self.assertEqual(sorted(t), sorted(self.ex_tags))

    def testExperimentRetrieval(self):
        exp = self.project.experiments[0]
        self.assertEqual(exp.experiment_id, self.experiment.experiment_id)

    def testTestData(self):
        test_data = self.project.test_data
        self.assertEqual(test_data, self.test_data)

    def testSnswers(self):
        answers = self.project.answers

    def testPredicted(self):
        pred = self.experiment.predicted

    def testExperimentDeletion(self):
        description = "a small experiment"
        tags = ['for deletion', 'another tag']
        configuration = {'language': 'english', 'dimensionality': 2000}
        predicted = {'here is a test instance': 'answers answer',
                     'here is another one': 'not the same'}

        experiment = self.project.new_experiment(description=description,
                                                 configuration=configuration,
                                                 predicted=predicted,
                                                 tags=tags)
        expid = experiment.experiment_id
        experiment.delete_experiment()
        self.assertEqual(len(self.project.experiments), 1)
        self.assertEqual(len(list(self.db['Experiment'].find(id=expid))), 0)
        self.assertEqual(len(list(self.db['ExperimentResult'].find(experiment_id=expid))), 0)

        self.experiment = None

    def testProjectDeletion(self):
        self.project.delete_project()
        self.project = None


def main():
    unittest.main()

if __name__ == '__main__':
    main()
