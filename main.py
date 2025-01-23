from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Boolean
import random

'''
Install the required packages first: 
Open the Terminal in PyCharm (bottom left). 

On Windows type:
python -m pip install -r requirements.txt

On MacOS type:
pip3 install -r requirements.txt

This will install the packages from requirements.txt for this project.
'''

# Initialize the Flask app
app = Flask(__name__)

# CREATE DB
class Base(DeclarativeBase):
    """Base class for SQLAlchemy declarative models."""
    pass

# Configure SQLite database URI for the app
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
# Initialize the database using SQLAlchemy
db = SQLAlchemy(model_class=Base)
db.init_app(app)

# CREATE TABLE
class Cafe(db.Model):
    """Model representing a Cafe table in the database."""
    # Define columns and their properties
    id: Mapped[int] = mapped_column(Integer, primary_key=True)  # Primary key column
    name: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)  # Cafe name, unique and mandatory
    map_url: Mapped[str] = mapped_column(String(500), nullable=False)  # URL to the cafe's map location
    img_url: Mapped[str] = mapped_column(String(500), nullable=False)  # URL to an image of the cafe
    location: Mapped[str] = mapped_column(String(250), nullable=False)  # Cafe's location
    seats: Mapped[str] = mapped_column(String(250), nullable=False)  # Number of seats available
    has_toilet: Mapped[bool] = mapped_column(Boolean, nullable=False)  # Boolean indicating if a toilet is available
    has_wifi: Mapped[bool] = mapped_column(Boolean, nullable=False)  # Boolean indicating if Wi-Fi is available
    has_sockets: Mapped[bool] = mapped_column(Boolean, nullable=False)  # Boolean indicating if power sockets are available
    can_take_calls: Mapped[bool] = mapped_column(Boolean, nullable=False)  # Boolean indicating if calls can be taken
    coffee_price: Mapped[str] = mapped_column(String(250), nullable=True)  # Price of coffee

    def to_dict(self):
        """Converts the Cafe object into a dictionary for JSON responses."""
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}

# Create the database and tables
with app.app_context():
    db.create_all()

@app.route("/")
def home():
    """Renders the home page."""
    return render_template("index.html")

@app.route("/random")
def get_random_cafe():
    """
    Returns a random cafe from the database as a JSON response.
    """
    result = db.session.execute(db.select(Cafe))  # Select all cafes
    all_cafes = result.scalars().all()  # Get all cafe objects
    random_cafe = random.choice(all_cafes)  # Pick a random cafe
    return jsonify(cafe=random_cafe.to_dict())  # Return JSON

@app.route("/all")
def get_all_cafes():
    """
    Returns all cafes sorted by name as a JSON response.
    """
    result = db.session.execute(db.select(Cafe).order_by(Cafe.name))  # Select cafes sorted by name
    all_cafes = result.scalars().all()
    return jsonify(cafes=[cafe.to_dict() for cafe in all_cafes])  # Return JSON

@app.route("/search")
def get_cafe_at_location():
    """
    Searches for cafes at a specific location. 
    Returns cafes found or an error message if no cafes are available.
    """
    query_location = request.args.get("loc")  # Get location from query parameters
    result = db.session.execute(db.select(Cafe).where(Cafe.location == query_location))  # Filter by location
    all_cafes = result.scalars().all()
    if all_cafes:
        return jsonify(cafes=[cafe.to_dict() for cafe in all_cafes])
    else:
        # Return 404 error if no cafes found
        return jsonify(error={"Not Found": "Sorry, we don't have a cafe at that location."}), 404

@app.route("/add", methods=["POST"])
def post_new_cafe():
    """
    Adds a new cafe to the database based on form data provided.
    """
    new_cafe = Cafe(
        name=request.form.get("name"),
        map_url=request.form.get("map_url"),
        img_url=request.form.get("img_url"),
        location=request.form.get("loc"),
        has_sockets=bool(request.form.get("sockets")),
        has_toilet=bool(request.form.get("toilet")),
        has_wifi=bool(request.form.get("wifi")),
        can_take_calls=bool(request.form.get("calls")),
        seats=request.form.get("seats"),
        coffee_price=request.form.get("coffee_price"),
    )
    db.session.add(new_cafe)  # Add the new cafe to the database
    db.session.commit()  # Commit the changes
    return jsonify(response={"success": "Successfully added the new cafe."})

@app.route("/update-price/<int:cafe_id>", methods=["PATCH"])
def patch_new_price(cafe_id):
    """
    Updates the price of a specific cafe identified by its ID.
    """
    new_price = request.args.get("new_price")  # Get the new price from query parameters
    cafe = db.get_or_404(Cafe, cafe_id)  # Get the cafe or return 404 if not found
    if cafe:
        cafe.coffee_price = new_price  # Update the coffee price
        db.session.commit()  # Commit the changes
        return jsonify(response={"success": "Successfully updated the price."}), 200
    else:
        return jsonify(error={"Not Found": "Sorry a cafe with that id was not found in the database."}), 404

@app.route("/report-closed/<int:cafe_id>", methods=["DELETE"])
def delete_cafe(cafe_id):
    """
    Deletes a specific cafe identified by its ID. Requires an API key for authorization.
    """
    api_key = request.args.get("api-key")  # Get the API key from query parameters
    if api_key == "TopSecretAPIKey":  # Validate the API key
        cafe = db.get_or_404(Cafe, cafe_id)  # Get the cafe or return 404 if not found
        if cafe:
            db.session.delete(cafe)  # Delete the cafe
            db.session.commit()  # Commit the changes
            return jsonify(response={"success": "Successfully deleted the cafe from the database."}), 200
        else:
            return jsonify(error={"Not Found": "Sorry a cafe with that id was not found in the database."}), 404
    else:
        # Return 403 if API key is invalid
        return jsonify(error={"Forbidden": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 403

if __name__ == '__main__':
    app.run(debug=True)
