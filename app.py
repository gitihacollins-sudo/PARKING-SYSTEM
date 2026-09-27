import os
from pathlib import Path

from flask import Flask, flash, redirect, render_template, request, url_for

from parking.database import initialize_database
from parking.service import ParkingError, check_out_vehicle, park_vehicle, parking_overview


BASE_DIR = Path(__file__).resolve().parent


def create_app(test_config=None):
	app = Flask(__name__, template_folder="parking/templates", static_folder="parking/static")
	app.config.from_mapping(
		SECRET_KEY=os.environ.get("PARKING_SECRET_KEY", "local-development-key-change-me"),
		DATABASE=os.environ.get("PARKING_DATABASE", str(BASE_DIR / "instance" / "parking.db")),
		SLOT_COUNT=int(os.environ.get("PARKING_SLOT_COUNT", "24")),
	)
	if test_config:
		app.config.update(test_config)

	initialize_database(app.config["DATABASE"], app.config["SLOT_COUNT"])

	@app.get("/")
	def dashboard():
		overview = parking_overview(app.config["DATABASE"])
		return render_template("dashboard.html", **overview)

	@app.post("/entry")
	def entry():
		try:
			ticket = park_vehicle(app.config["DATABASE"], request.form.get("registration", ""))
			flash(
				f"{ticket['registration']} parked in slot {ticket['slot_id']} at "
				f"{ticket['entry_time']}. Available spaces: {ticket['available_slots']}.",
				"success",
			)
		except ParkingError as error:
			flash(str(error), "error")
		return redirect(url_for("dashboard"))

	@app.post("/exit")
	def exit_vehicle():
		try:
			receipt = check_out_vehicle(
				app.config["DATABASE"], request.form.get("registration", "")
			)
			flash(
				f"{receipt['registration']} checked out. Duration: {receipt['duration']}. "
				f"Amount due: KSh {receipt['amount_due']}. "
				f"Available spaces: {receipt['available_slots']}.",
				"success",
			)
		except ParkingError as error:
			flash(str(error), "error")
		return redirect(url_for("dashboard"))

	return app


app = create_app()


if __name__ == "__main__":
	app.run(debug=os.environ.get("FLASK_DEBUG") == "1")
