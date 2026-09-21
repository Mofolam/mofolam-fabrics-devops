from flask import Flask, render_template, request, redirect, url_for
from app.config import Config
from app.models import db, Fabric

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)


@app.route("/")
def home():
    return """
    <h1>Mofolam Fabrics</h1>
    <h2>Inventory Management System</h2>
    <p>Welcome to the Mofolam Fabrics DevOps Project.</p>
    <a href="/inventory">View Inventory</a>
    """


@app.route("/inventory")
def inventory():

    fabrics = Fabric.query.all()

    inventory_html = """
    <h1>Mofolam Fabrics Inventory</h1>

    <table border="1" cellpadding="10">
        <tr>
            <th>Fabric</th>
            <th>Category</th>
            <th>Quantity</th>
            <th>Price</th>
        </tr>
    """

    for fabric in fabrics:
        inventory_html += f"""
        <tr>
            <td>{fabric.name}</td>
            <td>{fabric.category}</td>
            <td>{fabric.quantity}</td>
            <td>₦{fabric.price:,}</td>
        </tr>
        """

    inventory_html += """
    </table>

    <br>

    <a href="/add-fabric">Add New Fabric</a>

    <br><br>

    <a href="/">Back Home</a>
    """

    return inventory_html


@app.route("/add-fabric", methods=["GET", "POST"])
def add_fabric():

    if request.method == "POST":

        name = request.form["name"]
        category = request.form["category"]
        quantity = int(request.form["quantity"])
        price = int(request.form["price"])

        new_fabric = Fabric(
            name=name,
            category=category,
            quantity=quantity,
            price=price
        )

        db.session.add(new_fabric)
        db.session.commit()

        return redirect(url_for("inventory"))

    return render_template("add_fabric.html")

@app.route("/health")
def health():
    return {"status": "healthy"}, 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)