"""
Categories routes - CRUD endpoints for financial categories
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from patriot.backend.database import db
from patriot.backend.models.category import Category
from shared.utils.household_helpers import get_current_household_id, get_current_user_id

categories_bp = Blueprint("categories", __name__)


@categories_bp.route("/", methods=["GET"])
@jwt_required()
def get_categories():
    """Get all categories for the current household"""
    household_id = get_current_household_id()
    if not household_id:
        return jsonify({"error": "No household found for user"}), 404

    # Optional filters
    category_type = request.args.get("type")  # expense, income, savings, debt
    parent_id = request.args.get("parent_id")
    include_inactive = request.args.get("include_inactive", "false").lower() == "true"

    query = Category.query.filter_by(household_id=household_id)

    if category_type:
        query = query.filter_by(category_type=category_type)
    
    if parent_id:
        if parent_id == "null":
            query = query.filter(Category.parent_id.is_(None))
        else:
            query = query.filter_by(parent_id=int(parent_id))
    
    if not include_inactive:
        query = query.filter_by(is_active=True)

    categories = query.order_by(Category.name).all()

    return jsonify({
        "categories": [cat.to_dict(include_subcategories=True) for cat in categories],
        "count": len(categories)
    }), 200


@categories_bp.route("/<int:category_id>", methods=["GET"])
@jwt_required()
def get_category(category_id):
    """Get a specific category"""
    household_id = get_current_household_id()
    if not household_id:
        return jsonify({"error": "No household found for user"}), 404

    category = Category.query.filter_by(
        id=category_id, 
        household_id=household_id
    ).first()

    if not category:
        return jsonify({"error": "Category not found"}), 404

    return jsonify(category.to_dict(include_subcategories=True)), 200


@categories_bp.route("/", methods=["POST"])
@jwt_required()
def create_category():
    """Create a new category"""
    household_id = get_current_household_id()
    if not household_id:
        return jsonify({"error": "No household found for user"}), 404

    data = request.get_json()

    # Validate required fields
    if not data.get("name"):
        return jsonify({"error": "Category name is required"}), 400
    
    if not data.get("category_type"):
        return jsonify({"error": "Category type is required"}), 400

    # Validate category_type
    valid_types = ["expense", "income", "savings", "debt"]
    if data["category_type"] not in valid_types:
        return jsonify({"error": f"Invalid category type. Must be one of: {', '.join(valid_types)}"}), 400

    # Validate parent_id if provided
    if data.get("parent_id"):
        parent = Category.query.filter_by(
            id=data["parent_id"],
            household_id=household_id
        ).first()
        if not parent:
            return jsonify({"error": "Parent category not found"}), 404

    try:
        category = Category(
            household_id=household_id,
            name=data["name"],
            description=data.get("description"),
            category_type=data["category_type"],
            parent_id=data.get("parent_id"),
            icon=data.get("icon"),
            color=data.get("color"),
            budget_amount=data.get("budget_amount"),
            is_active=data.get("is_active", True)
        )

        db.session.add(category)
        db.session.commit()

        return jsonify({
            "message": "Category created successfully",
            "category": category.to_dict(include_subcategories=True)
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to create category: {str(e)}"}), 500


@categories_bp.route("/<int:category_id>", methods=["PUT"])
@jwt_required()
def update_category(category_id):
    """Update a category"""
    household_id = get_current_household_id()
    if not household_id:
        return jsonify({"error": "No household found for user"}), 404

    category = Category.query.filter_by(
        id=category_id,
        household_id=household_id
    ).first()

    if not category:
        return jsonify({"error": "Category not found"}), 404

    data = request.get_json()

    try:
        # Update fields if provided
        if "name" in data:
            category.name = data["name"]
        if "description" in data:
            category.description = data["description"]
        if "category_type" in data:
            valid_types = ["expense", "income", "savings", "debt"]
            if data["category_type"] not in valid_types:
                return jsonify({"error": f"Invalid category type. Must be one of: {', '.join(valid_types)}"}), 400
            category.category_type = data["category_type"]
        if "parent_id" in data:
            if data["parent_id"]:
                # Validate parent exists and prevent circular reference
                if data["parent_id"] == category_id:
                    return jsonify({"error": "Category cannot be its own parent"}), 400
                parent = Category.query.filter_by(
                    id=data["parent_id"],
                    household_id=household_id
                ).first()
                if not parent:
                    return jsonify({"error": "Parent category not found"}), 404
            category.parent_id = data["parent_id"]
        if "icon" in data:
            category.icon = data["icon"]
        if "color" in data:
            category.color = data["color"]
        if "budget_amount" in data:
            category.budget_amount = data["budget_amount"]
        if "is_active" in data:
            category.is_active = data["is_active"]

        db.session.commit()

        return jsonify({
            "message": "Category updated successfully",
            "category": category.to_dict(include_subcategories=True)
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to update category: {str(e)}"}), 500


@categories_bp.route("/<int:category_id>", methods=["DELETE"])
@jwt_required()
def delete_category(category_id):
    """Delete (soft delete) a category"""
    household_id = get_current_household_id()
    if not household_id:
        return jsonify({"error": "No household found for user"}), 404

    category = Category.query.filter_by(
        id=category_id,
        household_id=household_id
    ).first()

    if not category:
        return jsonify({"error": "Category not found"}), 404

    # Check if category has subcategories
    subcategories = Category.query.filter_by(
        parent_id=category_id,
        is_active=True
    ).count()
    
    if subcategories > 0:
        return jsonify({
            "error": "Cannot delete category with active subcategories. Delete or reassign subcategories first."
        }), 400

    try:
        # Soft delete
        category.is_active = False
        db.session.commit()

        return jsonify({"message": "Category deleted successfully"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to delete category: {str(e)}"}), 500


@categories_bp.route("/defaults", methods=["GET"])
@jwt_required()
def get_default_categories():
    """Get default category structures"""
    return jsonify({
        "defaults": Category.get_default_categories()
    }), 200


@categories_bp.route("/defaults/create", methods=["POST"])
@jwt_required()
def create_default_categories():
    """Create default categories for the household"""
    household_id = get_current_household_id()
    if not household_id:
        return jsonify({"error": "No household found for user"}), 404

    try:
        defaults = Category.get_default_categories()
        created_categories = []

        for default_cat in defaults:
            # Create parent category
            parent = Category(
                household_id=household_id,
                name=default_cat["name"],
                category_type=default_cat["type"],
                icon=default_cat.get("icon")
            )
            db.session.add(parent)
            db.session.flush()  # Get the ID
            created_categories.append(parent)

            # Create subcategories
            for subcat_name in default_cat.get("subcategories", []):
                subcat = Category(
                    household_id=household_id,
                    name=subcat_name,
                    category_type=default_cat["type"],
                    parent_id=parent.id
                )
                db.session.add(subcat)
                created_categories.append(subcat)

        db.session.commit()

        return jsonify({
            "message": f"Created {len(created_categories)} default categories",
            "categories": [cat.to_dict() for cat in created_categories]
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to create default categories: {str(e)}"}), 500
