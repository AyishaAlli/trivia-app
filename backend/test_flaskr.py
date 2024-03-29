import os
import unittest
import json

from flask import app, jsonify
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia"
        self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

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
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_add_question(self):
        new_question = {
            'question': '',
            'answer': 'Manal',
            'difficulty': 1,
            'category': 1
        }
        res = self.client().post('/questions', json=new_question)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
    
    def test_get_questions(self):
        res = self.client().get("/questions")
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["total_questions"])
        self.assertTrue(len(data["questions"]))
        self.assertTrue(len(data["categories"]))

    def test_get_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])
        self.assertTrue(data['total_categories'])

    def test_delete_questions(self):
        res = self.client().delete('questions/4')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], 11)
    
    def search_question(self):
        res = self.client().post('questions/search', json={"searchTerm": "the"})
        data = json.loads(res.data)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])

    def test_400_get_quiz_without_body(self):
        res = self.client().post("/quizzes")
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Bad request")

    def test_404_invalid_page_numbers(self):
        res = self.client().get('/questions?page=200000')
        data = json.loads(res.data)
        self.assertEqual(data['error'], 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data["message"], "Resource not found")

    def test_422_cannot_create_question(self):
        new_question = { 
        'question': 'What is the day after Tuesday?',
        'category': '1',
        'answer':'',
        'difficulty': 1,
        }

        res = self.client().post('/questions', json=new_question)
        data = json.loads(res.data)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['error'], 422)
        self.assertEqual(data['message'], "Unprocessable")

        


    


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()