import unittest2 as unittest
import dataset
import expy
import expy.project
import pymysql

class ProjectTest(unittest.TestCase):

    def setUp(self):
        self.cursor = pymysql.connect(user='root').cursor()
        self.cursor.execute("create database if not exists testExpy; use testExpy; " + expy.sql)
        self.db = dataset.connect('mysql+pymysql://root@localhost/testExpy')
        expy.project._db = self.db
        self.name = "test name"
        self.description = "just a test"
        self.test_data = {'here is a test instance': 'answers answer',
                          'here is another one': 'new answer'}

        self.project = expy.Project(project_name=self.name, description=self.description, test_data=self.test_data)

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
        self.project.delete_project()
        self.cursor.execute("drop database if exists testExpy")

    def testProjectCreation(self):
        project = self.project
        self.assertEqual(self.db['Project'].find_one(name=project.project_name)['name'], project.project_name)
        self.assertEqual(self.db['Project'].find_one(name=project.project_name)['description'], project.description)
        dat = {x['instance']: x['answer'] for x in self.db['TestData'].find(project_name=project.project_name)}
        self.assertEqual(dat, self.test_data)

    def testNewExperiment(self):
        pred = self.db.query("select instance, predicted from ExperimentResult join TestData on TestData.id = ExperimentResult.instance_id where ExperimentResult.experiment_id = {}".format(self.experiment.experiment_id))

        self.assertEqual(self.ex_predicted, {x['instance']: x['predicted'] for x in pred})
        
        t = [x['tag'] for x in self.db['Tag'].find(experiment_id=self.experiment.experiment_id)]
        self.assertEqual(sorted(t), sorted(self.ex_tags))

    def testExperimentRetrieval(self):
        exp = self.project.experiments[0]
        self.assertEqual(exp.experiment_id, self.experiment.experiment_id)

    def testTestData(self):
        test_data = self.project.test_data
        self.assertEqual(test_data, self.test_data)

    def testAnswers(self):
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
        #self.project.delete_project()
        #self.project = None
        pass


def main():
    unittest.main()

if __name__ == '__main__':
    main()
