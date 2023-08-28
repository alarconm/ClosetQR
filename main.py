from flask import Flask, render_template, request, redirect, url_for, jsonify
from replit import db
import qrcode
from io import BytesIO
import base64

app = Flask(__name__)


@app.route('/')
def index():
    hangers = [item for item in db.values()]
    return render_template('index.html', hangers=hangers)

@app.route('/update-clothing/<hanger_id>', methods=['GET'])
def show_update_clothing(hanger_id):
    hanger_key = f'hanger_{hanger_id}'
    
    if hanger_key not in db:
        return "Hanger not found", 404

    hanger = db[hanger_key]
    return render_template('update_clothing.html', hanger=hanger)

@app.route('/get-hangers')
def get_hangers():
    hangers = [item for item in db.values()]
    return jsonify(hangers)

@app.route('/add-hanger', methods=['POST'])
def add_hanger():
    hanger_id = request.form['hanger_id']

    hanger = {
        'hanger_id': hanger_id,
        'clothing_name': '',
        'last_worn': '',
        'notes': '',
        'qr_code_data_url': generate_qr_code_data_url(hanger_id),
    }

    db[f'hanger_{hanger_id}'] = hanger
    return redirect(url_for('index'))

@app.route('/delete-hanger', methods=['POST'])
def delete_hanger():
    hanger_id = request.form['hanger_id']
    hanger_key = f'hanger_{hanger_id}'
    if hanger_key not in db:
      return "Hanger not found", 404
    del db[hanger_key]
    return redirect(url_for('index'))

@app.route('/setup-closet', methods=['POST'])
def setup_closet():
    num_hangers = int(request.form['num_hangers'])

    for i in range(1, num_hangers + 1):
        hanger_id = f'Hanger {i}'
        hanger = {
            'hanger_id': hanger_id,
            'clothing_name': '',
            'last_worn': '',
            'notes': '',
            'qr_code_data_url': generate_qr_code_data_url(hanger_id),
        }
        db[f'hanger_{hanger_id}'] = hanger

    return redirect(url_for('index'))

@app.route('/update-clothing', methods=['POST'])
def update_clothing():
    hanger_id = request.form['hanger_id']
    clothing_name = request.form['clothing_name']
    last_worn = request.form['last_worn']
    notes = request.form['notes']

    hanger_key = f'hanger_{hanger_id}'
    
    if hanger_key not in db:
        return "Hanger not found", 404

    hanger = db[hanger_key]
    hanger['clothing_name'] = clothing_name
    hanger['last_worn'] = last_worn
    hanger['notes'] = notes
    db[hanger_key] = hanger

    return redirect(url_for('index'))

def generate_qr_code_data_url(hanger_id):
    update_url = url_for('show_update_clothing', hanger_id=hanger_id, _external=True)
    print(f"Generated URL: {update_url}")
    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
    qr.add_data(update_url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    buffered = BytesIO()
    img.save(buffered)
    img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
    return f"data:image/png;base64,{img_str}"

@app.route('/clear-closet', methods=['POST'])
def clear_closet():
    hanger_keys_to_delete = [key for key in db.keys() if key.startswith('clothing_tracker_hanger_')]
    for key in hanger_keys_to_delete:
        del db[key]
    print('Hangers after clearing:', [key for key in db.keys() if key.startswith('hanger_')])
    print(keys)
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)