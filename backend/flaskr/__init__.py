import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
from sqlalchemy.exc import SQLAlchemyError
from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def paginate_questions(request, selection):
      page = request.args.get('page', 1, type=int)
      start = (page - 1) * QUESTIONS_PER_PAGE
      end = start + QUESTIONS_PER_PAGE

      questions = [question.format() for question in selection]
      current_questions = questions[start:end]

      return current_questions


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
  def retrieve_categories():
    categories = Category.query.all()
    if len(categories) == 0:
      abort(404)
    listCategory ={}
    for category in categories:
      listCategory[category.id] =category.type
      pass
   # categoryFormate = [category.format() for category in categories]
    return jsonify({
      'success': True,
      'categories': listCategory,
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
    selection = Question.query.order_by(Question.id).all()
    total_questions = len(selection)
    questions = paginate_questions(request, selection)
     
    if (len(questions) == 0):
      abort(404)

    categories = Category.query.all()
    listCategories = {}
    for c in categories: 
       listCategories[c.id] = c.type

      
    return jsonify({
      'success': True,
      'questions':  questions,
      'total_questions': total_questions,
      'categories': listCategories ,#[category.format() for category in categories],
      #'current_category': current_category
    })

  '''
  @TODO:
  Create an endpoint to DELETE question using a question ID.

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page.
  '''
  @app.route('/questions/<int:id>', methods=['DELETE'])
  def delete_question(id):
    try:
      
      question = Question.query.filter(
          Question.id == id).one_or_none()
      if(question is None):
        abort(404)
      question.delete()
      selection = Question.query.all()
      current_question = paginate_questions(request, selection)
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
     
      question = Question(
        question=new_question,
        answer=new_answer,
        category=new_category,
        difficulty=new_difficulty,
      )
       
      question.insert()
      
      selection = Question.query.all()
      current_questions = paginate_questions(request, selection)

      return jsonify({
            'success': True,
            'created': question.id,
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
     # if search term is present
    if (body.get('searchTerm')):
      search_term = body.get('searchTerm')
      # query the database using search term
      selection = Question.query.filter(Question.question.ilike(f'%{search_term}%')).all()
      # 404 if no results found
      if (len(selection) == 0):
          abort(404)
       # paginate the results
      paginated = paginate_questions(request, selection)
      return jsonify({
        'success': True,
        'questions': paginated,
        'total_questions': len(Question.query.all())
      })  # return results
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
  def get_questions_by_category(id):

    category = Category.query.get(id) 
    print( category)
    
    if category is None:
      abort(400)

    selection = Question.query.filter_by(category=str(category.id)).all()
    # paginate the selection
    paginated_question = paginate_questions(request, selection)
    # return the results
    return jsonify({
            'success': True,
            'questions': paginated_question,
            'total_questions': len(Question.query.all()),
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
        getCategory =  Category.query.get(quiz_category['id'])
        questions = Question.query.filter_by(category=str(getCategory.id)).all()
        print(questions)
        
     
    def check_if_question_is_display(question):
      displayed_question = False
      for q in previous_questions:
        if (q == question.id):
          displayed_question = True
          return displayed_question

    
    get_random_question = questions[random.randrange(0, len(questions), 1)]
     
    while (check_if_question_is_display(get_random_question)):
      question =questions[random.randrange(0, len(questions), 1)]
       
      if (len(questions) ==len(previous_questions)  ):
        return jsonify({
          'success': True
        })

    
    return jsonify({
      'success': True,
      'question': get_random_question.format()
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

    
