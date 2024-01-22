

import os
from flask import Flask, flash, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

# Utils
def pagination(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]
    return current_questions

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  '''
  Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

  @app.route('/')
  def hello():
        return jsonify({
          'success': True,
          'message': 'Home page'
        }), 200
  
  '''
  Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization, true')
        response.headers.add('Access-Control-Allow-Methods', 'GET, PUT, POST, DELETE, OPTIONS')
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response

  '''

  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/categories', methods=['GET'])
  def get_categories():

        categories = Category.query.all()
        formatted_categories = {}
        total_categories = 0

        for category in categories:
            formatted_categories[category.id] = category.type
            total_categories += 1

        return jsonify({
          'success': True,
          'categories': formatted_categories,
          'total_categories': len(categories)
        }), 200


  '''

  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''

  @app.route('/questions', methods=['GET'])
  def get_questions():
        selection = Question.query.order_by(Question.category, Question.id).all()
        current_questions = pagination(request, selection)

        categories = Category.query.all()
        formatted_categories = {
          category.id: category.type for category in categories
        }

        if len(current_questions) == 0:
          abort(404)

        return jsonify({
          'success': True,
          'questions': current_questions,
          'total_questions': len(Question.query.all()),
          'categories': formatted_categories
        }), 200
  '''

  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/questions/<int:question_id>', methods=["DELETE"])
  def delete_question(question_id):
        try:
            question = Question.query.filter(Question.id == question_id).one_or_none()
            
            if question is None:
              abort(404)
            
            question.delete()

            selection = Question.query.order_by(Question.id).all()
            current_questions = pagination(request, selection)

            return jsonify({
                'success': True,
                'deleted': question.id,
                'question': current_questions,
                'total_questions': len(Question.query.all())
            })

        except:
            abort(422)


  '''

  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''

  @app.route('/questions', methods=["POST"])
  def create_question():
        body = request.get_json()
        question = body.get('question', None)
        answer = body.get('answer', None)
        difficulty = body.get('difficulty', None)
        category = body.get('category', None)

        try:
            question = Question(question=question, answer=answer, difficulty=difficulty, category=category)
            question.insert()

            selection = Question.query.order_by(Question.difficulty).all()
            current_questions = pagination(request, selection)
            
            return jsonify({
                "success": True,
                "created": question.id,
                "questions": current_questions,
                "total_questions": len(Question.query.all())
            })
        except:
            abort(500)

  '''

  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
  @app.route('/search', methods=['POST'])
  def search_questions():

    try:
        data = request.get_json()
        search_term = data.get('searchTerm')
        result = Question.query.filter(Question.question.ilike(f'%{search_term}%')).all()

        if len(result) == 0:
            abort(404)

        formatted_questions = [question.format() for question in result]
        current_questions = pagination(request, result)
        category = []

        for question in current_questions:
            current_categories = Category.query.filter(Category.id == question.get("category")).all()
            for current_category in current_categories:
                category.append(current_category.format())

        return jsonify({
          'success': True,
          'questions': formatted_questions,
          'total_questions': len(formatted_questions),
          'current_category': category
        }), 200

    except Exception as e:
        print('\n'+'Error searching: ', e)
        abort(404)

  '''

  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/categories/<int:category_id>/questions', methods=["GET"])
  def get_questions_by_category(category_id):

        selection = Question.query.filter(Question.category == category_id).all()
        current_questions = pagination(request, selection)
        total_questions = len(Question.query.all())
        category = Category.query.filter(Category.id == category_id).one_or_none()

        if category is None:
            abort(404)

        return jsonify({
            "questions": current_questions,
            "total_questions": total_questions,
            "current_category": category.type
        })

  '''
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''

  @app.route("/quizzes", methods=["POST"])
  def quiz():
    try:
      data = request.json
      previous_questions = data["previous_questions"]
      quiz_category_id = data["quiz_category"]["id"]

    except:
      abort(400)

    category = Category.query.filter_by(id=quiz_category_id).first()

    if category:
      questions = Question.query.filter_by(category=category.id).all()
    else:
      questions = Question.query.all()

    i = 0
    while i < len(questions):
      if questions[i].id in previous_questions:
        del questions[i]
        i-=1
      i+=1

    if len(questions) == 0:
      random_question = ""
    else:
      random_question = questions[random.randint(0, len(questions)-1)].format()
    return jsonify({
      "success": True,
      "question": random_question
    })

  ''' 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  @app.errorhandler(400)
  def bad_req(error):
        return jsonify({
            "success": False,
            "message": "Bad request",
            "error": 400
        }), 400

  @app.errorhandler(404)
  def not_fond(error):
      return jsonify({
          "success": False,
          "message": "Resource not found",
          "error": 404}), 404

  @app.errorhandler(422)
  def unprocessable(error):
      return jsonify({
        "success": False,
        "error": 422,
        "message": "Unprocessable"
        }), 422

  @app.errorhandler(500)
  def server_error(error):
      return jsonify({
          "success": False,
          "message": "Internal server error",
          "error": 500
      }), 500

  return app
