from flask import Flask, request, jsonify, send_from_directory, render_template
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from transformers import VisionEncoderDecoderModel, TrOCRProcessor
from transformers import BertTokenizer, BertForSequenceClassification
from PIL import Image
import io
import jwt
import datetime
from functools import wraps
from bson.objectid import ObjectId
from pymongo import MongoClient
import os

app = Flask(__name__)
CORS(app)

# MongoDB setup
client = MongoClient("mongodb://localhost:27017")  # Change if using Atlas
db = client["userdb"]
users = db["users"]

app.config['SECRET_KEY'] = 'Thisisasecretkey'


# ==== JWT Token Decorator ====
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')

        if not token:
            return jsonify({'message': 'Token is missing'}), 401

        try:
            token = token.split(' ')[1]
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = users.find_one({'_id': ObjectId(data['user_id'])})
        except Exception as e:
            return jsonify({'message': 'Token is invalid', 'error': str(e)}), 401

        return f(current_user, *args, **kwargs)
    return decorated


# ==== Routes ====

@app.route('/')
def serve_index():
    return render_template('home.html')

@app.route('/<path:path>')
def serve_file(path):
    if path.endswith('.html'):
        return render_template(path)
    return send_from_directory('static', path)


@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()

    if not all(k in data for k in ('name', 'email', 'password')):
        return jsonify({'message': 'Missing required fields'}), 400

    if users.find_one({'email': data['email']}):
        return jsonify({'message': 'Email already registered'}), 400

    hashed_password = generate_password_hash(data['password'])

    new_user = {
        'name': data['name'],
        'email': data['email'],
        'password': hashed_password,
        'created_at': datetime.datetime.utcnow()
    }

    result = users.insert_one(new_user)
    user_id = str(result.inserted_id)

    token = jwt.encode({
        'user_id': user_id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1)
    }, app.config['SECRET_KEY'])

    return jsonify({
        'message': 'Registration successful',
        'token': token,
        'user': {
            'id': user_id,
            'name': data['name'],
            'email': data['email']
        }
    }), 201


@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()

    if not all(k in data for k in ('email', 'password')):
        return jsonify({'message': 'Missing required fields'}), 400

    user = users.find_one({'email': data['email']})
    if not user or not check_password_hash(user['password'], data['password']):
        return jsonify({'message': 'Invalid credentials'}), 401

    token = jwt.encode({
        'user_id': str(user['_id']),
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1)
    }, app.config['SECRET_KEY'])

    return jsonify({
        'message': 'Login successful',
        'token': token,
        'user': {
            'id': str(user['_id']),
            'name': user['name'],
            'email': user['email']
        }
    }), 200


@app.route('/api/user', methods=['GET'])
@token_required
def get_user(current_user):
    return jsonify({
        'user': {
            'id': str(current_user['_id']),
            'name': current_user['name'],
            'email': current_user['email']
        }
    }), 200


@app.route('/api/logout', methods=['POST'])
@token_required
def logout(current_user):
    return jsonify({'message': 'Logout successful'}), 200


@app.route('/api/reset-password-request', methods=['POST'])
def reset_password_request():
    data = request.get_json()
    user = users.find_one({'email': data['email']})
    
    if user:
        reset_token = jwt.encode({
            'user_id': str(user['_id']),
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        }, app.config['SECRET_KEY'])

        return jsonify({
            'message': 'Password reset instructions sent',
            'reset_token': reset_token
        }), 200

    return jsonify({'message': 'Email not found'}), 404


@app.route('/api/reset-password', methods=['POST'])
def reset_password():
    data = request.get_json()
    try:
        token_data = jwt.decode(data['token'], app.config['SECRET_KEY'], algorithms=["HS256"])
        user_id = token_data['user_id']
        hashed_password = generate_password_hash(data['new_password'])

        result = users.update_one(
            {'_id': ObjectId(user_id)},
            {'$set': {'password': hashed_password}}
        )

        if result.modified_count == 1:
            return jsonify({'message': 'Password reset successful'}), 200

    except Exception as e:
        return jsonify({'message': 'Invalid or expired reset token', 'error': str(e)}), 401

    return jsonify({'message': 'Password reset failed'}), 400


# ==== OCR & BERT Section ====

processor = TrOCRProcessor.from_pretrained("microsoft/trocr-base-handwritten")
model = VisionEncoderDecoderModel.from_pretrained("microsoft/trocr-base-handwritten")
tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")
bert_model = BertForSequenceClassification.from_pretrained("bert-base-uncased", num_labels=1)

def extract_text(image_bytes):
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    pixel_values = processor(image, return_tensors="pt").pixel_values
    generated_ids = model.generate(pixel_values)
    extracted_text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
    return extracted_text

def grade_answer(extracted_text, keywords, weights):
    tokens = tokenizer(extracted_text, return_tensors="pt", padding=True, truncation=True)
    score = sum(weight for keyword, weight in zip(keywords, weights) if keyword.lower() in extracted_text.lower())
    return score


@app.route('/upload', methods=['GET'])
def upload_form():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']
    image_bytes = file.read()
    extracted_text = extract_text(image_bytes)

    keywords = request.form.getlist('keywords')
    weights = list(map(float, request.form.getlist('weights')))

    score = grade_answer(extracted_text, keywords, weights)

    return jsonify({'extracted_text': extracted_text, 'score': score})


# ==== Run App ====
if __name__ == '__main__':
    app.run(debug=True)