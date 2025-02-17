from flask import request, jsonify, g
from flask_cors import cross_origin
import json

def load(app):
  # Endpoint: GET /words with pagination (50 words per page)
  @app.route('/words', methods=['GET'])
  @cross_origin()
  def get_words():
    try:
      cursor = app.db.cursor()

      # Get the current page number from query parameters (default is 1)
      page = int(request.args.get('page', 1))
      # Ensure page number is positive
      page = max(1, page)
      words_per_page = 50
      offset = (page - 1) * words_per_page

      # Get sorting parameters from the query string
      sort_by = request.args.get('sort_by', 'kanji')  # Default to sorting by 'kanji'
      order = request.args.get('order', 'asc')  # Default to ascending order

      # Validate sort_by and order
      valid_columns = ['kanji', 'romaji', 'english', 'correct_count', 'wrong_count']
      if sort_by not in valid_columns:
        sort_by = 'kanji'
      if order not in ['asc', 'desc']:
        order = 'asc'

      # Query to fetch words with sorting
      cursor.execute(f'''
        SELECT w.id, w.kanji, w.romaji, w.english, 
            COALESCE(r.correct_count, 0) AS correct_count,
            COALESCE(r.wrong_count, 0) AS wrong_count
        FROM words w
        LEFT JOIN word_reviews r ON w.id = r.word_id
        ORDER BY {sort_by} {order}
        LIMIT ? OFFSET ?
      ''', (words_per_page, offset))

      words = cursor.fetchall()

      # Query the total number of words
      cursor.execute('SELECT COUNT(*) FROM words')
      total_words = cursor.fetchone()[0]
      total_pages = (total_words + words_per_page - 1) // words_per_page

      # Format the response
      words_data = []
      for word in words:
        words_data.append({
          "id": word["id"],
          "kanji": word["kanji"],
          "romaji": word["romaji"],
          "english": word["english"],
          "correct_count": word["correct_count"],
          "wrong_count": word["wrong_count"]
        })

      return jsonify({
        "words": words_data,
        "total_pages": total_pages,
        "current_page": page,
        "total_words": total_words
      })

    except Exception as e:
      return jsonify({"error": str(e)}), 500
    finally:
      app.db.close()

  # Endpoint: GET /words/:id to get a single word with its details
  @app.route('/words/<int:word_id>', methods=['GET'])
  @cross_origin()
  def get_word(word_id):
    try:
      cursor = app.db.cursor()
      
      # Query to fetch the word and its details
      cursor.execute('''
        SELECT w.id, w.kanji, w.romaji, w.english,
               COALESCE(r.correct_count, 0) AS correct_count,
               COALESCE(r.wrong_count, 0) AS wrong_count,
               GROUP_CONCAT(DISTINCT g.id || '::' || g.name) as groups
        FROM words w
        LEFT JOIN word_reviews r ON w.id = r.word_id
        LEFT JOIN word_groups wg ON w.id = wg.word_id
        LEFT JOIN groups g ON wg.group_id = g.id
        WHERE w.id = ?
        GROUP BY w.id
      ''', (word_id,))
      
      word = cursor.fetchone()
      
      if not word:
        return jsonify({"error": "Word not found"}), 404
      
      # Parse the groups string into a list of group objects
      groups = []
      if word["groups"]:
        for group_str in word["groups"].split(','):
          group_id, group_name = group_str.split('::')
          groups.append({
            "id": int(group_id),
            "name": group_name
          })
      
      return jsonify({
        "word": {
          "id": word["id"],
          "kanji": word["kanji"],
          "romaji": word["romaji"],
          "english": word["english"],
          "correct_count": word["correct_count"],
          "wrong_count": word["wrong_count"],
          "groups": groups
        }
      })
      
    except Exception as e:
      return jsonify({"error": str(e)}), 500

  # Endpoint: POST /words to add a new word
  @app.route('/words', methods=['POST'])
  @cross_origin()
  def create_word():
    try:
      data = request.get_json()
      kanji = data.get('kanji')
      romaji = data.get('romaji')
      english = data.get('english')
      parts = data.get('parts')

      if not kanji or not romaji or not english or not parts:
        return jsonify({"error": "All fields are required"}), 400

      cursor = app.db.cursor()
      cursor.execute('INSERT INTO words (kanji, romaji, english, parts) VALUES (?, ?, ?, ?)', (kanji, romaji, english, json.dumps(parts)))
      app.db.commit()
      return jsonify({"message": "Word added successfully"})
    except Exception as e:
      return jsonify({"error": str(e)}), 500

  # Endpoint: PUT /words/:id to update a word
  @app.route('/words/<int:word_id>', methods=['PUT'])
  @cross_origin()
  def update_word(word_id):
    try:
      data = request.get_json()
      kanji = data.get('kanji')
      romaji = data.get('romaji')
      english = data.get('english')
      parts = data.get('parts')

      if not kanji or not romaji or not english or not parts:
        return jsonify({"error": "All fields are required"}), 400

      cursor = app.db.cursor()
      cursor.execute('UPDATE words SET kanji = ?, romaji = ?, english = ?, parts = ? WHERE id = ?', (kanji, romaji, english, json.dumps(parts), word_id))
      app.db.commit()
      return jsonify({"message": "Word updated successfully"})
    except Exception as e:
      return jsonify({"error": str(e)}), 500

  # Endpoint: DELETE /words/:id to delete a word
  @app.route('/words/<int:word_id>', methods=['DELETE'])
  @cross_origin()
  def delete_word(word_id):
    try:
      cursor = app.db.cursor()
      cursor.execute('DELETE FROM words WHERE id = ?', (word_id,))
      app.db.commit()
      return jsonify({"message": "Word deleted successfully"})
    except Exception as e:
      return jsonify({"error": str(e)}), 500

  # Endpoint: GET /words/:id/reviews to get reviews for a word
  @app.route('/words/<int:word_id>/reviews', methods=['GET'])
  @cross_origin()
  def get_reviews(word_id):
    try:
      cursor = app.db.cursor()
      cursor.execute('SELECT * FROM word_reviews WHERE word_id = ?', (word_id,))
      reviews = cursor.fetchall()
      reviews_data = []
      for review in reviews:
        reviews_data.append({
          "id": review["id"],
          "word_id": review["word_id"],
          "correct_count": review["correct_count"],
          "wrong_count": review["wrong_count"]
        })
      return jsonify({"reviews": reviews_data})
    except Exception as e:
      return jsonify({"error": str(e)}), 500

  # Endpoint: POST /words/:id/reviews to add a review for a word
  @app.route('/words/<int:word_id>/reviews', methods=['POST'])
  @cross_origin()
  def add_review(word_id):
    try:
      data = request.get_json()
      correct_count = data.get('correct_count')
      wrong_count = data.get('wrong_count')

      cursor = app.db.cursor()
      cursor.execute('INSERT INTO word_reviews (word_id, correct_count, wrong_count) VALUES (?, ?, ?)', (word_id, correct_count, wrong_count))
      app.db.commit()
      return jsonify({"message": "Review added successfully"})
    except Exception as e:
      return jsonify({"error": str(e)}), 500
    
  # Endpoint: DELETE /words/:id/reviews to delete all reviews for a word
  @app.route('/words/<int:word_id>/reviews', methods=['DELETE'])
  @cross_origin()
  def delete_reviews(word_id):
    try:
      cursor = app.db.cursor()
      cursor.execute('DELETE FROM word_reviews WHERE word_id = ?', (word_id,))
      app.db.commit()
      return jsonify({"message": "Reviews deleted successfully"})
    except Exception as e:
      return jsonify({"error": str(e)}), 500

  # Endpoint: GET /words/:id/groups to get groups for a word
  @app.route('/words/<int:word_id>/groups', methods=['GET'])
  @cross_origin()
  def get_word_groups(word_id):
    try:
      cursor = app.db.cursor()
      cursor.execute('''
        SELECT g.id, g.name
        FROM word_groups wg
        JOIN groups g ON wg.group_id = g.id
        WHERE wg.word_id = ?
      ''', (word_id,))
      groups = cursor.fetchall()
      groups_data = []
      for group in groups:
        groups_data.append({
          "id": group["id"],
          "name": group["name"]
        })
      return jsonify({"groups": groups_data})
    except Exception as e:
      return jsonify({"error": str(e)}), 500
  
  # Endpoint: POST /words/:id/groups to add a group for a word
  @app.route('/words/<int:word_id>/groups', methods=['POST'])
  @cross_origin()
  def add_group(word_id):
    try:
      data = request.get_json()
      group_id = data.get('group_id')

      cursor = app.db.cursor()
      cursor.execute('INSERT INTO word_groups (word_id, group_id) VALUES (?, ?)', (word_id, group_id))
      app.db.commit()
      return jsonify({"message": "Group added successfully"})
    except Exception as e:
      return jsonify({"error": str(e)}), 500

  # Endpoint: DELETE /words/:id/groups/:group_id to delete a group for a word
  @app.route('/words/<int:word_id>/groups/<int:group_id>', methods=['DELETE'])
  @cross_origin()
  def delete_group_for_a_word(word_id, group_id):
    try:
      cursor = app.db.cursor()
      cursor.execute('DELETE FROM word_groups WHERE word_id = ? AND group_id = ?', (word_id, group_id))
      app.db.commit()
      return jsonify({"message": "Group deleted successfully"})
    except Exception as e:
      return jsonify({"error": str(e)}), 500

  # Endpoint: GET /words/:id/quiz to get a quiz for a word
  @app.route('/words/<int:word_id>/quiz', methods=['GET'])
  @cross_origin()
  def get_quiz(word_id):
    try:
      cursor = app.db.cursor()
      cursor.execute('SELECT kanji, romaji, english FROM words WHERE id = ?', (word_id,))
      word = cursor.fetchone()
      return jsonify({"word": word})
    except Exception as e:
      return jsonify({"error": str(e)}), 500

  # Endpoint: POST /words/:id/quiz to submit a quiz for a word
  @app.route('/words/<int:word_id>/quiz', methods=['POST'])
  @cross_origin()
  def submit_quiz(word_id):
    try:
      data = request.get_json()
      correct = data.get('correct')
      
      cursor = app.db.cursor()
      if correct:
        cursor.execute('UPDATE word_reviews SET correct_count = correct_count + 1 WHERE word_id = ?', (word_id,))
      else:
        cursor.execute('UPDATE word_reviews SET wrong_count = wrong_count + 1 WHERE word_id = ?', (word_id,))
      app.db.commit()
      return jsonify({"message": "Quiz submitted successfully"})
    except Exception as e:
      return jsonify({"error": str(e)}), 500
  
  # Endpoint: GET /words/:id/quiz-history to get quiz history for a word
  @app.route('/words/<int:word_id>/quiz-history', methods=['GET'])
  @cross_origin()
  def get_quiz_history(word_id):
    try:
      cursor = app.db.cursor()
      cursor.execute('SELECT correct_count, wrong_count FROM word_reviews WHERE word_id = ?', (word_id,))
      history = cursor.fetchone()
      return jsonify({"history": history})
    except Exception as e:
      return jsonify({"error": str(e)}), 500