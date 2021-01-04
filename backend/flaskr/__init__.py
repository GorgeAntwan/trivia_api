import os
from sys import dont_write_bytecode
from typing import final
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.sql.elements import Null
from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def paginate_questions(request, selection):
      page = request.args.get('page', 1, type=int)
      start = (page - 1) * QUESTIONS_PER_PAGE
      end = start + QUESTIONS_PER_PAGE

      questions = [question.format() for question in selection]
      current_questions = questions[start:end]

      return current_questions

def check_if_question_is_display(question,previous_questions):
       
      displayed_question = False
      for q in previous_questions:
        
        if (q == question.id):
          displayed_question = True

      return displayed_question

def get_final_random_question(questions,previous_questions):

      total_question = len(questions)
      total_previous_questions=len(previous_questions)
      random_index= random.randrange(0, total_question, 1)
      get_random_question = questions[random_index]
      
      while ( check_if_question_is_display(get_random_question,previous_questions)):
       
       random_index= random.randrange(0, total_question, 1)
       get_random_question = questions[random_index]
       
       if (total_question ==total_previous_questions):
          
          return ""

      final_display_question = get_random_question.format()
    
      return final_display_question
      
def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)

  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  setup_db(app)
  #CORS(app)
  CORS(app, resources={'/': {'origins': '*'}})
  # CORS Headers
  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers',
                         'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods',
                         'GET,PUT,POST,DELETE,OPTIONS')
    return response
  '''
  @TODO:
  Create an endpoint to handle GET requests
  for all available categories.
  '''
  @app.route('/categories')
  def get_all_category():
    categories = Category.query.all()
    if len(categories) == 0:
      abort(404)
    
    return jsonify({
      'success': True,
      'categories': [  category.format()   for category in categories],
      'total_categories': len(Category.query.all())
    })

  '''
  @TODO:
  Create an endpoint to handle GET requests for questions,
  including pagination (every 10 questions).
  This endpoint should return a list of questions,
  number of total questions, current category, categories.

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions.
  '''
  @app.route('/questions')
  def get_questions():

    all_questions = Question.query.order_by(Question.id).all()
    sub_questions = paginate_questions(request, all_questions)
     
    if (len(sub_questions) == 0):
      abort(404)

    categories = Category.query.all()
    
    return jsonify({
      'success': True,
      'questions':  sub_questions,
      'total_questions':len(all_questions) ,
      'categories':[category.format() for category in categories],  
    })

  '''
  @TODO:
  Create an endpoint to DELETE question using a question ID.

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page.
  '''
  @app.route('/questions/<int:id>', methods=['DELETE'])
  def delete_question_by_id(id):
    try:
      
      get_delete_question = Question.query.get(id)
      if(get_delete_question is None):
         
        abort(404)
      get_delete_question.delete()
      get_all_question_after_delete = Question.query.all()
      current_question = paginate_questions(request, get_all_question_after_delete)
      return jsonify({
          'success': True,
          'deleted': id,
          'questions': current_question,
          'total_questions': len(Question.query.all())
        })
    except:
      abort(422)

  '''
  @TODO:
  Create an endpoint to POST a new question,
  which will require the question and answer text,
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab,
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.
  '''
  @app.route('/questions',  methods=["POST"])
  def create_question():
    body = request.get_json()
    print(body)
    new_question = body.get('question', None)
    new_answer = body.get('answer', None)
    new_category = body.get('category', None)
    new_difficulty = body.get('difficulty', None)
    
    if (new_question is None) or (new_answer is None) or (new_difficulty is None) or (new_category is None):
      abort(422)
    try:
     
      new_question = Question(
        question=new_question,
        answer=new_answer,
        category=new_category,
        difficulty=new_difficulty,
      )
       
      new_question.insert()
      #all question after creat new question
      all_questions_after = Question.query.all()
      current_questions = paginate_questions(request, all_questions_after)

      return jsonify({
            'success': True,
            'created': new_question.id,
            'questions': current_questions,
            'total_questions': len(Question.query.all())
    })
    except SQLAlchemyError as e :
      print(e)
      abort(422)
  '''
  @TODO:
  Create a POST endpoint to get questions based on a search term.
  It should return any questions for whom the search term
  is a substring of the question.

  TEST: Search by any phrase. The questions list will update to include
  only question that include that string within their question.
  Try using the word "title" to start.
  '''
  @app.route('/searchQuestions', methods=["POST"])
  def search_question():

    body = request.get_json()
     
    if (body.get('searchTerm')):
      search_term = body.get('searchTerm')
      
      selection_search= Question.query.filter(Question.question.ilike(f'%{search_term}%')).all()
     
      if (len(selection_search) == 0):
          abort(404)
     
      paginated = paginate_questions(request, selection_search)
      return jsonify({
        'success': True,
        'questions': paginated,
        'total_questions': len(Question.query.all())
      })   
    else:
      abort(400)       
  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/categories/<int:id>/questions',methods=['GET'])
  def get_questions_by_category_id(id):

    category = Category.query.get(id)  
    if category is None:
      abort(400)

    all_Question =[]
    for q in Question.query.all() :
     if q.category ==str(category.id):
      all_Question.append(q)

    questions = paginate_questions(request, all_Question)
    if (len(questions) == 0):
      abort(404)

    total_questions = len(Question.query.all())

    return jsonify({
            'success': True,
            'questions':questions, 
            'total_questions': total_questions,
            'current_category': category.type
    })


  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
  @app.route('/quizzes', methods=['POST'])
  def get_random_quiz_question_play():

    body =request.get_json()
    previous_questions = body.get('previous_questions')
    quiz_category = body.get('quiz_category')
  
    if ((previous_questions is None) or ( quiz_category is None)):
         abort(400)
   
    if (quiz_category['id'] == 0):
        questions = Question.query.all()
       
        
    else:
        category_id = quiz_category['id']
        getCategory =  Category.query.get(category_id)
        if getCategory is None:
         abort(404)
        questions = Question.query.filter_by(category=str(getCategory.id)).all()
    
  

    final_question = get_final_random_question(questions,previous_questions)
    if(final_question==""):
       
      return jsonify({
            'success': True
          })
    else:
       
      return jsonify({
        'success': True,
        'question': final_question
      })
  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      "success":False,
      "error":404,
      "message":"Not Found"
    }),404
  @app.errorhandler(422)
  def unprocessable(error):
    return jsonify({
      "success":False,
      "error":422,
      "message":"unprocessable"
    }),422
  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({
      "success":False,
      "error":400,
      "message":"bad request"
    }),400
  @app.errorhandler(405)
  def method_not_allowed(error):
    return jsonify({
      "success":False,
      "error":405,
      "message":"method not allowed"
    }),405
  
  return app

    
