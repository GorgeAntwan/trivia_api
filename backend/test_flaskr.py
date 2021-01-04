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
        self.responseDatabase_name = "trivia_test"
        self.responseDatabase_path = "postgresql://{}/{}".format('Gorge@localhost:5432', self.responseDatabase_name)
        setup_db(self.app, self.responseDatabase_path)

        self.new_question = {
            'question': 'Whose autobiography is entitled I Know Why the Caged Bird Sings?',
            'answer': 'Maya Angelou',
            'difficulty': 4,
            'category': '2'
        }
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
    def test_get_paginated_all_questions(self):
        """Tests question pagination success when get all question"""

        response = self.client().get('/questions')
        responseData = json.loads(response.data)
        self.assertEqual(responseData['success'],True)
        self.assertTrue(len(responseData['questions']))
        self.assertEqual(response.status_code,200)
        self.assertTrue(responseData['total_questions'])


    def test_404_request_beyond_valid_page_get_all_question(self):
        """Tests question pagination failure 404 when get all question"""
        response = self.client().get('/questions?page=100')
        responseData = json.loads(response.data)
        self.assertEqual(responseData['success'], False)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(responseData['message'], 'Not Found')

    def test_delete_question_from_all_question(self):
        """Tests question deletion success from all question"""

        question=self.new_question['question']
        answer=self.new_question['answer']
        category=self.new_question['category']
        difficulty=self.new_question['difficulty']
        new_question = Question(question=question, answer=answer,category=category, difficulty=difficulty)
        new_question.insert()
        questions_before_delete = Question.query.all()
        response = self.client().delete('/questions/{}'.format(new_question.id))
        responseData = json.loads(response.data)
        questions_after_delete = Question.query.all()
        question = Question.query.filter(Question.id == new_question.id).one_or_none()
        print(question)
        self.assertEqual(responseData['success'], True)
        self.assertIsNone(question)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(questions_before_delete) - len(questions_after_delete) == 1)
        self.assertEqual(responseData['deleted'], new_question.id)
        

    def test_create_new_question(self):
        """Tests new question creation success"""

        questions_before_create_new_question =  Question.query.all()
        response = self.client().post('/questions',json = self.new_question)
        responseData =json.loads(response.data)
        questions_after_create_new_question=Question.query.all()
        question =Question.query.filter_by(id=responseData['created']).one_or_none()       
        self.assertEqual(responseData['success'], True)
        self.assertTrue(len(questions_after_create_new_question) - len(questions_before_create_new_question) == 1)
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(question)


    def test_422_if_question_creation_fails_add(self):
       """Tests question creation failure 422"""
      
       questions_before_create=Question.query.all()
       response = self.client().post('/questions',json={})
       responseData = json.loads(response.data)
       questions_after_create = Question.query.all()  
       self.assertEqual(responseData['success'], False)
       self.assertTrue(len(questions_after_create) == len(questions_before_create))
       self.assertEqual(response.status_code, 422)


    def test_search_questions(self):
        """Tests search questions success"""

        response = self.client().post('/searchQuestions',json={'searchTerm':'region'})
        responseData =json.loads(response.data)
        self.assertEqual(responseData['success'], True)
        self.assertEqual(response.status_code, 200)

    def test_404_if_search_questions_fails(self):
        """Tests search questions failure 404"""
        
        response = self.client().post('/searchQuestions',json={'searchTerm': 'qqqqqq'})
        responseData = json.loads(response.data)
        self.assertEqual(responseData['success'], False)
        self.assertEqual(response.status_code, 404)
    
    def test_get_questions_by_category(self):
        """Tests getting questions by category success"""

        response = self.client().get('/categories/2/questions')
        responseData = json.loads(response.data)
        self.assertEqual(response.status_code,200)
        self.assertNotEqual(len(responseData['questions']),0)
        self.assertEqual(responseData['success'],True)
        self.assertEqual(responseData['current_category'], 'Art')


    def test_400_if_questions_by_category_fails(self):
        """Tests getting questions by category failure 400"""

        response = self.client().get('/categories/100/questions')
        responseData = json.loads(response.data)
        self.assertEqual(responseData['success'],False)
        self.assertEqual(responseData['message'], 'bad request')
        self.assertEqual(response.status_code,400)


    def test_play_quiz_game_correct(self):
        """Tests playing quiz game success"""

        response = self.client().post('/quizzes', json={'previous_questions': [2, 6],
                   'quiz_category': {'type': 'Science', 'id': '1'}})
        responseData = json.loads(response.data)
        self.assertEqual(response.status_code,200)
        self.assertTrue(responseData['question'])
        self.assertNotEqual(responseData['question']['id'], 2)
        self.assertNotEqual(responseData['question']['id'], 6)
        self.assertEqual(responseData['success'],True)

    def test_play_quiz_fails_not_correct(self):
        """Tests playing quiz game failure 400"""

        response = self.client().post('/quizzes', json={})
        responseData = json.loads(response.data)
        self.assertEqual(responseData['success'], False)
        self.assertEqual(responseData['message'], 'bad request')
        self.assertEqual(response.status_code, 400)


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()