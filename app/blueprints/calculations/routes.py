"""
Calculations routes for the mechanic shop application.
"""
from flask import request, jsonify
from app.extensions import limiter
from . import calculations_bp

@calculations_bp.route("/add", methods=["POST"])
@limiter.limit("100 per minute")
def add_numbers():
    """
    Add numbers together.
    ---
    tags:
      - Calculations
    summary: Add numbers
    description: Add a list of numbers.
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              numbers:
                type: array
                items:
                  type: number
                description: List of numbers to add
                example: [1, 2, 3.5]
    responses:
      200:
        description: Sum returned.
        content:
          application/json:
            schema:
              type: object
              properties:
                result:
                  type: number
                operation:
                  type: string
                operands:
                  type: array
                  items:
                    type: number
      400:
        description: Validation error
      500:
        description: Internal server error
    """
    try:
        data = request.get_json()
        if not data or "numbers" not in data:
            return jsonify({"error": "Missing numbers field"}), 400
        numbers = data["numbers"]
        if not isinstance(numbers, list):
            return jsonify({"error": "Numbers must be a list"}), 400
        if len(numbers) < 2:
            return jsonify({"error": "At least 2 numbers required"}), 400
        for num in numbers:
            if not isinstance(num, (int, float)):
                return jsonify({"error": "All items must be numbers"}), 400
        result = sum(numbers)
        return jsonify({"result": result, "operation": "addition", "operands": numbers}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@calculations_bp.route("/subtract", methods=["POST"])
@limiter.limit("100 per minute")
def subtract_numbers():
    """
    Subtract a list of numbers (first - second - third - ...)
    ---
    tags:
      - Calculations
    summary: Subtract numbers
    description: Subtract all subsequent numbers from the first.
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              numbers:
                type: array
                items:
                  type: number
                description: List of numbers to subtract
                example: [10, 3, 2]
    responses:
      200:
        description: Difference returned.
        content:
          application/json:
            schema:
              type: object
              properties:
                result:
                  type: number
                operation:
                  type: string
                operands:
                  type: array
                  items:
                    type: number
      400:
        description: Validation error
      500:
        description: Internal server error
    """
    try:
        data = request.get_json()
        if not data or "numbers" not in data:
            return jsonify({"error": "Missing numbers field"}), 400
        numbers = data["numbers"]
        if not isinstance(numbers, list):
            return jsonify({"error": "Numbers must be a list"}), 400
        if len(numbers) < 2:
            return jsonify({"error": "At least 2 numbers required"}), 400
        for num in numbers:
            if not isinstance(num, (int, float)):
                return jsonify({"error": "All items must be numbers"}), 400
        result = numbers[0]
        for num in numbers[1:]:
            result -= num
        return jsonify({"result": result, "operation": "subtraction", "operands": numbers}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@calculations_bp.route("/multiply", methods=["POST"])
@limiter.limit("100 per minute")
def multiply_numbers():
    """
    Multiply a list of numbers.
    ---
    tags:
      - Calculations
    summary: Multiply numbers
    description: Multiply a list of numbers together.
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              numbers:
                type: array
                items:
                  type: number
                description: List of numbers to multiply
                example: [2, 3, 4]
    responses:
      200:
        description: Product returned.
        content:
          application/json:
            schema:
              type: object
              properties:
                result:
                  type: number
                operation:
                  type: string
                operands:
                  type: array
                  items:
                    type: number
      400:
        description: Validation error
      500:
        description: Internal server error
    """
    try:
        data = request.get_json()
        if not data or "numbers" not in data:
            return jsonify({"error": "Missing numbers field"}), 400
        numbers = data["numbers"]
        if not isinstance(numbers, list):
            return jsonify({"error": "Numbers must be a list"}), 400
        if len(numbers) < 2:
            return jsonify({"error": "At least 2 numbers required"}), 400
        for num in numbers:
            if not isinstance(num, (int, float)):
                return jsonify({"error": "All items must be numbers"}), 400
        result = 1
        for num in numbers:
            result *= num
        return jsonify({"result": result, "operation": "multiplication", "operands": numbers}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@calculations_bp.route("/divide", methods=["POST"])
@limiter.limit("100 per minute")
def divide_numbers():
    """
    Divide a list of numbers (first / second / third / ...)
    ---
    tags:
      - Calculations
    summary: Divide numbers
    description: Divide the first number by each of the subsequent numbers in order.
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              numbers:
                type: array
                items:
                  type: number
                description: List of numbers to divide
                example: [100, 2, 5]
    responses:
      200:
        description: Quotient returned.
        content:
          application/json:
            schema:
              type: object
              properties:
                result:
                  type: number
                operation:
                  type: string
                operands:
                  type: array
                  items:
                    type: number
      400:
        description: Validation error or division by zero
      500:
        description: Internal server error
    """
    try:
        data = request.get_json()
        if not data or "numbers" not in data:
            return jsonify({"error": "Missing numbers field"}), 400
        numbers = data["numbers"]
        if not isinstance(numbers, list):
            return jsonify({"error": "Numbers must be a list"}), 400
        if len(numbers) < 2:
            return jsonify({"error": "At least 2 numbers required"}), 400
        for num in numbers:
            if not isinstance(num, (int, float)):
                return jsonify({"error": "All items must be numbers"}), 400
        for num in numbers[1:]:
            if num == 0:
                return jsonify({"error": "Division by zero"}), 400
        result = numbers[0]
        for num in numbers[1:]:
            result /= num
        return jsonify({"result": result, "operation": "division", "operands": numbers}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@calculations_bp.route("/health", methods=["GET"])
def health_check():
    """
    Health check for calculations service.
    ---
    tags:
      - Calculations
    summary: Health check
    description: Returns the status of the calculations service and its available endpoints.
    responses:
      200:
        description: Health status and endpoints.
        content:
          application/json:
            schema:
              type: object
              properties:
                status:
                  type: string
                service:
                  type: string
                endpoints:
                  type: array
                  items:
                    type: string
                available_operations:
                  type: array
                  items:
                    type: string
    """
    return (
        jsonify(
            {
                "status": "healthy",
                "service": "calculations",
                "endpoints": [
                    "/add",
                    "/subtract",
                    "/multiply",
                    "/divide",
                ],
                "available_operations": ["add", "subtract", "multiply", "divide"],
            }
        ),
        200,
    )