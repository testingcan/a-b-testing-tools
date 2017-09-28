from flask import Flask, render_template, request
from flask_wtf import Form
from wtforms import FloatField, IntegerField
from wtforms.validators import NumberRange

from math import sqrt
from scipy.stats import chi2_contingency
import numpy as np

app = Flask(__name__)
app.config["SECRET_KEY"] = "ljhl"

@app.route("/")
def index():
	return render_template("index.jinja2")

@app.route("/sample_size_calculator", methods=["GET", "POST"])
def sample_size_calculator():

	class CalculateForm(Form):
		r = FloatField("Number of variants", validators=[NumberRange(min=1)])
		conversion = FloatField("Baseline Conversion-Rate",
				validators=[NumberRange(max=1, min=0.01)])
		delta = FloatField("Desired delta", validators=[NumberRange(max=1,
					min = 0.01)])

	form = CalculateForm()
	result = None

	if form.validate_on_submit():
		sigma = sqrt(form.conversion.data * (1 - form.conversion.data))
		result = ((4 * form.r.data * sigma) / (form.delta.data * form.conversion.data)) ** 2
		result = int(result)
	return render_template("sample_size_calculator.jinja2", result=result, form=form)

@app.route("/a-b-test", methods=["GET", "POST"])
def a_b_test():

	class ABForm(Form):
		original_conversion = IntegerField(
				"Number of conversions original",
				validators=[NumberRange(min=1)]
				)
		original_non_conversion = IntegerField(
				"Number of non-conversions original",
				validators=[NumberRange(min=1)]
				)
		alternative_conversion = IntegerField(
				"Number of conversions alternative",
				validators=[NumberRange(min=1)]
				)
		alternative_non_conversion = IntegerField(
				"Number of non-conversions alternative",
				validators=[NumberRange(min=1)]
				)

	form = ABForm()
	chi2 = None
	p = None
	dof = None
	expected = None
	power = None

	if form.validate_on_submit():
		obs = np.array([
				[form.original_conversion.data,
				form.original_non_conversion.data],
				[form.alternative_conversion.data,
				form.alternative_non_conversion.data]
				])
		chi2, p, dof, expected = chi2_contingency(obs)
		chi2 = round(chi2, 4)
		power = round(1 - p, 2)
		p = round(p, 2)
	return render_template("a-b-test.jinja2",
			chi2=chi2,
			p=p,
			dof=dof,
			expected=expected,
			power=power,
			form=form
			)

if __name__ == "__main__":
	app.debug = True
	app.run()


