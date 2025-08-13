from flask import Flask, render_template, request, jsonify
import math
import traceback

app = Flask(__name__)

# Basic Calculator Functions
def calculate_basic(operation, num1, num2):
    """Perform basic arithmetic operations."""
    try:
        if operation == 'add':
            return num1 + num2
        elif operation == 'subtract':
            return num1 - num2
        elif operation == 'multiply':
            return num1 * num2
        elif operation == 'divide':
            if num2 == 0:
                return "Error: Division by zero"
            return num1 / num2
        elif operation == 'power':
            return num1 ** num2
        elif operation == 'sqrt':
            if num1 < 0:
                return "Error: Cannot calculate square root of negative number"
            return math.sqrt(num1)
        elif operation == 'percentage':
            return (num1 * num2) / 100
        else:
            return "Error: Invalid operation"
    except Exception as e:
        return f"Error: {str(e)}"

# BMI Calculator Functions
def convert_weight_to_kg(weight, unit):
    """Convert weight to kilograms."""
    if unit.lower() == 'lbs':
        return weight * 0.453592
    return weight  

def convert_height_to_meters(height, unit, feet=None, inches=None):
    """Convert height to meters."""
    if unit.lower() == 'cm':
        return height / 100
    elif unit.lower() == 'ft':
        if feet is not None and inches is not None:
            total_inches = (feet * 12) + inches
            return total_inches * 0.0254
        else:
            return height * 0.3048  # If only feet provided
    return height  

def calculate_bmi(weight, height):
    """Calculate BMI using weight in kg and height in meters."""
    bmi = weight / (height ** 2)
    return round(bmi, 2)

def get_bmi_category(bmi):
    """Return BMI category based on BMI value."""
    if bmi < 18.5:
        return "Underweight", "#3498db", "You may want to gain some weight for optimal health."
    elif 18.5 <= bmi < 24.9:
        return "Normal Weight", "#2ecc71", "Great! You're in the healthy weight range."
    elif 25 <= bmi < 29.9:
        return "Overweight", "#f39c12", "Consider a balanced diet and regular exercise."
    else:
        return "Obesity", "#e74c3c", "Please consult with a healthcare professional."

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/calculate_bmi', methods=['POST'])
def calculate_bmi_endpoint():
    try:
        # Ensure we always return JSON
        if not request.is_json:
            return jsonify({'error': 'Request must be JSON'}), 400
            
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        if 'weight' not in data or 'weight_unit' not in data or 'height_unit' not in data:
            return jsonify({'error': 'Missing required fields'}), 400
        
        try:
            weight = float(data['weight'])
            if weight <= 0:
                return jsonify({'error': 'Weight must be a positive number'}), 400
        except (ValueError, TypeError):
            return jsonify({'error': 'Invalid weight value'}), 400
            
        weight_unit = data['weight_unit']
        height_unit = data['height_unit']
        
        # Convert weight to kg
        weight_kg = convert_weight_to_kg(weight, weight_unit)
        
        # Handle height conversion based on unit
        if height_unit.lower() == 'ft':
            try:
                feet = float(data.get('feet', 0))
                inches = float(data.get('inches', 0))
                if feet <= 0 and inches <= 0:
                    return jsonify({'error': 'Please enter valid feet and inches'}), 400
                if feet < 0 or inches < 0 or inches >= 12:
                    return jsonify({'error': 'Invalid feet or inches value'}), 400
                height_m = convert_height_to_meters(0, 'ft', feet, inches)
            except (ValueError, TypeError):
                return jsonify({'error': 'Invalid feet or inches value'}), 400
        else:
            try:
                height_value = float(data['height'])
                if height_value <= 0:
                    return jsonify({'error': 'Height must be a positive number'}), 400
                
                # Adjust validation for different units
                if height_unit.lower() == 'cm':
                    if height_value < 1 or height_value > 300:  # 1cm to 300cm (0.01m to 3m)
                        return jsonify({'error': 'Height must be between 1 and 300 centimeters'}), 400
                elif height_unit.lower() == 'm':
                    if height_value < 0.01 or height_value > 3:  # 0.01m to 3m
                        return jsonify({'error': 'Height must be between 0.01 and 3 meters'}), 400

                height_m = convert_height_to_meters(height_value, height_unit)
            except (ValueError, TypeError):
                return jsonify({'error': 'Invalid height value'}), 400
        
        if height_m <= 0:
            return jsonify({'error': 'Invalid height calculation'}), 400
        
        bmi = calculate_bmi(weight_kg, height_m)
        category, color, advice = get_bmi_category(bmi)
        
        return jsonify({
            'success': True,
            'bmi': bmi,
            'category': category,
            'color': color,
            'advice': advice,
            'weight_kg': round(weight_kg, 2),
            'height_m': round(height_m, 2)
        })
    
    except Exception as e:
        # Log the full error for debugging
        app.logger.error(f"BMI calculation error: {str(e)}")
        app.logger.error(f"Traceback: {traceback.format_exc()}")
        return jsonify({'error': f'Server error: {str(e)}'}), 500

# Error handlers to ensure JSON responses
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
