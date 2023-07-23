from flask import Flask, render_template, request
from flask_cors import CORS, cross_origin
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq
import pymongo
import argparse

app = Flask(__name__)

@app.route("/", methods=['GET'])
@cross_origin()
def homepage():
    return render_template("index.html")

@app.route("/review", methods=['POST'])
@cross_origin()
def index():
    if request.method == 'POST':
        try:
            searchString = request.form['content'].replace(" ", "")
            flipkart_url = "https://www.flipkart.com/search?q=" + searchString
            
            # Using requests session to avoid redundant HTTP requests
            flipkartPage = requests.get(flipkart_url).text

            flipkart_html = bs(flipkartPage, "html.parser")
            bigboxes = flipkart_html.findAll("div", {"class": "_1AtVbE col-12-12"})
            del bigboxes[0:3]
            box = bigboxes[0]
            productLink = "https://www.flipkart.com" + box.div.div.div.a['href']

            with requests.Session() as session:
                prodRes = session.get(productLink)
                prodRes.encoding = 'utf-8'

            prod_html = bs(prodRes.text, "html.parser")
            commentboxes = prod_html.find_all('div', {'class': "_16PBlm"})

            reviews = []
            for commentbox in commentboxes:
                try:
                    name = commentbox.div.div.find_all('p', {'class': '_2sc7ZR _2V5EHH'})[0].text
                except Exception as e:
                    name = 'No Name'

                try:
                    rating = commentbox.div.div.div.div.text
                except Exception as e:
                    rating = 'No Rating'

                try:
                    commentHead = commentbox.div.div.div.p.text
                except Exception as e:
                    commentHead = 'No Comment Heading'

                try:
                    comtag = commentbox.div.div.find_all('div', {'class': ''})
                    custComment = comtag[0].div.text
                except Exception as e:
                    custComment = 'No Comment'

                mydict = {"Product": searchString, "Name": name, "Rating": rating, "CommentHead": commentHead,
                          "Comment": custComment}
                reviews.append(mydict)

            # # Insert data into MongoDB using bulk_write for efficient insertion
            # client = pymongo.MongoClient("mongodb+srv://vaibhav:Pwskills@cluster0.akhldgc.mongodb.net/?retryWrites=true&w=majority")
            # db = client['review_scrap']
            # review_col = db['review_scrap_data']

            # if reviews:
            #     review_col.bulk_write([pymongo.InsertOne(review) for review in reviews])

            return render_template('result.html', reviews=reviews)
        except Exception as e:
            print(f"An error occurred: {e}")
            return 'Something went wrong.'
    else:
        return render_template('index.html')

if __name__ == "__main__":
    # Initialize the argument parser
    parser = argparse.ArgumentParser(description="Flask app arguments")
    parser.add_argument("--host", default="127.0.0.1", help="Host IP address")
    parser.add_argument("--port", type=int, default=5000, help="Port number")
    args = parser.parse_args()

    # Run the Flask app with the provided arguments
    app.run(host=args.host, port=args.port, debug=True)
