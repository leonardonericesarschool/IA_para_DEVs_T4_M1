"""Flask blueprints and route handlers for expenses."""
from flask import Blueprint, jsonify, request

from app.application.dtos.expense_dto import ExpenseCreateDTO
from app.application.use_cases.create_expense_use_case import CreateExpenseUseCase
from app.application.use_cases.list_expenses_use_case import ListExpensesUseCase
from app.infrastructure.repositories.sqlalchemy_expense_repository import (
    SQLAlchemyExpenseRepository,
)

expenses_bp = Blueprint("expenses", __name__, url_prefix="/expenses")

# Initialize repository and use cases
repository = SQLAlchemyExpenseRepository()
create_use_case = CreateExpenseUseCase(repository)
list_use_case = ListExpensesUseCase(repository)


@expenses_bp.route("", methods=["POST"])
def create_expense():
    """
    Create a new expense.
    ---
    tags:
      - Expenses
    summary: Create a new expense
    description: Registers a new corporate expense with validation based on type limits
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              name:
                type: string
                example: "Almoço de trabalho"
              type:
                type: string
                enum: ["alimentação", "transporte", "hospedagem", "outros"]
                example: "alimentação"
              amount:
                type: number
                format: float
                example: 80.00
            required:
              - name
              - type
              - amount
    responses:
      201:
        description: Expense accepted and registered
        content:
          application/json:
            schema:
              type: object
              properties:
                id:
                  type: integer
                name:
                  type: string
                type:
                  type: string
                amount:
                  type: number
                status:
                  type: string
                  enum: ["aceita", "recusada"]
                message:
                  type: string
      400:
        description: Expense rejected due to limit exceeded
        content:
          application/json:
            schema:
              type: object
              properties:
                id:
                  type: integer
                name:
                  type: string
                type:
                  type: string
                amount:
                  type: number
                status:
                  type: string
                  enum: ["aceita", "recusada"]
                message:
                  type: string
      422:
        description: Validation error in request body
      500:
        description: Internal server error
    """
    try:
        # Get JSON from request
        try:
            data = request.get_json(force=False)
        except Exception:
            return (
                jsonify({"error": "Request body must be JSON"}),
                400,
            )

        if data is None:
            return (
                jsonify({"error": "Request body must be JSON"}),
                400,
            )

        # Validate and convert to DTO (Pydantic will validate)
        try:
            dto = ExpenseCreateDTO(**data)
        except ValueError as e:
            return jsonify({"error": str(e)}), 422

        # Execute use case
        response_dto, status_code = create_use_case.execute(dto)

        return jsonify(response_dto.model_dump()), status_code

    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


@expenses_bp.route("", methods=["GET"])
def list_expenses():
    """
    List all expenses.
    ---
    tags:
      - Expenses
    summary: List all expenses
    description: Retrieves a list of all registered corporate expenses
    responses:
      200:
        description: List of expenses
        content:
          application/json:
            schema:
              type: array
              items:
                type: object
                properties:
                  id:
                    type: integer
                  name:
                    type: string
                  type:
                    type: string
                    enum: ["alimentação", "transporte", "hospedagem", "outros"]
                  amount:
                    type: number
                    format: float
                  status:
                    type: string
                    enum: ["aceita", "recusada"]
      500:
        description: Internal server error
    """
    try:
        response_dtos = list_use_case.execute()
        return (
            jsonify([dto.model_dump() for dto in response_dtos]),
            200,
        )
    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


@expenses_bp.route("/health", methods=["GET"])
def health():
    """
    Health check endpoint.
    ---
    tags:
      - Health
    summary: Health check
    description: Verifies if the API is running and healthy
    responses:
      200:
        description: Service is healthy
        content:
          application/json:
            schema:
              type: object
              properties:
                status:
                  type: string
                  example: "healthy"
    """
    return jsonify({"status": "healthy"}), 200
