from flask import Flask, render_template, request, url_for
import pandas as pd
import matplotlib.pyplot as plt 
import seaborn as sns 
import plotly.express as px
import plotly.io as pio
import warnings
 
app = Flask(__name__)
main_data = pd.read_csv("cleaned_glassdoor_data.csv")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/index.html/")
def jobindex():
    return render_template("index.html")

@app.route("/about/")
def about():
    return render_template("about.html")

@app.route("/contact/")
def contact():
    return render_template("contact.html")

@app.route("/searchjob/")
def jobsearch():
    return render_template("searchjobform.html")

# @app.route("/joblist/")
# def joblist():
#     return render_template("job-list.html")

@app.route("/job-detail/")
def jobdetail():
    return render_template("job-detail.html")

@app.route("/category/")
def jobcategory():
    return render_template("category.html")
@app.route("/analysis/")
def analysis():
    return render_template("analysis.html")
@app.route("/company_location_map/")
def map():
    return render_template("company_locations_map.html")
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.route("/aftersubmit/", methods=['GET', 'POST'])
def aftersubmit():
    if request.method == "POST":
        job_profile = request.form.get('jobprofile')
        location = request.form.get('location')  
        rating = request.form.get('rating') 
        sector = request.form.get('sector')
        company_name = request.form.get('companyname')
        data = main_data.copy()
        if rating:
            if rating.isnumeric():
                rating = eval(rating)
                if not rating<=5:
                    error = "Please Enter rating between 1 to 5"
                    return render_template("searchjobform.html", err=error)
            else:
                error = "Please enter valid rating"
                return render_template("searchjobform.html", err=error)
        if job_profile:
            data = data[data['job_title'].apply(lambda x: True if job_profile.lower() in x.lower() else False)]
        if location:
            data = data[data['location'].str.lower() == str(location).lower()]
        if rating:
            data = data[data['company_rating']>=rating]
        if sector:
            data = data[data['sector'].apply(lambda x: True if str(sector) in str(x).lower() else False)]
        if company_name:
            data = data[data['company'].str.lower().str.strip() == company_name.strip().lower()]               
        return render_template("aftersubmit.html",data = data.to_dict(orient='records'), job_profile=job_profile, location=location, rating=rating, sector=sector, company_name=company_name)

    else:
        return render_template("searchjobform.html")

@app.route("/showplot/", methods=['GET', 'POST'])
def showplot():
    if request.method == "GET":
        return render_template("index.html")
    else:
        category = request.form.get("category") 
        column_name = request.form.get("column")
        if category == "bar":
            count = main_data[column_name].value_counts().iloc[:10]
            index = count.index 
            values = count.values 
            file_name = f"static/img/{column_name}_{category}.jpg"
            plt.figure(figsize=(10, 5), dpi=100)
            sns.barplot(index, values)
            plt.xticks(rotation=90)
            plt.title(f"TOP 10 {column_name.upper()}", color='green')
            plt.savefig(file_name, bbox_inches='tight')
            # plt.show()
        elif category == "piechart":
            plt.rcParams['font.size'] = 6
            count = main_data[column_name].value_counts().iloc[:10]
            index = count.index 
            values = count.values 
            file_name = f"static/img/{column_name}_{category}.jpg"
            plt.figure(figsize=(10, 5), dpi=100)
            plt.pie(values, labels=index, wedgeprops={'ls':'-', 'edgecolor': 'black', 'lw': 2}, autopct='%1.1f%%')
            plt.title(f"TOP 10 {column_name.upper()}", color='green')
            plt.savefig(file_name, bbox_inches='tight')
            # plt.show()
        elif category == "histogram":
            count = main_data[column_name].value_counts().iloc[:10]
            file_name = f"static/img/{column_name}_{category}.jpg"
            plt.figure(figsize=(10, 5), dpi=100)
            sns.histplot(main_data[column_name][:10], palette="red")
            plt.xticks(rotation=90)
            plt.title(f"DISTRIBUTION OF {column_name.upper()}", color='green')
            plt.savefig(file_name, bbox_inches='tight')
            # plt.show()
        
        return render_template("category.html", img="../"+file_name)


@app.route("/plotly/", methods=['GET', 'POST'])
def plotly():
    if request.method == "GET":
        return render_template("plotly.html")
    else:
        column_name = request.form.get("column")
        category = request.form.get("category")
        if category == "bar":
            html_file_path= f"templates/{column_name}_{category}.html"
            fig = px.bar(main_data[column_name].value_counts(), title=f"Count of {column_name}", color=main_data[column_name].value_counts().index)
            pio.write_html(fig, file=html_file_path, auto_open=False) 
        
        elif category == "pie":
            html_file_path= f"templates/{column_name}_{category}.html"
            fig = px.pie(main_data, values=main_data[column_name].value_counts().values[:10], names=main_data[column_name].value_counts().index[:10], title= f"Pie chart of {column_name}")
            pio.write_html(fig, file=html_file_path, auto_open=False) 
        
        elif category == "histogram":
            html_file_path= f"templates/{column_name}_{category}.html"
            fig = px.histogram(main_data, x= main_data[column_name], title=f"Histogram of {column_name}")
            pio.write_html(fig, file=html_file_path, auto_open=False) 
        return render_template(f"{column_name}_{category}.html", html="../"+html_file_path)
        

if __name__ == "__main__":
    app.run(host='localhost', port=3000, debug=True)