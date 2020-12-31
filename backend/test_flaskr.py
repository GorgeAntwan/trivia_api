import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgresql://{}/{}".format('Gorge@localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

         # sample question for use in tests
        self.new_question = {
            'question': 'Which four states make up the 4 Corners region of the US?',
            'answer': 'Colorado, New Mexico, Arizona, Utah',
            'difficulty': 3,
            'category': '3'
        }

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_get_paginated_questions(self):
        """Tests question pagination success"""

        # get response and load data
        response = self.client().get('/questions')
        data = json.loads(response.data)
        #to check status code and message
        self.assertEqual(response.status_code,200)
        self.assertEqual(data['success'],True)
        
       # check that total_questions and questions return data
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))

    def test_404_request_beyond_valid_page(self):
        """Tests question pagination failure 404"""
        response = self.client().get('/questions?page=100')
        data = json.loads(response.data)
        # check status code and message
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Not Found')

    def test_delete_question(self):
        """Tests question deletion success"""

        # create a new question to be deleted
        question = Question(question=self.new_question['question'], answer=self.new_question['answer'],
                            category=self.new_question['category'], difficulty=self.new_question['difficulty'])
        question.insert()

        # get the id of the new question
        q_id = question.id

        # get number of questions before delete
        questions_before = Question.query.all()

        # delete the question and store response
        response = self.client().delete('/questions/{}'.format(q_id))
        data = json.loads(response.data)

        # get number of questions after delete
        questions_after = Question.query.all()

        # see if the question has been deleted
        question = Question.query.filter(Question.id == q_id).one_or_none()

        # check status code and success message
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)

        # check if question id matches deleted id
        self.assertEqual(data['deleted'], q_id)

        # check if one less question after delete
        self.assertTrue(len(questions_before) - len(questions_after) == 1)

        # check if question equals None after delete
        self.assertEqual(question, None)
    def test_create_new_question(self):
        """Tests question creation success"""

        #get question before create new question
        questions_before =  Question.query.all()
        response = self.client().post('/questions',json = self.new_question)
        data =json.loads(response.data)

        #get number of question after create
        questions_after=Question.query.all()

        #get question after create 
        question =Question.query.filter_by(id=data['created']).one_or_none()

        # check status code and success message
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)

        # check if one more question after post
        self.assertTrue(len(questions_after) - len(questions_before) == 1)

        # check that question is not None
        self.assertIsNotNone(question)
    def test_422_if_question_creation_fails(self):
       """Tests question creation failure 422"""
       #get questions before create
       questions_before=Question.query.all()
       
       #create new question
       response = self.client().post('/questions',json={})
       data = json.loads(response.data)
       questions_after = Question.query.all()

       # check status code and success message
       self.assertEqual(response.status_code, 422)
       self.assertEqual(data['success'], False)

       # check if questions_after and questions_before are equal
       self.assertTrue(len(questions_after) == len(questions_before))
    def test_search_questions(self):
        """Tests search questions success"""

        response = self.client().post('/searchQuestions',json={'searchTerm':'region'})
        data =json.loads(response.data)

        # check response status code and message
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_404_if_search_questions_fails(self):
        """Tests search questions failure 404"""
        # send post request with search term that should fail
        response = self.client().post('/searchQuestions',json={'searchTerm': 'qqqqqq'})
        data = json.loads(response.data)

        # check response status code and message
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
    
    def test_get_questions_by_category(self):
        """Tests getting questions by category success"""

        response = self.client().get('/categories/2/questions')
        data = json.loads(response.data)

        self.assertEqual(response.status_code,200)
        self.assertEqual(data['success'],True)

        # check that questions are returned 
        self.assertNotEqual(len(data['questions']),0)
        
        #to check the category is correct
        self.assertEqual(data['current_category'], 'Art')

    def test_400_if_questions_by_category_fails(self):
        """Tests getting questions by category failure 400"""

        response = self.client().get('/categories/100/questions')
        data = json.loads(response.data)

        self.assertEqual(response.status_code,400)
        self.assertEqual(data['success'],False)

        self.assertEqual(data['message'], 'bad request')

    def test_play_quiz_game(self):
        """Tests playing quiz game success"""
        response = self.client().post('/quizzes', json={'previous_questions': [2, 6],
                   'quiz_category': {'type': 'Science', 'id': '1'}})
        data = json.loads(response.data)
        
        #check response status and message
        self.assertEqual(response.status_code,200)
        self.assertEqual(data['success'],True)

        # check that a question is returned
        self.assertTrue(data['question'])

        # check that question returned is not on previous question list
        self.assertNotEqual(data['question']['id'], 2)
        self.assertNotEqual(data['question']['id'], 6)

    def test_play_quiz_fails(self):
        """Tests playing quiz game failure 400"""

        # send post request without json data
        response = self.client().post('/quizzes', json={})

        # load response data
        data = json.loads(response.data)

        # check response status code and message
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'bad request')

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()